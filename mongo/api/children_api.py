from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# Convert integer status fields to strings
for doc in db.children.find():
    update = {}
    if isinstance(doc.get("current_stunting_status"), int):
        update["current_stunting_status"] = str(doc["current_stunting_status"])
    if isinstance(doc.get("current_wasting_status"), int):
        update["current_wasting_status"] = str(doc["current_wasting_status"])
    if update:
        db.children.update_one({"_id": doc["_id"]}, {"$set": update})

# Remove documents missing 'child_id'
db.children.delete_many({"child_id": {"$exists": False}})

print("Children collection cleaned.")

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
    valid = [
        c for c in children
        if "child_id" in c and
           isinstance(c.get("current_stunting_status"), str) and
           isinstance(c.get("current_wasting_status"), str)
    ]
    return valid

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
