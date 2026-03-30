from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..db import SessionDep
from ..models import Partner, PartnerCreate, PartnerPublic

router = APIRouter(tags=["partners"], prefix="/partners")


@router.get("", response_model=list[PartnerPublic])
def get_partners(session: SessionDep):
    partners = session.exec(select(Partner)).all()
    return partners


@router.get("/{id}", response_model=PartnerPublic)
def get_partner(session: SessionDep, id: int):
    partner = session.exec(select(Partner).where(Partner.id == id)).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@router.post("", response_model=PartnerPublic)
def create_partner(session: SessionDep, partner: PartnerCreate):
    db_partner = session.exec(
        select(Partner).where(Partner.name == partner.name)
    ).first()
    if db_partner:
        raise HTTPException(status_code=400, detail="Partner already exists")

    db_partner = Partner.model_validate(partner)
    session.add(db_partner)
    session.commit()
    session.refresh(db_partner)
    return db_partner


@router.delete("/{id}")
def delete_partner(session: SessionDep, id: int):
    partner = session.exec(select(Partner).where(Partner.id == id)).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    session.delete(partner)
    session.commit()
