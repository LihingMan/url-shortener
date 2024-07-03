from app.database import get_db
from app.helpers import generate_short_url, get_client_ip, get_geo_from_ip
from app.repository.report_repository import insert_one
from app.repository.shorturl_repository import find_or_insert_one, find_original_url, NotFound
from fastapi import APIRouter, HTTPException, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging
import httpx

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

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
async def redirect_to_url(short_url: str, request: Request, db: Session = Depends(get_db)):
    try:
        short_url_obj = find_original_url(db, short_url)
        ip_address = get_client_ip(request)
        geolocation = await get_geo_from_ip(ip_address)
        insert_one(db, short_url_obj.id, ip_address, geolocation)
        return RedirectResponse(url=short_url_obj.original_url)
    except NotFound as e:
        return HTMLResponse(content=f"<h1>{str(e)}</h1>", status_code=404)
    except httpx.HTTPStatusError as e:
        log.error(f"could not get geolocation for ip: {ip_address}")
    except Exception as e:
        log.error(f"error: {str(e)}")
        return HTMLResponse(content="<h1>Unexpected error redirecting</h1>", status_code=500)
