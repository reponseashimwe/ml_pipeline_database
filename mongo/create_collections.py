from pymongo import MongoClient

MONGO_URI = "mongodb+srv://rntabana:Renep123@ml-cluster.huuj3ty.mongodb.net/?retryWrites=true&w=majority&appName=ML-Cluster"
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# 1. Clear and create 'children' collection, then insert a sample document
children = db["children"]
children.delete_many({})  # Clear all documents
children.insert_one({
    "child_id": "C001",
    "gender": "Male",
    "current_stunting_status": "Normal",
    "current_wasting_status": "At Risk"
})

# 2. Clear and create 'diagnosis' collection, then insert a sample document
diagnosis = db["diagnosis"]
diagnosis.delete_many({})
diagnosis.insert_one({
    "measurement_id": 1,
    "stunting_status": "Normal",
    "wasting_status": "Moderate"
})

# 3. Clear and create 'measurements' collection, then insert a sample document
measurements = db["measurements"]
measurements.delete_many({})
measurements.insert_one({
    "measurement_id": 1,
    "child_id": "C001",
    "age_months": 24,
    "body_length_cm": 85.5,
    "body_weight_kg": 12.3,
    "measurement_date": "2023-01-10"
})

print("Collections cleared and sample documents inserted.")