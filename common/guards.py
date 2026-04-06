from fastapi import Depends, Header, HTTPException
from firebase_admin.auth import InvalidIdTokenError, verify_id_token
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, UserRole


def get_current_user(
    authorization: str | None = Header(None), session: Session = Depends(get_session)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    token = authorization.replace("Bearer ", "")
    try:
        decoded = verify_id_token(token)
        uid = decoded.get("uid")
    except InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.provider_id == uid)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def admin_guard(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def user_guard(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.user:
        raise HTTPException(status_code=403, detail="User access required")
    return current_user
