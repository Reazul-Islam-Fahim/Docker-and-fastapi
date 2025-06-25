from sqlalchemy import Column, Integer, String, Boolean, func, Float, DateTime
from database.db import Base
from sqlalchemy.orm import relationship

class SliderType(Base):
    __tablename__ = "slider_type"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    rate = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())