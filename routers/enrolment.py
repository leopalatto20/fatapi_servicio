from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import insert, select

from ..common.guards import user_guard
from ..db import SessionDep
from ..models import EnrolmentToken, Project, User

router = APIRouter(prefix="/enrolment", tags=["enrolment"])


@router.post("/{token}")
async def create_enrolment(
    token: str, session: SessionDep, user: User = Depends(user_guard)
):
    db_token = session.exec(
        select(EnrolmentToken).where(EnrolmentToken.token == token)
    ).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")

    project = session.exec(
        select(Project).where(Project.id == db_token.id_project)
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Token not related to a project")

    enrolment = session.exec(
        insert(EnrolmentToken).values(
            token=token, id_project=project.id, id_user=user.id
        )
    )

    return enrolment
