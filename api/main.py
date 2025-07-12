from fastapi import FastAPI, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
import models
import schemas
from database import get_db, init_db
from datetime import date

app = FastAPI(
    title="Child Malnutrition Analysis API",
    description="""
    API for managing and analyzing child malnutrition data.
    
    Features:
    * Create and manage child records
    * Record measurements and track growth
    * Diagnose stunting and wasting conditions
    * Generate predictions using machine learning
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Startup Event
@app.on_event("startup")
async def startup_event():
    if not init_db():
        raise Exception("Failed to initialize database")

# Health Check
@app.get(
    "/health",
    response_model=schemas.DatabaseStatus,
    tags=["System"],
    summary="Check API health"
)
def health_check():
    """
    Check if the API is running and healthy.
    """
    return {"status": "healthy", "timestamp": str(date.today())}

# Children Endpoints
@app.post(
    "/children/",
    response_model=schemas.Child,
    status_code=status.HTTP_201_CREATED,
    tags=["Children"],
    summary="Create a new child record"
)
def create_child(
    child: schemas.ChildCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new child record with the following information:
    
    - **gender**: Male or Female
    - **child_id**: Optional - will be auto-generated if not provided
    - **current_stunting_status**: Optional initial stunting status
    - **current_wasting_status**: Optional initial wasting status
    """
    try:
        return crud.create_child(db, child_id=child.child_id, gender=child.gender.value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get(
    "/children/{child_id}",
    response_model=schemas.Child,
    tags=["Children"],
    summary="Get a specific child's record"
)
def read_child(
    child_id: str = Path(..., description="The ID of the child to get"),
    db: Session = Depends(get_db)
):
    """
    Get a specific child's record by their ID.
    """
    db_child = crud.get_child(db, child_id=child_id)
    if db_child is None:
        raise HTTPException(status_code=404, detail="Child not found")
    return db_child

@app.get(
    "/children/",
    response_model=List[schemas.Child],
    tags=["Children"],
    summary="List all children"
)
def read_children(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get a list of all children records with pagination.
    """
    children = crud.get_children(db, skip=skip, limit=limit)
    return children

# Measurements Endpoints
@app.post(
    "/measurements/",
    response_model=schemas.Measurement,
    status_code=status.HTTP_201_CREATED,
    tags=["Measurements"],
    summary="Create a new measurement"
)
def create_measurement(
    measurement: schemas.MeasurementCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new measurement record with the following information:
    
    - **child_id**: ID of the child being measured
    - **age_months**: Age in months (0-60)
    - **body_length_cm**: Body length in centimeters (30-120)
    - **body_weight_kg**: Body weight in kilograms (1-30)
    """
    if not crud.get_child(db, child_id=measurement.child_id):
        raise HTTPException(status_code=404, detail="Child not found")
    
    return crud.create_measurement(
        db,
        child_id=measurement.child_id,
        age_months=measurement.age_months,
        body_length_cm=measurement.body_length_cm,
        body_weight_kg=measurement.body_weight_kg
    )

@app.get(
    "/measurements/{child_id}",
    response_model=List[schemas.Measurement],
    tags=["Measurements"],
    summary="Get all measurements for a child"
)
def read_measurements(
    child_id: str = Path(..., description="The ID of the child to get measurements for"),
    db: Session = Depends(get_db)
):
    """
    Get all measurements for a specific child.
    """
    if not crud.get_child(db, child_id=child_id):
        raise HTTPException(status_code=404, detail="Child not found")
    
    measurements = crud.get_measurements(db, child_id=child_id)
    return measurements

# Diagnosis Endpoints
@app.post(
    "/diagnosis/",
    response_model=schemas.Diagnosis,
    status_code=status.HTTP_201_CREATED,
    tags=["Diagnosis"],
    summary="Create a new diagnosis"
)
def create_diagnosis(
    diagnosis: schemas.DiagnosisCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new diagnosis record with the following information:
    
    - **measurement_id**: ID of the measurement being diagnosed
    - **stunting_status**: Stunting status diagnosis
    - **wasting_status**: Wasting status diagnosis
    """
    return crud.create_diagnosis(
        db,
        measurement_id=diagnosis.measurement_id,
        stunting_status=diagnosis.stunting_status,
        wasting_status=diagnosis.wasting_status
    )

@app.get(
    "/diagnosis/{measurement_id}",
    response_model=List[schemas.Diagnosis],
    tags=["Diagnosis"],
    summary="Get diagnosis history for a measurement"
)
def read_diagnosis_history(
    measurement_id: int = Path(..., description="The ID of the measurement to get diagnosis for"),
    db: Session = Depends(get_db)
):
    """
    Get the diagnosis history for a specific measurement.
    """
    diagnosis_history = crud.get_diagnosis_history(db, measurement_id=measurement_id)
    if not diagnosis_history:
        raise HTTPException(status_code=404, detail="No diagnosis found for this measurement")
    return diagnosis_history

# Database Status
@app.get(
    "/database/status",
    response_model=schemas.DatabaseStatus,
    tags=["System"],
    summary="Check database status"
)
def check_database_status(db: Session = Depends(get_db)):
    """
    Check if the database is populated with data.
    """
    is_populated = crud.is_database_populated(db)
    return {
        "status": "populated" if is_populated else "empty",
        "timestamp": str(date.today())
    }
