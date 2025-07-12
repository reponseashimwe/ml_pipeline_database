from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from datetime import date
from database import Base

class Children(Base):
    __tablename__ = "Children"

    child_id = Column(String(15), primary_key=True)
    gender = Column(String(10), nullable=False)
    current_stunting_status = Column(SmallInteger, nullable=True)
    current_wasting_status = Column(SmallInteger, nullable=True)

    # Relationships
    measurements = relationship("Measurements", back_populates="child", cascade="all, delete-orphan")

class Measurements(Base):
    __tablename__ = "Measurements"

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(String(15), ForeignKey('Children.child_id'), nullable=False)
    age_months = Column(Integer, nullable=False)
    body_length_cm = Column(Float(precision=2), nullable=False)
    body_weight_kg = Column(Float(precision=2), nullable=False)
    measurement_date = Column(Date, default=date.today)

    # Relationships
    child = relationship("Children", back_populates="measurements")
    diagnosis = relationship("Diagnosis", back_populates="measurement", cascade="all, delete-orphan")

class Diagnosis(Base):
    __tablename__ = "Diagnosis"

    diagnosis_id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id = Column(Integer, ForeignKey('Measurements.measurement_id'), nullable=False)
    stunting_status = Column(SmallInteger, nullable=False)
    wasting_status = Column(SmallInteger, nullable=False)
    diagnosis_date = Column(Date, default=date.today)

    # Relationships
    measurement = relationship("Measurements", back_populates="diagnosis")
