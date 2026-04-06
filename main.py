from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import create_db_and_tables
from .routers import partners, projects, users, verification_tokens
from .security.firebase import start_firebase


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    start_firebase()
    yield
    print("Closing DB")


app = FastAPI(lifespan=lifespan)
app.mount("/qr_codes", StaticFiles(directory="static/qr_codes"), name="qr_codes")
app.include_router(partners.router)
app.include_router(users.router)
app.include_router(verification_tokens.router)
app.include_router(projects.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
