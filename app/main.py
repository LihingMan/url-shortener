from alembic.config import Config
from alembic import command
from app.database import SessionLocal, engine, Base
from app.helpers import generate_short_url
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from sqlalchemy.orm import Session

from app.repository.shorturl_repository import NotFound, find_or_insert_one, find_original_url

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/html")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/shorten")
async def shorten_url(request: Request, url: str = Form(...), db: Session = Depends(get_db)):
    try:
        # Generate short URL
        short_url_hash = generate_short_url(url)
        
        # Insert into database
        find_or_insert_one(db, short_url_hash, url)
        
        # Construct full short URL
        short_url = request.url.scheme + "://" + request.url.netloc + "/" + short_url_hash
        
        return {"short_url": short_url, "target_url": url, "title": "URL Shortener"}

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{short_url}", response_class=RedirectResponse)
async def redirect_to_url(short_url: str, db: Session = Depends(get_db)):
        try:
            original_url = find_original_url(db, short_url)
            print('HEHEHEHEHE', original_url)
            return RedirectResponse(url=original_url)
        except NotFound as e:
            return HTMLResponse(content=f"<h1>{str(e)}</h1>", status_code=404)
