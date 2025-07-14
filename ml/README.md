# ML Module Documentation - Child Stunting Prediction

Machine learning component for predicting child stunting status using Random Forest Classification.

## 🧠 Model Overview

**Objective:** Predict stunting status from anthropometric measurements

-   **Algorithm:** Random Forest Classifier
-   **Model File:** `random_forest_optimized.joblib` (57MB)
-   **Performance:** ~95% training accuracy, <100ms prediction time

## 📁 Module Structure

```
ml/
├── __init__.py                    # Module initialization
├── predict.py                     # Prediction pipeline
├── random_forest_optimized.joblib # Trained model
└── README.md                      # Documentation
```

## 🔬 Model Specifications

### Input Features

| Feature     | Type        | Range               | Description           |
| ----------- | ----------- | ------------------- | --------------------- |
| Age_Months  | Integer     | 0-60                | Child's age in months |
| Gender      | Categorical | Laki-laki/Perempuan | Child's gender        |
| Body_Weight | Float       | 1.0-30.0            | Weight in kg          |
| Body_Length | Float       | 30.0-120.0          | Height in cm          |

### Output Classes

-   **Normal** - Healthy growth ✅
-   **Tall** - Above average height ✅
-   **Stunted** - Below average height ⚠️
-   **Severely Stunted** - Significantly below average 🚨

## 🔧 Usage

```python
from ml.predict import predict_stunting_status

result = predict_stunting_status(
    age_months=24,
    body_length_cm=85.0,
    body_weight_kg=12.5,
    gender='Laki-laki'
)
# Returns: "Normal", "Stunted", "Severely Stunted", or "Tall"
```

## ⚡ Preprocessing Pipeline

-   **Numerical Features:** StandardScaler (Age, Weight, Height)
-   **Categorical Features:** OneHotEncoder (Gender)
-   **Missing Values:** Median imputation for numerical data
-   **Gender Mapping:** Indonesian values preserved from training

## 🔄 API Integration

Automatic integration with FastAPI endpoints:

-   Called during measurement creation/update
-   Powers `/diagnosis/predict` endpoint
-   Graceful fallback to "Normal" if model unavailable

## 🚨 Common Issues

**Feature Count Mismatch:**

-   Ensure preprocessor sees both gender categories during initialization

**Unknown Gender Categories:**

-   Use original Indonesian values: "Laki-laki", "Perempuan"

**Model Loading Errors:**

-   Verify `random_forest_optimized.joblib` exists in ml/ directory
-   Check file permissions and scikit-learn compatibility

## 📈 Model Performance

-   **Training Data:** ~100,000 Indonesian child health records
-   **Feature Importance:** Age > Height > Weight > Gender
-   **Memory Usage:** ~200MB when loaded
-   **Prediction Speed:** Sub-100ms response time

## 🔄 Model Updates

1. Train new model with updated dataset
2. Replace `random_forest_optimized.joblib`
3. Restart API service
4. Verify integration via `/diagnosis/predict` endpoint

## 📞 Support

-   Test predictions with known sample data
-   Monitor prediction latency and accuracy
-   Check model file integrity and permissions
-   Verify input data formats match training requirements
