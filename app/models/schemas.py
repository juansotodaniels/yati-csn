from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class SeismicEvent(BaseModel):
    source: str
    event_id: Optional[str] = None
    origin_time: str
    latitude: float
    longitude: float
    depth_km: float
    magnitude: float
    place: Optional[str] = None


class IntensityResult(BaseModel):
    locality: str
    intensity: float


class PreliminaryEventResponse(BaseModel):
    status: str
    message: str
    event: SeismicEvent
    intensities: List[IntensityResult]
    metadata: Optional[Dict[str, Any]] = None
