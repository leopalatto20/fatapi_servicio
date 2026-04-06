import os
import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from qrcode import QRCode
from qrcode.image.pil import PilImage
from sqlalchemy.sql.dml import Insert

from ..common.guards import admin_guard
from ..db import SessionDep
from ..models import User, VerificationToken

router = APIRouter(prefix="/verification-tokens", tags=["verification-tokens"])

QR_CODES_DIR = "static/qr_codes"


@router.post("")
def create_verification_token(session: SessionDep, _: User = Depends(admin_guard)):
    os.makedirs(QR_CODES_DIR, exist_ok=True)

    length = 8
    token = "".join(random.choices(string.ascii_letters + string.digits, k=length))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    session.exec(Insert(VerificationToken).values(token=token, expires_at=expires_at))
    session.commit()

    frontend_url = os.getenv("FRONTEND_URL")
    if not frontend_url:
        raise ValueError("FRONTEND_URL environment variable not set")

    qr = QRCode()
    qr.add_data(f"{frontend_url}/verify?token={token}")
    img: PilImage = qr.make_image(image_factory=PilImage)

    qr_path = os.path.join(QR_CODES_DIR, f"{token}.png")
    img.save(qr_path)

    return {"qr_code_path": f"/qr_codes/{token}.png"}
