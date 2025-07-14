import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# Define the required fields for each collection based on the ERD/schema
collection_fields = {
    "children": ["child_id", "gender", "current_stunting_status", "current_wasting_status"],
    "measurements": ["measurement_id", "child_id", "age_months", "body_length_cm", "body_weight_kg", "measurement_date"],
    "diagnosis": ["measurement_id", "stunting_status", "wasting_status"]
}

csv_collection_map = {
    "children.csv": "children",
    "diagnosis.csv": "diagnosis",
    "measurements.csv": "measurements"
}

def import_csv_to_mongo(csv_path, collection_name):
    df = pd.read_csv(csv_path)
    required_fields = collection_fields[collection_name]
    df = df[[col for col in required_fields if col in df.columns]]
    records = df.to_dict(orient='records')
    if records:
        db[collection_name].insert_many(records)
        print(f"Inserted {len(records)} records into '{collection_name}' collection.")
    else:
        print(f"No records found in {csv_path}.")

if __name__ == "__main__":
    for csv_file, collection in csv_collection_map.items():
        try:
            import_csv_to_mongo(f"data/{csv_file}", collection)
        except Exception as e:
            print(f"Error importing {csv_file} into {collection}: {e}") 