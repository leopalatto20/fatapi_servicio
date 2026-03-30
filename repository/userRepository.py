from sqlmodel import select

from db import SessionDep
from models import User


def get_by_id(id: str, session: SessionDep):
    return session.exec(select(User).where(User.id == id)).first()


def get_by_email(email: str, session: SessionDep):
    return session.exec(select(User).where(User.email == email)).first()


def get_by_provider_id(provider_id: str, session: SessionDep):
    return session.exec(select(User).where(User.provider_id == provider_id)).first()
