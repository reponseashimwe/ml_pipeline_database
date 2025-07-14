# MongoDB Schema (Aligned with ERD)

## Collections

### 1. children
```json
{
  "child_id": "string",                
  "gender": "string",
  "current_stunting_status": "string",
  "current_wasting_status": "string"
}
```
| Field                   | Type   | Description                      |
|-------------------------|--------|----------------------------------|
| child_id                | String | Unique child ID (PK)             |
| gender                  | String | Gender                           |
| current_stunting_status | String | Current stunting status          |
| current_wasting_status  | String | Current wasting status           |

### 2. measurements
```json
{
  "measurement_id": 1,                  
  "child_id": "string",               
  "age_months": 24,
  "body_length_cm": 85.5,
  "body_weight_kg": 12.3,
  "measurement_date": "2023-01-10"
}
```
| Field            | Type    | Description                              |
|------------------|---------|------------------------------------------|
| measurement_id   | Integer | Unique measurement ID (PK)               |
| child_id         | String  | Reference to children.child_id (FK)      |
| age_months       | Integer | Age in months                            |
| body_length_cm   | Float   | Body length in centimeters               |
| body_weight_kg   | Float   | Body weight in kilograms                 |
| measurement_date | String  | Date of measurement (YYYY-MM-DD)         |

### 3. diagnosis
```json
{
  "measurement_id": 1,                  
  "stunting_status": "string",
  "wasting_status": "string"
}
```
| Field           | Type    | Description                                  |
|-----------------|---------|----------------------------------------------|
| measurement_id  | Integer | Reference to measurements.measurement_id (PK, FK) |
| stunting_status | String  | Stunting status                              |
| wasting_status  | String  | Wasting status                               |
