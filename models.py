from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class Schedule(str, Enum):
    matutino = "matutino"
    vespertino = "vespertino"
    mixto = "mixto"


class Modality(str, Enum):
    en_linea = "en linea"
    presencial = "presencial"
    mixto = "mixto"


class Days(str, Enum):
    entre_semana = "entre semana"
    fines_de_semana = "fines de semana"
    mixto = "mixto"


class VerificationTokenBase(SQLModel):
    expires_at: datetime


class VerificationToken(VerificationTokenBase, table=True):
    token: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)


class VerificationTokenPublic(VerificationTokenBase):
    token: str
    created_at: datetime


class VerificationTokenCreate(VerificationTokenBase):
    pass


class UserBase(SQLModel):
    email: str = Field(unique=True)
    role: UserRole = Field(default=UserRole.user)
    verified: bool = Field(default=False)
    name: str
    degree: str
    semester: int
    provider_id: str | None = None


class User(UserBase, table=True):
    id: str = Field(primary_key=True)
    token: Optional[str] = Field(default=None, foreign_key="verificationtoken.token")


class UserPublic(UserBase):
    id: str


class UserCreate(UserBase):
    id: str
    token: Optional[str] = None
    password: str


class UserUpdate(SQLModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None
    verified: Optional[bool] = None
    name: Optional[str] = None
    degree: Optional[str] = None
    semester: Optional[int] = None


class PartnerBase(SQLModel):
    name: str = Field(unique=True)


class Partner(PartnerBase, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )


class PartnerPublic(PartnerBase):
    id: int


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(SQLModel):
    name: Optional[str] = None


class ProjectBase(SQLModel):
    name: str = Field(unique=True)
    id_partner: int = Field(foreign_key="partner.id")
    slots: int = Field(default=0)
    schedule_detail: str
    description: str
    schedule: Schedule
    modality: Modality
    days: Days


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )


class ProjectPublic(ProjectBase):
    id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    slots: Optional[int] = None
    schedule_detail: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[Schedule] = None
    modality: Optional[Modality] = None
    days: Optional[Days] = None


class EnrolmentTokenBase(SQLModel):
    id_project: int = Field(foreign_key="project.id")
    expires_at: datetime


class EnrolmentToken(EnrolmentTokenBase, table=True):
    token: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=get_datetime_utc)


class EnrolmentTokenPublic(EnrolmentTokenBase):
    token: str
    created_at: datetime


class EnrolmentTokenCreate(EnrolmentTokenBase):
    pass


class EnrolmentBase(SQLModel):
    id_user: str = Field(foreign_key="user.id", primary_key=True)
    id_project: int = Field(foreign_key="project.id", primary_key=True)
    token: Optional[str] = Field(default=None, foreign_key="enrolmenttoken.token")


class Enrolment(EnrolmentBase, table=True):
    date: datetime = Field(default_factory=get_datetime_utc)


class EnrolmentPublic(EnrolmentBase):
    date: datetime


class EnrolmentCreate(EnrolmentBase):
    pass
