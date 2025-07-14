# API Documentation - Child Malnutrition Analysis

FastAPI-based REST API for managing child health data and providing real-time malnutrition status predictions.

## 🏗️ Architecture

```
api/
├── main.py          # FastAPI application and routes
├── models.py        # SQLAlchemy ORM models
├── schemas.py       # Pydantic validation schemas
├── crud.py          # Database operations
├── database.py      # Database configuration
└── requirements.txt # Dependencies
```

## 🚀 Quick Setup

```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "DATABASE_URL=mysql+pymysql://user:pass@host/malnutrition" > .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access:** http://localhost:8000/docs

## 📚 Key Endpoints

### Children Management

-   `GET /children/` - List children with filtering/pagination
-   `POST /children/` - Create child with initial measurement
-   `GET /children/{child_id}` - Get specific child details
-   `PUT /children/{child_id}` - Update child gender
-   `DELETE /children/{child_id}` - Remove child record

### Measurements

-   `POST /measurements/` - Add new measurement
-   `GET /measurements/{child_id}` - Get child's measurements
-   `PUT /measurements/{measurement_id}` - Update measurement
-   `DELETE /measurements/{measurement_id}` - Remove measurement

### Diagnosis & Prediction

-   `GET /diagnosis/latest` - Latest measurement diagnosis
-   `GET /diagnosis/child/{child_id}` - Child's latest diagnosis
-   `POST /diagnosis/predict` - Direct prediction (no storage)

## 📋 Data Models

### Gender Enum

-   `Laki-laki` (Male)
-   `Perempuan` (Female)

### Stunting Status

-   `Normal`, `Tall`, `Stunted`, `Severely Stunted`

### Wasting Status

-   `Normal weight`, `Risk of Overweight`, `Underweight`, `Severely Underweight`

## 🔧 Technical Features

-   **Database:** MySQL with SQLAlchemy ORM
-   **Validation:** Pydantic schemas with range validation
-   **ML Integration:** Real-time stunting predictions
-   **Auto-generation:** Child IDs via stored procedures
-   **Cascade Deletes:** Automatic cleanup of related records

## ⚙️ Configuration

Environment variables in `.env`:

```bash
DATABASE_URL=mysql+pymysql://user:pass@host:port/database
DEBUG=true
LOG_LEVEL=info
```

## 🔒 Security

-   Parameterized queries (SQL injection prevention)
-   Input validation with Pydantic
-   Environment-based configuration
-   Limited database privileges

## 🐛 Common Issues

**Database Connection Error:**

-   Check DATABASE_URL format
-   Verify MySQL service running

**ML Model Not Found:**

-   Ensure `ml/random_forest_optimized.joblib` exists
-   Check parent directory structure

**Validation Errors:**

-   Verify input ranges: age (0-60), height (30-120), weight (1-30)
-   Use correct gender values: "Laki-laki" or "Perempuan"

## 📞 Support

-   Interactive docs: `/docs` endpoint
-   API schema: `/openapi.json`
-   Live demo: [https://pipeline-database.onrender.com/docs](https://pipeline-database.onrender.com/docs)
