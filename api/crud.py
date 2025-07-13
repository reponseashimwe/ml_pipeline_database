from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, desc
from typing import List, Optional
import models
import schemas
from datetime import date, datetime
import pandas as pd
import os
from fastapi import HTTPException
import sys
from pathlib import Path

# Add the parent directory to Python path to find the ml module
sys.path.append(str(Path(__file__).parent.parent))

try:
    from ml.predict import predict_stunting_status
except ImportError as e:
    print(f"Warning: ML module not found - {e}")
    print("Make sure the ml directory is in the Python path")
    predict_stunting_status = None

# Children CRUD operations
def create_child_with_measurement(db: Session, child_data: schemas.ChildCreate) -> models.Children:
    try:
        # First generate the ID
        db.execute(text("SET @new_id = NULL"))
        db.execute(text("CALL GenerateChildUniqueID(@new_id)"))
        result = db.execute(text("SELECT @new_id"))
        child_id = result.scalar()
        
        if not child_id:
            raise ValueError("Failed to generate child ID")
        
        # Create child record
        gender_text = "Male" if child_data.gender == schemas.Gender.MALE else "Female"
        db_child = models.Children(
            child_id=child_id,
            gender=child_data.gender,
            gender_text=gender_text
        )
        
        db.add(db_child)
        db.flush()  # Ensure child is created before measurement
        
        # Create measurement with diagnosis
        measurement_data = schemas.MeasurementCreate(
            age_months=child_data.initial_measurement.age_months,
            body_length_cm=child_data.initial_measurement.body_length_cm,
            body_weight_kg=child_data.initial_measurement.body_weight_kg
        )
        
        db_measurement = models.Measurements(
            child_id=child_id,
            age_months=measurement_data.age_months,
            body_length_cm=measurement_data.body_length_cm,
            body_weight_kg=measurement_data.body_weight_kg,
            measurement_date=date.today()
        )
        
        db.add(db_measurement)
        db.flush()  # Get measurement ID
        
        db.commit()
        db.refresh(db_child)
        return db_child
        
    except Exception as e:
        db.rollback()
        if isinstance(e, IntegrityError):
            raise HTTPException(
                status_code=400,
                detail="Invalid data: Could not create child record. Please check the provided values."
            )
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the child record: {str(e)}"
        )

def get_child(db: Session, child_id: str) -> Optional[models.Children]:
    return db.query(models.Children)\
        .options(joinedload(models.Children.measurements).joinedload(models.Measurements.diagnosis))\
        .filter(models.Children.child_id == child_id)\
        .first()

def get_children(db: Session, skip: int = 0, limit: int = 30, stunting_status: Optional[str] = None, wasting_status: Optional[str] = None) -> List[models.Children]:
    query = db.query(models.Children)\
        .options(joinedload(models.Children.measurements).joinedload(models.Measurements.diagnosis))\
        .order_by(desc(models.Children.created_at))
    
    if stunting_status:
        query = query.filter(models.Children.current_stunting_status == stunting_status)
    if wasting_status:
        query = query.filter(models.Children.current_wasting_status == wasting_status)
    
    return query.offset(skip).limit(limit).all()

def get_children_count(db: Session, stunting_status: Optional[str] = None, wasting_status: Optional[str] = None) -> int:
    query = db.query(models.Children)
    if stunting_status:
        query = query.filter(models.Children.current_stunting_status == stunting_status)
    if wasting_status:
        query = query.filter(models.Children.current_wasting_status == wasting_status)
    return query.count()

def update_child(db: Session, child_id: str, gender: schemas.Gender) -> models.Children:
    try:
        db_child = get_child(db, child_id)
        if not db_child:
            raise HTTPException(status_code=404, detail=f"Child with ID {child_id} not found")
        
        db_child.gender = gender
        db_child.gender_text = "Male" if gender == schemas.Gender.MALE else "Female"
        
        db.commit()
        db.refresh(db_child)
        return db_child
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update child: {str(e)}"
        )

def delete_child(db: Session, child_id: str) -> bool:
    try:
        db_child = get_child(db, child_id)
        if not db_child:
            raise HTTPException(status_code=404, detail=f"Child with ID {child_id} not found")
        
        db.delete(db_child)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete child: {str(e)}"
        )

# Measurements CRUD operations
def create_measurement_with_diagnosis(db: Session, child_id: str, measurement_data: schemas.MeasurementCreate) -> models.Measurements:
    try:
        # Create measurement record
        db_measurement = models.Measurements(
            child_id=child_id,
            age_months=measurement_data.age_months,
            body_length_cm=measurement_data.body_length_cm,
            body_weight_kg=measurement_data.body_weight_kg,
            measurement_date=date.today()
        )
        
        db.add(db_measurement)
        
        db.commit()
        db.refresh(db_measurement)
        
        # Ensure diagnosis is loaded
        measurement_with_diagnosis = db.query(models.Measurements)\
            .options(joinedload(models.Measurements.diagnosis))\
            .filter(models.Measurements.measurement_id == db_measurement.measurement_id)\
            .first()
            
        return measurement_with_diagnosis
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        if isinstance(e, IntegrityError):
            raise HTTPException(
                status_code=400,
                detail="Invalid data: Could not create measurement. Please check the provided values."
            )
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the measurement: {str(e)}"
        )

def get_measurements(db: Session, child_id: str, skip: int = 0, limit: int = 30) -> List[models.Measurements]:
    return db.query(models.Measurements)\
        .options(joinedload(models.Measurements.diagnosis))\
        .filter(models.Measurements.child_id == child_id)\
        .order_by(desc(models.Measurements.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def update_measurement(db: Session, measurement_id: int, measurement: schemas.MeasurementUpdate) -> models.Measurements:
    try:
        db_measurement = db.query(models.Measurements)\
            .options(joinedload(models.Measurements.diagnosis))\
            .filter(models.Measurements.measurement_id == measurement_id)\
            .first()
        
        if not db_measurement:
            raise HTTPException(status_code=404, detail=f"Measurement with ID {measurement_id} not found")
        
        # Update measurement values
        db_measurement.age_months = measurement.age_months
        db_measurement.body_length_cm = measurement.body_length_cm
        db_measurement.body_weight_kg = measurement.body_weight_kg
        
        # Recalculate diagnosis
        stunting_status, wasting_status = calculate_diagnosis(
            age_months=measurement.age_months,
            body_length_cm=measurement.body_length_cm,
            body_weight_kg=measurement.body_weight_kg
        )
        
        # Update diagnosis
        if db_measurement.diagnosis:
            db_measurement.diagnosis.stunting_status = stunting_status
            db_measurement.diagnosis.wasting_status = wasting_status
            db_measurement.diagnosis.diagnosis_date = date.today()
        else:
            db_diagnosis = models.Diagnosis(
                measurement_id=measurement_id,
                stunting_status=stunting_status,
                wasting_status=wasting_status,
                diagnosis_date=date.today()
            )
            db.add(db_diagnosis)
        
        # Update child's current status if this is the latest measurement
        latest_measurement = db.query(models.Measurements)\
            .filter(models.Measurements.child_id == db_measurement.child_id)\
            .order_by(desc(models.Measurements.created_at))\
            .first()
        
        if latest_measurement and latest_measurement.measurement_id == measurement_id:
            child = db.query(models.Children).filter(models.Children.child_id == db_measurement.child_id).first()
            if child:
                child.current_stunting_status = stunting_status
                child.current_wasting_status = wasting_status
        
        db.commit()
        db.refresh(db_measurement)
        return db_measurement
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update measurement: {str(e)}"
        )

def delete_measurement(db: Session, measurement_id: int) -> bool:
    try:
        db_measurement = db.query(models.Measurements)\
            .options(joinedload(models.Measurements.diagnosis))\
            .filter(models.Measurements.measurement_id == measurement_id)\
            .first()
            
        if not db_measurement:
            raise HTTPException(status_code=404, detail=f"Measurement with ID {measurement_id} not found")
        
        # Get the child's ID before deleting the measurement
        child_id = db_measurement.child_id
        
        # Delete the measurement (and its diagnosis due to cascade)
        db.delete(db_measurement)
        db.flush()
        
        # Update child's status based on their latest remaining measurement
        latest_measurement = db.query(models.Measurements)\
            .options(joinedload(models.Measurements.diagnosis))\
            .filter(models.Measurements.child_id == child_id)\
            .order_by(desc(models.Measurements.created_at))\
            .first()
        
        child = db.query(models.Children).filter(models.Children.child_id == child_id).first()
        if child:
            if latest_measurement and latest_measurement.diagnosis:
                child.current_stunting_status = latest_measurement.diagnosis.stunting_status
                child.current_wasting_status = latest_measurement.diagnosis.wasting_status
            else:
                child.current_stunting_status = None
                child.current_wasting_status = None
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete measurement: {str(e)}"
        )

def calculate_diagnosis(age_months: int, body_length_cm: float, body_weight_kg: float) -> tuple[str, str]:
    # TODO: Implement actual diagnosis calculation based on WHO standards
    # For now, return placeholder values
    return "Normal", "Normal weight"

def get_latest_measurement(db: Session) -> Optional[models.Measurements]:
    return db.query(models.Measurements)\
        .options(joinedload(models.Measurements.diagnosis))\
        .order_by(desc(models.Measurements.created_at))\
        .first()

def get_latest_measurement_by_child(db: Session, child_id: str) -> Optional[models.Measurements]:
    return db.query(models.Measurements)\
        .options(joinedload(models.Measurements.diagnosis))\
        .filter(models.Measurements.child_id == child_id)\
        .order_by(desc(models.Measurements.created_at))\
        .first()

def get_measurement_by_id(db: Session, measurement_id: int) -> Optional[models.Measurements]:
    return db.query(models.Measurements)\
        .options(joinedload(models.Measurements.diagnosis))\
        .filter(models.Measurements.measurement_id == measurement_id)\
        .first()

def perform_diagnosis(age_months: int, body_length_cm: float, body_weight_kg: float, gender: str) -> dict:
    """
    Perform diagnosis using the trained ML model
    """
    try:
        if predict_stunting_status is None:
            raise ImportError("ML module not properly loaded")
        
        # Get stunting prediction from ML model
        stunting_status = predict_stunting_status(
            age_months=age_months,
            body_length_cm=body_length_cm,
            body_weight_kg=body_weight_kg,
            gender=gender
        )
        
        # Return diagnosis results
        return {
            "stunting_status": stunting_status,
            "age_months": age_months,
            "body_length_cm": body_length_cm,
            "body_weight_kg": body_weight_kg,
            "diagnosis_date": date.today().isoformat()
        }

    except Exception as e:
        raise Exception(f"Failed to perform diagnosis: {str(e)}")

# Initial data loader for stunting_wasting_dataset.csv
def load_stunting_wasting_dataset(db: Session, csv_path: str):
    print(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} total records")
    
    # Limit to 500 rows
    df = df.head(500)
    print(f"Processing first 500 records")
    
    for idx, row in df.iterrows():
        try:
            # Create child with initial measurement
            child_data = schemas.ChildCreate(
                gender=row["Jenis Kelamin"],
                initial_measurement=schemas.MeasurementCreate(
                    age_months=int(row["Umur (bulan)"]),
                    body_length_cm=float(row["Tinggi Badan (cm)"]),
                    body_weight_kg=float(row["Berat Badan (kg)"])
                )
            )
            
            print(f"Processing record {idx+1}/500")
            create_child_with_measurement(db, child_data)
            print(f"Successfully processed record {idx+1}/500")
            
        except Exception as e:
            print(f"Error processing record {idx+1}/500: {str(e)}")
            db.rollback()
            continue
    
    print("Data loading completed!")
