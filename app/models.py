from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original = Column(String, nullable=False)
    short = Column(String, unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    expires_at = Column(DateTime, nullable=True)

class ClickLog(Base):
    __tablename__ = "click_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)