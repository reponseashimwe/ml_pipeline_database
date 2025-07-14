from pymongo import MongoClient

MONGO_URI = "mongodb+srv://rntabana:Renep123@ml-cluster.huuj3ty.mongodb.net/?retryWrites=true&w=majority&appName=ML-Cluster"
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# 1. Create 'children' collection and insert a sample document
children = db["children"]
children.insert_one({
    "child_id": "C001",
    "name": "John Doe",
    "gender": "Male",
    "date_of_birth": "2015-06-01"
})

# 2. Create 'diagnosis' collection and insert a sample document
diagnosis = db["diagnosis"]
diagnosis.insert_one({
    "diagnosis_id": "D001",
    "child_id": "C001",
    "diagnosis_date": "2023-01-15",
    "diagnosis_type": "Malnutrition",
    "result": "Stunted"
})

# 3. Create 'measurements' collection and insert a sample document
measurements = db["measurements"]
measurements.insert_one({
    "measurement_id": "M001",
    "child_id": "C001",
    "measurement_date": "2023-01-10",
    "height_cm": 102.5,
    "weight_kg": 15.8
})

print("Collections created and sample documents inserted.")