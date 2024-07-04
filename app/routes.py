from app.database import get_db
from app.helpers import generate_short_url, get_client_ip, get_geo_from_ip, get_title_tag_from_url
from app.repository.report_repository import get_all_for_short_url, insert_one
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
    return templates.TemplateResponse(request, "form.html")

@router.post("/shorten")
async def shorten_url(request: Request, url: str = Form(...), db: Session = Depends(get_db)):
    try:
        title = await get_title_tag_from_url(url)

        # Generate short URL
        short_url_hash = generate_short_url(url)
        
        # Insert into database
        find_or_insert_one(db, short_url_hash, url)
        
        # Construct full short URL
        short_url = f"{request.url.scheme}://{request.url.netloc}/{short_url_hash}"

        return {"short_url": short_url, "target_url": url, "short_url_hash": short_url_hash, "title": title}

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

@router.get("/report/{short_url}", response_class=HTMLResponse)
async def generate_report(request: Request, short_url: str, db: Session = Depends(get_db)):
    try:
        all_reports = get_all_for_short_url(db, short_url)
        visit_history = []
        for report in all_reports:
            report_obj = {
                "visited_at": report.visited_at,
                "lat": "Not available",
                "lon": "Not available",
                "region_name": "Not available"
            }
            geolocation_success = report.geolocation["status"]
            if geolocation_success == "success":
                report_obj["lat"] = report.geolocation["lat"]
                report_obj["lon"] = report.geolocation["lon"]
                report_obj["region_name"] = report.geolocation["regionName"]
            visit_history.append(report_obj)
    except Exception as e:
        log.error(f"error: {str(e)}")
        return HTMLResponse(content="<h1>Unexpected error generating report</h1>", status_code=500)
    return templates.TemplateResponse(request, "report.html", {"visit_history": visit_history ,"short_url": f"{request.url.scheme}://{request.url.netloc}/{short_url}"})
