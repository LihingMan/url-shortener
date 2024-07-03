from app.models.shorturl import ShortURL
from sqlalchemy.orm import Session
import logging

log = logging.getLogger(__name__)

class NotFound(Exception):
    pass

def find_or_insert_one(db: Session, short_url_hash: str, original_url: str) -> str:
    exists = db.query(ShortURL).filter(ShortURL.short_url == short_url_hash).first()
    if exists:
        return exists.short_url

    db_shorturl = ShortURL(original_url=original_url, short_url=short_url_hash)
    db.add(db_shorturl)
    db.commit()
    db.refresh(db_shorturl)
    return db_shorturl.short_url

def find_original_url(db: Session, short_url_hash: str) -> ShortURL:
    exists = db.query(ShortURL).filter(ShortURL.short_url == short_url_hash).first()
    if exists is None:
        raise NotFound("Short URL does not exist!")

    return exists

def find_one(db: Session, short_url_hash: str) -> ShortURL:
    exists = db.query(ShortURL).filter(ShortURL.short_url == short_url_hash).first()

    if exists is None:
        raise NotFound("Short URL does not exist!")

    return exists
