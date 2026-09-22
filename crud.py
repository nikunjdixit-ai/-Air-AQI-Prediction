from sqlalchemy.orm import Session
from .models import PredictionHistory
from .schemas import PredictRequest
def save_prediction(db: Session, req: PredictRequest, aqi: float, category: str) -> PredictionHistory:
    """
    Inserts a newly predicted AQI record into the SQLite database.
    """
    record = PredictionHistory(
        pm25=req.pm25,
        pm10=req.pm10,
        no2=req.no2,
        co=req.co,
        so2=req.so2,
        o3=req.o3,
        predicted_aqi=aqi,
        aqi_category=category
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
def get_recent_history(db: Session, limit: int = 50):
    """
    Fetches the most recent predictions from the database,
    ordered from newest to oldest.
    """
    return db.query(PredictionHistory).order_by(PredictionHistory.timestamp.desc()).limit(limit).all()