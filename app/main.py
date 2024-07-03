import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic.config import Config
from alembic import command
from app.database import engine, Base

log = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)
# app.mount("/static", StaticFiles(directory="static"), name="static") # put back when it's ready

def run_migrations():
    log.info("Beginning migrations")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info("Starting up")
    run_migrations()
    yield
    log.info("Shutting down")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}
