from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from sqlmodel import select

from ..db import SessionDep
from ..models import User, UserCreate, UserPublic

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
