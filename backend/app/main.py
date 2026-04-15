from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import shutil, json, traceback
from pathlib import Path

from app import models, schemas, database, crud
from app.ollama_client import analyze_document
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.export_trip import create_trip_excel

# FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB
models.Base.metadata.create_all(bind=database.engine)

# Uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Routes
@app.post("/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    trip_id: int = None,
    db: Session = Depends(database.get_db),
    background_tasks: BackgroundTasks = None,
):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = crud.create_document(
        db,
        filename=file.filename,
        trip_id=trip_id,
        extracted_data=json.dumps({"status": "processing"})
    )

    if background_tasks:
        background_tasks.add_task(process_document, str(file_path), document.id)

    return {
        "id": document.id,
        "filename": document.filename,
        "trip_id": document.trip_id,
        "extracted_data": {"status": "processing"}
    }


# Background processing
def process_document(file_path: str, document_id: int):
    from app.database import SessionLocal
    from app import models

    db = SessionLocal()
    try:
        result = analyze_document(file_path)

        raw_text = None
        parsed = {}

        if isinstance(result, dict):
            parsed = result
        elif isinstance(result, str):
            raw_text = result
            try:
                parsed = json.loads(result)
            except Exception:
                parsed = {}
        else:
            parsed = {}

        extracted_data = {
            "status": "done",
            "raw_text": raw_text,
            "amount": float(str(parsed.get("amount", 0)).replace("$", "")) if "amount" in parsed else 0,
            "category": parsed.get("category", "Other"),
            "date": parsed.get("date"),
        }

        for k, v in parsed.items():
            if k not in extracted_data:
                extracted_data[k] = v

    except Exception as e:
        print("Background task error:", str(e))
        print(traceback.format_exc())
        extracted_data = {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }

    try:
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if document:
            document.extracted_data = json.dumps(extracted_data)
            db.commit()
    except Exception as e:
        print("Error updating document in DB:", str(e))
        print(traceback.format_exc())
    finally:
        db.close()


# Trips
@app.post("/trips", response_model=schemas.Trip)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_trip(db, trip)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to create a trip")

@app.get("/trips", response_model=list[schemas.Trip])
def get_trips(db: Session = Depends(database.get_db)):
    return crud.get_trips(db)


# Assign document
@app.patch("/documents/{doc_id}/assign", response_model=schemas.DocumentResponse)
def assign_document(doc_id: int, trip_id: int, db: Session = Depends(database.get_db)):
    return crud.assign_document_to_trip(db, doc_id, trip_id)


# Trip summary
@app.get("/trips/{trip_id}/summary")
def get_trip_summary(trip_id: int, db: Session = Depends(database.get_db)):
    documents = db.query(models.Document).filter(models.Document.trip_id == trip_id).all()
    total = 0
    categories_sum = {}
    for doc in documents:
        try:
            data = json.loads(doc.extracted_data)
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}

        try:
            amount = float(str(data.get("amount", 0)).replace("$", ""))
        except Exception:
            amount = 0

        total += amount
        cat = data.get("category", "Other")
        categories_sum[cat] = categories_sum.get(cat, 0) + amount

    return {"total": total, "count": len(documents), "categories": categories_sum}


# Export trip to Excel
@app.get("/trips/{trip_id}/export")
def export_trip_excel_endpoint(trip_id: int, db: Session = Depends(database.get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    documents = db.query(models.Document).filter(models.Document.trip_id == trip_id).all()
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for this trip")

    stream, filename = create_trip_excel(documents, trip.name)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# Get document (polling)
@app.get("/documents/{doc_id}", response_model=schemas.DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(database.get_db)):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        extracted_data = json.loads(document.extracted_data)
        if not isinstance(extracted_data, dict):
            extracted_data = {"status": "processing"}
    except Exception:
        extracted_data = {"status": "processing"}

    print(f"Polling /documents/{doc_id} returned: {extracted_data}")

    return {
        "id": document.id,
        "filename": document.filename,
        "trip_id": document.trip_id,
        "extracted_data": extracted_data
    }


# Update document
@app.patch("/documents/{doc_id}")
def update_document(doc_id: int, data: dict, db: Session = Depends(database.get_db)):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        existing = json.loads(document.extracted_data)
        if not isinstance(existing, dict):
            existing = {}
    except Exception:
        existing = {}

    existing.update(data)
    document.extracted_data = json.dumps(existing)
    db.commit()
    return {"status": "ok"}

# Delete document
@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(database.get_db)):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        db.delete(document)
        db.commit()
        return {"status": "ok", "message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
    
# Delete trip
@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(database.get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    try:
        documents = db.query(models.Document).filter(models.Document.trip_id == trip_id).all()
        for doc in documents:
            db.delete(doc)
        db.delete(trip)
        db.commit()
        return {"status": "ok", "message": "Trip and all related documents deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete trip: {str(e)}")
    
# Get trip documents
@app.get("/trips/{trip_id}/documents")
def get_trip_documents(trip_id: int, db: Session = Depends(database.get_db)):
    documents = db.query(models.Document).filter(models.Document.trip_id == trip_id).all()
    result = []
    for doc in documents:
        try:
            data = json.loads(doc.extracted_data)
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}

        result.append({
            "id": doc.id,
            "amount": data.get("amount"),
            "category": data.get("category"),
            "date": data.get("date")
        })
    return result