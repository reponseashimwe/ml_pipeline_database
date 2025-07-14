from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
MONGO_URI = "mongodb+srv://rntabana:Renep123@ml-cluster.huuj3ty.mongodb.net/?retryWrites=true&w=majority&appName=ML-Cluster"
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# Pydantic model for Children
class Child(BaseModel):
    child_id: str
    gender: str
    current_stunting_status: str
    current_wasting_status: str

@app.post("/mongo/children/", response_model=Child)
def create_child(child: Child):
    if db.children.find_one({"child_id": child.child_id}):
        raise HTTPException(status_code=400, detail="Child already exists")
    db.children.insert_one(child.dict())
    return child

@app.get("/mongo/children/", response_model=List[Child])
def get_children():
    children = list(db.children.find({}, {"_id": 0}))
    return children

@app.get("/mongo/children/{child_id}", response_model=Child)
def get_child(child_id: str):
    child = db.children.find_one({"child_id": child_id}, {"_id": 0})
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return child

@app.put("/mongo/children/{child_id}", response_model=Child)
def update_child(child_id: str, child: Child):
    result = db.children.update_one({"child_id": child_id}, {"$set": child.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Child not found")
    return child

@app.delete("/mongo/children/{child_id}")
def delete_child(child_id: str):
    result = db.children.delete_one({"child_id": child_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Child not found")
    return {"detail": "Child deleted"}
