from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ShortURL(Base):
    __tablename__ = 'short_urls'

    id = Column(Integer, primary_key=True, index=True)
    short_url = Column(String(15), unique=True, index=True)
    original_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("Report", back_populates="short_url", cascade="all, delete-orphan")
