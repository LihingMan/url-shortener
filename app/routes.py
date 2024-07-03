from app.database import get_db
from app.helpers import generate_short_url
from app.repository.shorturl_repository import find_or_insert_one, find_original_url, NotFound
from fastapi import APIRouter, HTTPException, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("uvicorn.error")

router = APIRouter()

templates = Jinja2Templates(directory="static/html")

@router.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse({"request": request}, "form.html")

@router.post("/shorten")
async def shorten_url(request: Request, url: str = Form(...), db: Session = Depends(get_db)):
    try:
        # Generate short URL
        short_url_hash = generate_short_url(url)
        
        # Insert into database
        find_or_insert_one(db, short_url_hash, url)
        
        # Construct full short URL
        short_url = f"{request.url.scheme}://{request.url.netloc}/{short_url_hash}"

        return {"short_url": short_url, "target_url": url}

    except Exception as e:
        log.error(f"Error shortening url: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{short_url}", response_class=RedirectResponse)
async def redirect_to_url(short_url: str, db: Session = Depends(get_db)):
    try:
        original_url = find_original_url(db, short_url)
        return RedirectResponse(url=original_url)
    except NotFound as e:
        return HTMLResponse(content=f"<h1>{str(e)}</h1>", status_code=404)
