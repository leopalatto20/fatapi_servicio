from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import auth
from sqlmodel import select

from ..common.guards import get_current_user
from ..db import SessionDep
from ..models import User, UserCreate, UserPublic, VerificationToken

router = APIRouter(tags=["users"], prefix="/users")


@router.post("/register", response_model=UserPublic)
def register(user: UserCreate, session: SessionDep):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = session.exec(select(User).where(User.id == user.id)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="ID already registered")

    try:
        firebase_user = auth.create_user(
            email=user.email,
            password=user.password,
        )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        id=user.id,
        provider_id=firebase_user.uid,
        email=user.email,
        name=user.name,
        degree=user.degree,
        semester=user.semester,
        role=user.role,
        verified=False,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.put("/verify")
def verify_user(
    session: SessionDep, token: str, user: User = Depends(get_current_user)
):
    db_token = session.exec(
        select(VerificationToken).where(VerificationToken.token == token)
    ).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")

    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")

    existing_user = session.exec(select(User).where(User.token == token)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Token already used")

    user.token = db_token.token
    user.verified = True
    session.commit()
    session.refresh(user)
    return user
