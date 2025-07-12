from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "Laki-laki"
    FEMALE = "Perempuan"

    @property
    def display_value(self) -> str:
        return "Male" if self == Gender.MALE else "Female"

class StuntingStatus(str, Enum):
    SEVERELY_STUNTED = "Severely Stunted"
    STUNTED = "Stunted"
    NORMAL = "Normal"
    TALL = "Tall"

class WastingStatus(str, Enum):
    SEVERELY_UNDERWEIGHT = "Severely Underweight"
    UNDERWEIGHT = "Underweight"
    NORMAL = "Normal weight"
    RISK_OF_OVERWEIGHT = "Risk of Overweight"

class Message(BaseModel):
    detail: str

# Diagnosis Schema
class DiagnosisBase(BaseModel):
    stunting_status: StuntingStatus
    wasting_status: WastingStatus
    diagnosis_date: date = Field(default_factory=date.today)

class DiagnosisCreate(DiagnosisBase):
    pass

class Diagnosis(DiagnosisBase):
    diagnosis_id: int
    measurement_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Measurement Schemas
class MeasurementBase(BaseModel):
    age_months: int = Field(..., ge=0, le=60, description="Age in months (0-60)")
    body_length_cm: float = Field(..., ge=30, le=120, description="Body length in centimeters")
    body_weight_kg: float = Field(..., ge=1, le=30, description="Body weight in kilograms")

class MeasurementCreate(MeasurementBase):
    pass

class MeasurementUpdate(MeasurementBase):
    pass

class Measurement(MeasurementBase):
    measurement_id: int
    child_id: str
    measurement_date: date
    created_at: datetime
    updated_at: datetime
    diagnosis: Optional[Diagnosis] = None

    class Config:
        orm_mode = True

# Children Schemas
class ChildBase(BaseModel):
    gender: Gender = Field(..., description="Gender of the child (Male/Female)")

class ChildCreate(ChildBase):
    initial_measurement: MeasurementCreate = Field(..., description="Initial measurement for the child")

class Child(ChildBase):
    child_id: str
    gender_text: str
    current_stunting_status: Optional[StuntingStatus]
    current_wasting_status: Optional[WastingStatus]
    created_at: datetime
    updated_at: datetime
    measurements: List[Measurement] = []

    class Config:
        orm_mode = True

class ChildrenResponse(BaseModel):
    total: int = Field(..., description="Total number of records")
    limit: int = Field(..., description="Number of records per page")
    offset: int = Field(..., description="Number of records skipped")
    data: List[Child]

    class Config:
        orm_mode = True

# Form schemas for HTML forms
class ChildForm(BaseModel):
    gender: str = Field(..., description="Gender selection")
    age_months: int = Field(..., description="Age in months")
    body_length_cm: float = Field(..., description="Body length in cm")
    body_weight_kg: float = Field(..., description="Body weight in kg")

class DiagnosisResponse(BaseModel):
    stunting_status: StuntingStatus
    wasting_status: WastingStatus
    age_months: int = Field(..., ge=0, le=60)
    body_length_cm: float = Field(..., ge=30, le=120)
    body_weight_kg: float = Field(..., ge=1, le=30)
    diagnosis_date: date
    measurement_id: Optional[int] = None
    child_id: Optional[str] = None

    class Config:
        orm_mode = True 