from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    short_url_id = Column(Integer, ForeignKey('short_urls.id'), nullable=False, index=True)
    visited_at = Column(DateTime(timezone=True), default=func.now())
    ip_address = Column(String, nullable=True)
    geolocation = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    short_url = relationship("ShortURL", back_populates="report")
