# MongoDB Schema

## Collections

### 1. children
```json
{
  "_id": "ObjectId",
  "child_id": "string",      
  "name": "string",
  "gender": "string",
  "date_of_birth": "YYYY-MM-DD"
}
```
| Field         | Type     | Description                |
|---------------|----------|----------------------------|
| _id           | ObjectId | MongoDB unique identifier  |
| child_id      | String   | Unique child ID            |
| name          | String   | Child's name               |
| gender        | String   | Gender                     |
| date_of_birth | String   | Date of birth (YYYY-MM-DD) |
| ...           | ...      | Additional fields as needed|

### 2. diagnosis
```json
{
  "_id": "ObjectId",
  "diagnosis_id": "string",  
  "child_id": "string",         
  "diagnosis_date": "YYYY-MM-DD",
  "diagnosis_type": "string",
  "result": "string"
}
```
| Field          | Type     | Description                        |
|----------------|----------|------------------------------------|
| _id            | ObjectId | MongoDB unique identifier          |
| diagnosis_id   | String   | Unique diagnosis ID                |
| child_id       | String   | Reference to children.child_id     |
| diagnosis_date | String   | Date of diagnosis (YYYY-MM-DD)     |
| diagnosis_type | String   | Type of diagnosis                  |
| result         | String   | Diagnosis result                   |
| ...            | ...      | Additional fields as needed        |

### 3. measurements
```json
{
  "_id": "ObjectId",
  "measurement_id": "string", 
  "child_id": "string",         
  "measurement_date": "YYYY-MM-DD",
  "height_cm": 100.5,
  "weight_kg": 15.2
}
```
| Field            | Type     | Description                        |
|------------------|----------|------------------------------------|
| _id              | ObjectId | MongoDB unique identifier          |
| measurement_id   | String   | Unique measurement ID              |
| child_id         | String   | Reference to children.child_id     |
| measurement_date | String   | Date of measurement (YYYY-MM-DD)   |
| height_cm        | Number   | Height in centimeters              |
| weight_kg        | Number   | Weight in kilograms                |
| ...              | ...      | Additional fields as needed        |
