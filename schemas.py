from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
class PredictRequest(BaseModel):
    """
    Validates the pollutant numbers sent by the user.
    'ge=0' ensures that values cannot be negative.
    """
    pm25: float = Field(..., ge=0, le=1000, description="PM2.5 concentration in µg/m³")
    pm10: float = Field(..., ge=0, le=1000, description="PM10 concentration in µg/m³")
    no2: float = Field(..., ge=0, le=1000, description="NO2 concentration in µg/m³")
    co: float = Field(..., ge=0, le=200, description="CO concentration in mg/m³")
    so2: float = Field(..., ge=0, le=1000, description="SO2 concentration in µg/m³")
    o3: float = Field(..., ge=0, le=1000, description="O3 concentration in µg/m³")
    model_config = {
        "json_schema_extra": {
            "example": {
                "pm25": 85.4,
                "pm10": 120.3,
                "no2": 42.1,
                "co": 0.8,
                "so2": 15.2,
                "o3": 35.6
            }
        }
    }
class PredictResponse(BaseModel):
    """
    Defines the response sent back to the user after predicting AQI.
    """
    id: Optional[int] = None
    predicted_aqi: float
    category: str
    advisory: str
    timestamp: datetime
class HistoryItemResponse(BaseModel):
    """
    Defines the structure for past predictions stored in the database.
    """
    id: int
    timestamp: datetime
    pm25: float
    pm10: float
    no2: float
    co: float
    so2: float
    o3: float
    predicted_aqi: float
    aqi_category: str
    model_config = ConfigDict(from_attributes=True)