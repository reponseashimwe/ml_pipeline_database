from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum

class Gender(str, Enum):
    MALE = "Laki-laki"      # Indonesian for Male
    FEMALE = "Perempuan"    # Indonesian for Female

class StuntingStatus(int, Enum):
    SEVERELY_STUNTED = -2   # Severely stunted growth
    STUNTED = -1           # Stunted growth
    NORMAL = 0             # Normal growth
    TALL = 1              # Above normal height

class WastingStatus(int, Enum):
    SEVERELY_WASTED = -2    # Severely underweight
    WASTED = -1            # Underweight
    NORMAL = 0             # Normal weight
    RISK_OF_OVERWEIGHT = 1  # Risk of being overweight
    OVERWEIGHT = 2         # Overweight

# Children Schemas
class ChildBase(BaseModel):
    gender: Gender = Field(..., description="Gender of the child (Laki-laki=Male/Perempuan=Female)")
    current_stunting_status: Optional[StuntingStatus] = Field(None, description="Current stunting status (-2=Severely stunted, -1=Stunted, 0=Normal, 1=Tall)")
    current_wasting_status: Optional[WastingStatus] = Field(None, description="Current wasting status (-2=Severely wasted, -1=Wasted, 0=Normal, 1=Risk of overweight, 2=Overweight)")

class ChildCreate(ChildBase):
    child_id: Optional[str] = Field(None, description="Child ID (will be auto-generated if not provided)")

class Child(ChildBase):
    child_id: str = Field(..., description="Unique identifier for the child")

    class Config:
        from_attributes = True

# Measurements Schemas
class MeasurementBase(BaseModel):
    age_months: int = Field(..., ge=0, le=60, description="Age in months (0-60)")
    body_length_cm: float = Field(..., ge=30, le=120, description="Body length in centimeters")
    body_weight_kg: float = Field(..., ge=1, le=30, description="Body weight in kilograms")

class MeasurementCreate(MeasurementBase):
    child_id: str = Field(..., description="ID of the child being measured")

class Measurement(MeasurementBase):
    measurement_id: int = Field(..., description="Unique identifier for the measurement")
    child_id: str = Field(..., description="ID of the child being measured")
    measurement_date: date = Field(..., description="Date of measurement")

    class Config:
        from_attributes = True

# Diagnosis Schemas
class DiagnosisBase(BaseModel):
    stunting_status: StuntingStatus = Field(..., description="Stunting status diagnosis")
    wasting_status: WastingStatus = Field(..., description="Wasting status diagnosis")

class DiagnosisCreate(DiagnosisBase):
    measurement_id: int = Field(..., description="ID of the measurement being diagnosed")

class Diagnosis(DiagnosisBase):
    diagnosis_id: int = Field(..., description="Unique identifier for the diagnosis")
    measurement_id: int = Field(..., description="ID of the measurement being diagnosed")
    diagnosis_date: date = Field(..., description="Date of diagnosis")

    class Config:
        from_attributes = True

# Response Models
class Message(BaseModel):
    detail: str

class DatabaseStatus(BaseModel):
    status: str
    timestamp: str 