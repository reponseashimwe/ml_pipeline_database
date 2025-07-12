from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import models
import schemas
from datetime import date

# Children CRUD operations
def create_child(db: Session, child_id: Optional[str], gender: str) -> models.Children:
    """Create a new child record.
    
    Args:
        db: Database session
        child_id: Optional child ID (will be auto-generated if None)
        gender: Gender in Indonesian (Laki-laki/Perempuan)
    """
    db_child = models.Children(
        child_id=child_id,
        gender=gender  # Store original Indonesian value
    )
    try:
        db.add(db_child)
        db.commit()
        db.refresh(db_child)
        return db_child
    except IntegrityError:
        db.rollback()
        raise ValueError("Child with this ID already exists")

def get_child(db: Session, child_id: str) -> Optional[models.Children]:
    """Get a child by ID."""
    return db.query(models.Children).filter(models.Children.child_id == child_id).first()

def get_children(db: Session, skip: int = 0, limit: int = 100) -> List[models.Children]:
    """Get a list of children with pagination."""
    return db.query(models.Children).offset(skip).limit(limit).all()

def update_child_status(
    db: Session, 
    child_id: str, 
    stunting_status: Optional[schemas.StuntingStatus] = None,
    wasting_status: Optional[schemas.WastingStatus] = None
) -> Optional[models.Children]:
    """Update a child's stunting and wasting status."""
    db_child = get_child(db, child_id)
    if db_child:
        if stunting_status is not None:
            db_child.current_stunting_status = stunting_status.value
        if wasting_status is not None:
            db_child.current_wasting_status = wasting_status.value
        db.commit()
        db.refresh(db_child)
    return db_child

# Measurements CRUD operations
def create_measurement(
    db: Session,
    child_id: str,
    age_months: int,
    body_length_cm: float,
    body_weight_kg: float
) -> models.Measurements:
    """Create a new measurement record."""
    db_measurement = models.Measurements(
        child_id=child_id,
        age_months=age_months,
        body_length_cm=body_length_cm,
        body_weight_kg=body_weight_kg,
        measurement_date=date.today()
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def get_measurements(db: Session, child_id: str) -> List[models.Measurements]:
    """Get all measurements for a child."""
    return db.query(models.Measurements).filter(models.Measurements.child_id == child_id).all()

def get_latest_measurement(db: Session, child_id: str) -> Optional[models.Measurements]:
    """Get the most recent measurement for a child."""
    return db.query(models.Measurements)\
        .filter(models.Measurements.child_id == child_id)\
        .order_by(models.Measurements.measurement_date.desc())\
        .first()

# Diagnosis CRUD operations
def create_diagnosis(
    db: Session,
    measurement_id: int,
    stunting_status: schemas.StuntingStatus,
    wasting_status: schemas.WastingStatus
) -> models.Diagnosis:
    """Create a new diagnosis record."""
    db_diagnosis = models.Diagnosis(
        measurement_id=measurement_id,
        stunting_status=stunting_status.value,
        wasting_status=wasting_status.value,
        diagnosis_date=date.today()
    )
    db.add(db_diagnosis)
    db.commit()
    db.refresh(db_diagnosis)
    return db_diagnosis

def get_diagnosis_history(db: Session, measurement_id: int) -> List[models.Diagnosis]:
    """Get diagnosis history for a measurement."""
    return db.query(models.Diagnosis)\
        .filter(models.Diagnosis.measurement_id == measurement_id)\
        .order_by(models.Diagnosis.diagnosis_date.desc())\
        .all()

# Utility function to check if database is populated
def is_database_populated(db: Session) -> bool:
    """Check if the database has any records."""
    return db.query(models.Children).count() > 0
