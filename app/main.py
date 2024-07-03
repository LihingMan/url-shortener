from alembic.config import Config
from alembic import command
from app.routes import router
from app.database import engine, Base
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("uvicorn.error")

def run_migrations():
    log.info("Beginning migrations")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info("Starting up")
    Base.metadata.create_all(bind=engine)
    run_migrations()
    yield
    log.info("Shutting down")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/html")

app.include_router(router)
