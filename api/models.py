from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import date, datetime
from database import Base

class Children(Base):
    __tablename__ = "Children"

    child_id = Column(String(24), primary_key=True)
    gender = Column(String(10), nullable=False)
    gender_text = Column(String(20), nullable=False)
    current_stunting_status = Column(String(50), nullable=True)
    current_wasting_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    measurements = relationship("Measurements", back_populates="child", cascade="all, delete-orphan")

class Measurements(Base):
    __tablename__ = "Measurements"

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(String(24), ForeignKey('Children.child_id', ondelete='CASCADE'), nullable=False)
    age_months = Column(Integer, nullable=False)
    body_length_cm = Column(Float(precision=2), nullable=False)
    body_weight_kg = Column(Float(precision=2), nullable=False)
    measurement_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    child = relationship("Children", back_populates="measurements")
    diagnosis = relationship("Diagnosis", back_populates="measurement", cascade="all, delete-orphan", uselist=False)

class Diagnosis(Base):
    __tablename__ = "Diagnosis"

    diagnosis_id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id = Column(Integer, ForeignKey('Measurements.measurement_id', ondelete='CASCADE'), nullable=False)
    stunting_status = Column(String(50), nullable=False)
    wasting_status = Column(String(50), nullable=False)
    diagnosis_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    measurement = relationship("Measurements", back_populates="diagnosis")
