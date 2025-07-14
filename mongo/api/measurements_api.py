from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
MONGO_URI = "mongodb+srv://rntabana:Renep123@ml-cluster.huuj3ty.mongodb.net/?retryWrites=true&w=majority&appName=ML-Cluster"
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# Pydantic model for Measurements
class Measurement(BaseModel):
    measurement_id: int
    child_id: str
    age_months: int
    body_length_cm: float
    body_weight_kg: float
    measurement_date: str

@app.post("/mongo/measurements/", response_model=Measurement)
def create_measurement(measurement: Measurement):
    if db.measurements.find_one({"measurement_id": measurement.measurement_id}):
        raise HTTPException(status_code=400, detail="Measurement already exists")
    db.measurements.insert_one(measurement.dict())
    return measurement

@app.get("/mongo/measurements/", response_model=List[Measurement])
def get_measurements():
    measurements = list(db.measurements.find({}, {"_id": 0}))
    return measurements

@app.get("/mongo/measurements/{measurement_id}", response_model=Measurement)
def get_measurement(measurement_id: int):
    measurement = db.measurements.find_one({"measurement_id": measurement_id}, {"_id": 0})
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement

@app.put("/mongo/measurements/{measurement_id}", response_model=Measurement)
def update_measurement(measurement_id: int, measurement: Measurement):
    result = db.measurements.update_one({"measurement_id": measurement_id}, {"$set": measurement.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement

@app.delete("/mongo/measurements/{measurement_id}")
def delete_measurement(measurement_id: int):
    result = db.measurements.delete_one({"measurement_id": measurement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return {"detail": "Measurement deleted"} 