from typing import List
from app.models.report import Report
from app.repository.shorturl_repository import find_one
from sqlalchemy.orm import Session

def insert_one(db: Session, short_url_id: int, ip_address: str, geolocation):
    db_report = Report(short_url_id=short_url_id, ip_address=ip_address, geolocation=geolocation)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

def get_all_for_short_url(db: Session, short_url_hash: str) -> List[Report]:
    short_url = find_one(db, short_url_hash)

    return db.query(Report).filter(Report.short_url_id == short_url.id).all()
