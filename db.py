import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .models import *

load_dotenv()

mysql_url = os.getenv("DB_URL")
if not mysql_url:
    raise ValueError("DB_URL not set")

engine = create_engine(mysql_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
