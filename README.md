# Child Malnutrition Analysis ML Pipeline

A comprehensive machine learning pipeline system for analyzing and predicting child stunting status based on anthropometric measurements using Indonesian child health data.

## 🏗️ System Architecture

This project implements a complete ML pipeline with the following components:

```
ml_pipeline_database/
├── api/          # FastAPI web service with REST endpoints
├── data/         # Data processing and CSV management
├── ml/           # Machine learning models and prediction logic
├── sql/          # Database schema, procedures, and triggers
├── mongo/        # MongoDB schema documentation (alternative)
└── reports/      # Project documentation and analysis reports
```

## 🗄️ Database Schema

### Entity Relationship Diagram

![ERD Diagram](https://github.com/reponseashimwe/ml_pipeline_database/blob/main/sql/erd_diagram.png)

The database consists of three main entities:

-   **Children** - Demographic information and current health status
-   **Measurements** - Anthropometric data (height, weight, age)
-   **Diagnosis** - ML-generated malnutrition classifications

### Key Database Features

-   **Automated ID Generation** - Unique child identifiers with timestamp format
-   **Cascade Relationships** - Automatic cleanup of related records
-   **Stored Procedures** - ID generation and gender text mapping
-   **Triggers** - Automatic field updates and data consistency
-   **Bilingual Support** - Indonesian source data with English display values

## 📊 Dataset Information

**Source:** [Stunting and Wasting Dataset - Kaggle](https://www.kaggle.com/datasets/jabirmuktabir/stunting-wasting-dataset)

-   **Size:** ~100,000 Indonesian child health records
-   **Features:** Age, Gender, Height, Weight, Malnutrition Status
-   **Language:** Indonesian column headers and categorical values
-   **Quality:** Pre-validated against WHO growth standards

## 🔬 Machine Learning Model

-   **Algorithm:** Random Forest Classifier
-   **Target:** Stunting status prediction (4 categories)
-   **Features:** Age (months), Gender, Body Weight (kg), Body Length (cm)
-   **Performance:** ~95%+ training accuracy, <100ms prediction time
-   **Preprocessing:** StandardScaler + OneHotEncoder pipeline

## 🌐 Live Demo

**Deployed API:** [https://pipeline-database.onrender.com/docs](https://pipeline-database.onrender.com/docs)

-   Interactive Swagger UI documentation
-   Real-time prediction endpoints
-   Complete CRUD operations for child health data
-   Form-based data entry interface

## 🚀 Quick Start

### Prerequisites

-   Python 3.8+
-   MySQL 5.7+ or MariaDB 10.3+
-   Virtual environment (recommended)

### Installation

1. **Setup environment:**

    ```bash
    cd ml_pipeline_database/api
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Configure database:**

    ```bash
    echo "DATABASE_URL=mysql+pymysql://username:password@localhost/malnutrition" > .env
    ```

3. **Initialize database:**

    ```bash
    # Run SQL scripts in order (see sql/README.md)
    mysql -u username -p malnutrition < ../sql/00-create_tables.sql
    # ... (complete setup in sql/README.md)
    ```

4. **Start API server:**

    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

5. **Access documentation:**
    - Local API: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints Overview

### Core Operations

-   **Children Management** - CRUD operations for child records
-   **Measurements** - Anthropometric data tracking
-   **Diagnosis** - ML-powered malnutrition assessment
-   **Prediction** - Direct stunting status prediction

### Key Features

-   Form-based data entry with validation
-   Real-time ML predictions
-   Comprehensive filtering and pagination
-   Automatic diagnosis generation

## 🔧 Technical Stack

-   **Backend:** FastAPI with SQLAlchemy ORM
-   **Database:** MySQL with automated procedures and triggers
-   **ML Framework:** scikit-learn with joblib model persistence
-   **Data Processing:** pandas and numpy
-   **Validation:** Pydantic schemas with comprehensive validation
-   **Documentation:** Auto-generated Swagger UI and ReDoc

## 📁 Documentation Structure

Each component has detailed documentation:

-   **[API Documentation](api/README.md)** - FastAPI implementation details
-   **[ML Documentation](ml/README.md)** - Model architecture and prediction logic
-   **[Data Documentation](data/README.md)** - Dataset processing and validation
-   **[SQL Documentation](sql/README.md)** - Database schema and procedures

## 📄 Project Report

**Full Technical Report:** [Project Report PDF](https://example.com/malnutrition-analysis-report.pdf) _(to be updated)_

Contains detailed methodology, results, and recommendations for the malnutrition analysis system.

## 🎯 Use Cases

### Clinical Applications

-   Rapid malnutrition screening in healthcare settings
-   Growth monitoring and early intervention
-   Population health assessment

### Research Applications

-   Large-scale nutritional epidemiology studies
-   ML model development and validation
-   Cross-cultural adaptation of growth standards

### Integration Scenarios

-   Electronic health record systems
-   Mobile health applications
-   Government health monitoring platforms

## 🔒 Privacy & Security

-   **Data Anonymization** - No personally identifiable information
-   **Generated Identifiers** - Synthetic child IDs for privacy protection
-   **Secure Database** - Parameterized queries and access controls
-   **Environment Variables** - Sensitive configuration externalized

## 🐛 Troubleshooting

Common issues and solutions are documented in individual component READMEs:

-   Database connection problems → [SQL Documentation](sql/README.md)
-   ML model loading errors → [ML Documentation](ml/README.md)
-   API configuration issues → [API Documentation](api/README.md)

## 📈 Future Enhancements

-   Integration with WHO growth standards
-   Advanced visualization dashboards
-   Mobile application development
-   Multi-language localization
-   Deep learning model exploration
-   Real-time monitoring capabilities

## 📞 Support

For technical support:

-   Review component-specific documentation
-   Check the [live API documentation](https://pipeline-database.onrender.com/docs)
-   Examine database schema in [SQL documentation](sql/README.md)
-   Refer to ML model details in [ML documentation](ml/README.md)

---

**Dataset Source:** [Kaggle - Stunting and Wasting Dataset](https://www.kaggle.com/datasets/jabirmuktabir/stunting-wasting-dataset)  
**Live Demo:** [https://pipeline-database.onrender.com/docs](https://pipeline-database.onrender.com/docs)  
**Technical Report:** [Project Documentation](https://example.com/malnutrition-analysis-report.pdf)
