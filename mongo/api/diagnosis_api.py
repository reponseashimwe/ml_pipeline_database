from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
MONGO_URI = "mongodb+srv://rntabana:Renep123@ml-cluster.huuj3ty.mongodb.net/?retryWrites=true&w=majority&appName=ML-Cluster"
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# Pydantic model for Diagnosis
class Diagnosis(BaseModel):
    measurement_id: int
    stunting_status: str
    wasting_status: str

@app.post("/mongo/diagnosis/", response_model=Diagnosis)
def create_diagnosis(diagnosis: Diagnosis):
    if db.diagnosis.find_one({"measurement_id": diagnosis.measurement_id}):
        raise HTTPException(status_code=400, detail="Diagnosis already exists")
    db.diagnosis.insert_one(diagnosis.dict())
    return diagnosis

@app.get("/mongo/diagnosis/", response_model=List[Diagnosis])
def get_diagnoses():
    diagnoses = list(db.diagnosis.find({}, {"_id": 0}))
    return diagnoses

@app.get("/mongo/diagnosis/{measurement_id}", response_model=Diagnosis)
def get_diagnosis(measurement_id: int):
    diagnosis = db.diagnosis.find_one({"measurement_id": measurement_id}, {"_id": 0})
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return diagnosis

@app.put("/mongo/diagnosis/{measurement_id}", response_model=Diagnosis)
def update_diagnosis(measurement_id: int, diagnosis: Diagnosis):
    result = db.diagnosis.update_one({"measurement_id": measurement_id}, {"$set": diagnosis.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return diagnosis

@app.delete("/mongo/diagnosis/{measurement_id}")
def delete_diagnosis(measurement_id: int):
    result = db.diagnosis.delete_one({"measurement_id": measurement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return {"detail": "Diagnosis deleted"} 