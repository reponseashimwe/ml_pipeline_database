from fastapi import FastAPI, Depends, HTTPException, status, Query, Path, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
import models
import schemas
from database import get_db, init_db
from datetime import date, datetime
import os

app = FastAPI(
    title="Child Malnutrition Analysis API",
    description="API for managing and analyzing child malnutrition data.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    if not init_db():
        raise Exception("Failed to initialize database")
    # Load initial data from stunting_wasting_dataset.csv if empty
    db = next(get_db())
    if not crud.get_children(db):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(current_dir, 'data', 'stunting_wasting_dataset.csv')
        crud.load_stunting_wasting_dataset(db, csv_path)

@app.get("/children/", response_model=schemas.ChildrenResponse, tags=["Children"], summary="List all children")
def read_children(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(30, ge=1, le=100, description="Maximum number of records to return (default 30)"),
    stunting_status: Optional[schemas.StuntingStatus] = Query(None, description="Filter by stunting status"),
    wasting_status: Optional[schemas.WastingStatus] = Query(None, description="Filter by wasting status"),
    db: Session = Depends(get_db)
):
    try:
        total = crud.get_children_count(db, stunting_status=stunting_status, wasting_status=wasting_status)
        children = crud.get_children(db, skip=skip, limit=limit, stunting_status=stunting_status, wasting_status=wasting_status)
        return {
            "total": total,
            "limit": limit,
            "offset": skip,
            "data": children
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving children: {str(e)}"
        )

@app.get("/children/{child_id}", response_model=schemas.Child, tags=["Children"], summary="Get a specific child record")
def read_child(child_id: str = Path(..., description="The ID of the child to retrieve"), db: Session = Depends(get_db)):
    try:
        child = crud.get_child(db, child_id=child_id)
        if child is None:
            raise HTTPException(status_code=404, detail=f"Child with ID {child_id} not found")
        return child
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving the child: {str(e)}")

@app.post("/children/", response_model=schemas.Child, status_code=status.HTTP_201_CREATED, tags=["Children"], summary="Create a new child record")
def create_child(
    gender: schemas.Gender = Form(..., description="Gender of the child (Male/Female)"),
    age_months: int = Form(..., ge=0, le=60, description="Age in months (0-60)"),
    body_length_cm: float = Form(..., ge=30, le=120, description="Body length in centimeters"),
    body_weight_kg: float = Form(..., ge=1, le=30, description="Body weight in kilograms"),
    db: Session = Depends(get_db)
):
    try:
        child_data = schemas.ChildCreate(
            gender=gender,
            initial_measurement=schemas.MeasurementCreate(
                age_months=age_months,
                body_length_cm=body_length_cm,
                body_weight_kg=body_weight_kg
            )
        )
        return crud.create_child_with_measurement(db, child_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.put("/children/{child_id}", response_model=schemas.Child, tags=["Children"], summary="Update a child's gender")
def update_child(
    child_id: str = Path(..., description="The ID of the child to update"),
    gender: schemas.Gender = Form(..., description="Gender of the child (Male/Female)"),
    db: Session = Depends(get_db)
):
    try:
        return crud.update_child(db, child_id=child_id, gender=gender)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the child: {str(e)}"
        )

@app.delete("/children/{child_id}", response_model=schemas.Message, tags=["Children"], summary="Delete a child record")
def delete_child(
    child_id: str = Path(..., description="The ID of the child to delete"),
    db: Session = Depends(get_db)
):
    try:
        crud.delete_child(db, child_id=child_id)
        return {"detail": f"Child {child_id} deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the child: {str(e)}"
        )

@app.post("/measurements/", response_model=schemas.Measurement, status_code=status.HTTP_201_CREATED, tags=["Measurements"], summary="Create a new measurement")
def create_measurement(
    child_id: str = Form(..., description="ID of the child being measured"),
    age_months: int = Form(..., ge=0, le=60, description="Age in months (0-60)"),
    body_length_cm: float = Form(..., ge=30, le=120, description="Body length in centimeters"),
    body_weight_kg: float = Form(..., ge=1, le=30, description="Body weight in kilograms"),
    db: Session = Depends(get_db)
):
    try:
        # First check if child exists
        child = crud.get_child(db, child_id)
        if not child:
            raise HTTPException(status_code=404, detail=f"Child with ID {child_id} not found")
            
        measurement_data = schemas.MeasurementCreate(
            age_months=age_months,
            body_length_cm=body_length_cm,
            body_weight_kg=body_weight_kg
        )
        return crud.create_measurement_with_diagnosis(db, child_id, measurement_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the measurement: {str(e)}")

@app.get("/measurements/{child_id}", response_model=List[schemas.Measurement], tags=["Measurements"], summary="Get all measurements for a child")
def read_measurements(
    child_id: str = Path(..., description="The ID of the child to retrieve measurements for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(30, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    try:
        # First check if child exists
        child = crud.get_child(db, child_id)
        if not child:
            raise HTTPException(status_code=404, detail=f"Child with ID {child_id} not found")
            
        return crud.get_measurements(db, child_id=child_id, skip=skip, limit=limit)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving measurements: {str(e)}")

@app.put("/measurements/{measurement_id}", response_model=schemas.Measurement, tags=["Measurements"], summary="Update a measurement")
def update_measurement(
    measurement_id: int = Path(..., description="The ID of the measurement to update"),
    age_months: int = Form(..., ge=0, le=60, description="Age in months (0-60)"),
    body_length_cm: float = Form(..., ge=30, le=120, description="Body length in centimeters"),
    body_weight_kg: float = Form(..., ge=1, le=30, description="Body weight in kilograms"),
    db: Session = Depends(get_db)
):
    try:
        measurement_data = schemas.MeasurementUpdate(
            age_months=age_months,
            body_length_cm=body_length_cm,
            body_weight_kg=body_weight_kg
        )
        return crud.update_measurement(db, measurement_id=measurement_id, measurement=measurement_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the measurement: {str(e)}"
        )

@app.delete("/measurements/{measurement_id}", response_model=schemas.Message, tags=["Measurements"], summary="Delete a measurement record")
def delete_measurement(
    measurement_id: int = Path(..., description="The ID of the measurement to delete"),
    db: Session = Depends(get_db)
):
    try:
        crud.delete_measurement(db, measurement_id=measurement_id)
        return {"detail": f"Measurement {measurement_id} deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the measurement: {str(e)}"
        )

@app.get("/diagnosis/latest", response_model=schemas.DiagnosisResponse, tags=["Diagnosis"], summary="Get diagnosis from latest measurement")
def get_latest_diagnosis(db: Session = Depends(get_db)):
    try:
        measurement = crud.get_latest_measurement(db)
        if not measurement:
            raise HTTPException(
                status_code=404,
                detail="No measurements found in the system"
            )
        
        diagnosis = crud.perform_diagnosis(
            age_months=measurement.age_months,
            body_length_cm=measurement.body_length_cm,
            body_weight_kg=measurement.body_weight_kg,
            gender=measurement.child.gender
        )
        
        # Add measurement info
        diagnosis["measurement_id"] = measurement.measurement_id
        diagnosis["child_id"] = measurement.child_id
        
        return diagnosis
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the diagnosis: {str(e)}"
        )

@app.get("/diagnosis/child/{child_id}", response_model=schemas.DiagnosisResponse, tags=["Diagnosis"], summary="Get diagnosis from child's latest measurement")
def get_child_latest_diagnosis(
    child_id: str = Path(..., description="The ID of the child to diagnose"),
    db: Session = Depends(get_db)
):
    try:
        # First check if child exists
        child = crud.get_child(db, child_id)
        if not child:
            raise HTTPException(
                status_code=404,
                detail=f"Child with ID {child_id} not found"
            )
        
        measurement = crud.get_latest_measurement_by_child(db, child_id)
        if not measurement:
            raise HTTPException(
                status_code=404,
                detail=f"No measurements found for child {child_id}"
            )
        
        diagnosis = crud.perform_diagnosis(
            age_months=measurement.age_months,
            body_length_cm=measurement.body_length_cm,
            body_weight_kg=measurement.body_weight_kg,
            gender=measurement.child.gender
        )
        
        # Add measurement info
        diagnosis["measurement_id"] = measurement.measurement_id
        diagnosis["child_id"] = measurement.child_id
        
        return diagnosis
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the diagnosis: {str(e)}"
        )

@app.get("/diagnosis/measurement/{measurement_id}", response_model=schemas.DiagnosisResponse, tags=["Diagnosis"], summary="Get diagnosis for a specific measurement")
def get_measurement_diagnosis(
    measurement_id: int = Path(..., description="The ID of the measurement to diagnose"),
    db: Session = Depends(get_db)
):
    try:
        measurement = crud.get_measurement_by_id(db, measurement_id)
        if not measurement:
            raise HTTPException(
                status_code=404,
                detail=f"Measurement with ID {measurement_id} not found"
            )
        
        diagnosis = crud.perform_diagnosis(
            age_months=measurement.age_months,
            body_length_cm=measurement.body_length_cm,
            body_weight_kg=measurement.body_weight_kg,
            gender=measurement.child.gender
        )
        
        # Add measurement info
        diagnosis["measurement_id"] = measurement.measurement_id
        diagnosis["child_id"] = measurement.child_id
        
        return diagnosis
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the diagnosis: {str(e)}"
        )

@app.post("/diagnosis/predict", response_model=schemas.PredictionResponse, tags=["Diagnosis"], summary="Get diagnosis prediction from direct input")
def predict_diagnosis(
    gender: schemas.Gender = Form(..., description="Gender of the child (Laki-laki/Perempuan)"),
    age_months: int = Form(..., ge=0, le=60, description="Age in months (0-60)"),
    body_length_cm: float = Form(..., ge=30, le=120, description="Body length/height in centimeters"),
    body_weight_kg: float = Form(..., ge=1, le=30, description="Body weight in kilograms")
):
    """
    Get stunting prediction from direct input parameters without saving to database.
    
    Returns only the stunting prediction without wasting status.
    """
    try:
        diagnosis = crud.perform_diagnosis(
            age_months=age_months,
            body_length_cm=body_length_cm,
            body_weight_kg=body_weight_kg,
            gender=gender
        )
        
        # Return only the stunting prediction
        return {
            "stunting_status": diagnosis["stunting_status"],
            "age_months": age_months,
            "body_length_cm": body_length_cm,
            "body_weight_kg": body_weight_kg,
            "diagnosis_date": date.today().isoformat()
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform diagnosis: {str(e)}"
        )
