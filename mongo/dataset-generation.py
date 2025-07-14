import pandas as pd
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb+srv://rntabana:Renep123@ml-cluster.huuj3ty.mongodb.net/?retryWrites=true&w=majority&appName=ML-Cluster"
client = MongoClient(MONGO_URI)
db = client["Ml_Foramtive"]

# Mapping of CSV files to collection names
csv_collection_map = {
    "children.csv": "children",
    "diagnosis.csv": "diagnosis",
    "measurements.csv": "measurements"
}

def import_csv_to_mongo(csv_path, collection_name):
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient='records')
    if records:
        db[collection_name].insert_many(records)
        print(f"Inserted {len(records)} records into '{collection_name}' collection.")
    else:
        print(f"No records found in {csv_path}.")

if __name__ == "__main__":
    for csv_file, collection in csv_collection_map.items():
        csv_path = f"../data/{csv_file}" if __file__.startswith("/Users") else f"data/{csv_file}"
        try:
            import_csv_to_mongo(f"data/{csv_file}", collection)
        except Exception as e:
            print(f"Error importing {csv_file} into {collection}: {e}") 