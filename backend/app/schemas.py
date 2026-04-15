from pydantic import BaseModel
from typing import Optional, Dict, Any

# Documents
class DocumentCreate(BaseModel):
    filename: str
    trip_id: Optional[int] = None

class DocumentResponse(BaseModel):
    id: int
    filename: str
    trip_id: Optional[int]
    extracted_data: Dict[str, Any]

    class Config:
        orm_mode = True

# Trips
class TripCreate(BaseModel):
    name: str

class Trip(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True