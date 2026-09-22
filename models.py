from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .database import Base
class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pm25 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=False)
    no2 = Column(Float, nullable=False)
    co = Column(Float, nullable=False)
    so2 = Column(Float, nullable=False)
    o3 = Column(Float, nullable=False)
    predicted_aqi = Column(Float, nullable=False)
    aqi_category = Column(String(50), nullable=False)