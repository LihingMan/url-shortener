from app.models.report import Report
from sqlalchemy.orm import Session

def insert_one(db: Session, short_url_id: int, ip_address: str, geolocation):
    db_report = Report(short_url_id=short_url_id, ip_address=ip_address, geolocation=geolocation)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
