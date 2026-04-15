from sqlalchemy.orm import Session
from . import models, schemas

# Documents
def create_document(db: Session, filename: str, trip_id: int = None, extracted_data: str = None):
    doc = models.Document(
        filename=filename,
        trip_id=trip_id,
        extracted_data=extracted_data
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def assign_document_to_trip(db: Session, doc_id: int, trip_id: int):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise ValueError("Document not found")
    doc.trip_id = trip_id
    db.commit()
    db.refresh(doc)
    return doc

# Trips
def create_trip(db: Session, trip: schemas.TripCreate):
    trip_obj = models.Trip(name=trip.name)
    db.add(trip_obj)
    db.commit()
    db.refresh(trip_obj)
    return trip_obj

def get_trips(db: Session):
    return db.query(models.Trip).all()