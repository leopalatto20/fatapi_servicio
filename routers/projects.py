import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from sqlalchemy.sql.expression import Insert
from sqlmodel.sql.expression import Select

from ..common.guards import admin_guard
from ..db import SessionDep
from ..models import EnrolmentToken, Project, ProjectCreate, ProjectPublic, User

router = APIRouter(tags=["projects"], prefix="/projects")


@router.post("", response_model=ProjectPublic)
async def create_project(
    project: ProjectCreate, session: SessionDep, _: User = Depends(admin_guard)
):
    session.add(project)
    session.commit()
    return project


@router.get("", response_model=list[ProjectPublic])
async def get_projects(session: SessionDep):
    return session.exec(Select(Project)).all()


@router.post("{project_id}/tokens")
async def create_project_tokens(project_id: int, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tokens = []
    length = 8
    for _ in range(project.slots):
        token = "".join(random.choices(string.ascii_letters + string.digits, k=length))

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        session.exec(
            Insert(EnrolmentToken).values(
                token=token, expires_at=expires_at, project_id=project_id
            )
        )

        tokens.append(token)

    return {"tokens": tokens}
