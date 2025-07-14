# Data Documentation - Child Malnutrition Dataset

Dataset management and processing for the child malnutrition analysis pipeline.

## 📁 Dataset Overview

```
data/
├── stunting_wasting_dataset.csv    # Main dataset (4.4MB, Indonesian)
├── split_data.py                   # Processing script
├── children.csv                    # Processed children records
├── measurements.csv                # Processed measurements
└── diagnosis.csv                   # Processed diagnoses
```

## 📊 Main Dataset

**Source:** [Kaggle - Stunting and Wasting Dataset](https://www.kaggle.com/datasets/jabirmuktabir/stunting-wasting-dataset)

-   **Size:** ~100,000 Indonesian child health records
-   **Language:** Indonesian column headers and values
-   **Quality:** Pre-validated against WHO growth standards

### Column Structure

| Indonesian          | English         | Type        | Range               | Description    |
| ------------------- | --------------- | ----------- | ------------------- | -------------- |
| `Jenis Kelamin`     | Gender          | Categorical | Laki-laki/Perempuan | Child's gender |
| `Umur (bulan)`      | Age             | Integer     | 0-60                | Age in months  |
| `Tinggi Badan (cm)` | Height          | Float       | 30-120              | Height in cm   |
| `Berat Badan (kg)`  | Weight          | Float       | 1-30                | Weight in kg   |
| `Stunting`          | Stunting Status | Categorical | 4 categories        | Classification |
| `Wasting`           | Wasting Status  | Categorical | 4 categories        | Classification |

## 🔄 Data Processing

### Running the Script

```bash
cd data/
python split_data.py
```

### What it does:

1. Loads `stunting_wasting_dataset.csv`
2. Creates binary mappings for ML training
3. Splits into normalized database tables:
    - `children.csv` - Demographics and status
    - `measurements.csv` - Anthropometric data
    - `diagnosis.csv` - Classifications

## 📈 Dataset Statistics

```
Total Records: ~100,000
Gender Distribution: 52% Male, 48% Female
Age Distribution: Evenly spread 0-60 months

Stunting Prevalence:
- Normal: ~65%
- Tall: ~10%
- Stunted: ~20%
- Severely Stunted: ~5%
```

## 🔍 Data Validation

Input validation ranges:

```python
age_months: 0-60
body_length_cm: 30.0-120.0
body_weight_kg: 1.0-30.0
gender: ['Laki-laki', 'Perempuan']
```

## 🔒 Privacy & Ethics

-   **Anonymized:** No personal identifiers
-   **Generated IDs:** Synthetic child identifiers
-   **Research Purpose:** Used only for malnutrition analysis
-   **Consent:** Collected with appropriate permissions

## 🔧 API Integration

-   **Startup Loading:** Automatic import on first API run
-   **Real-time Validation:** Input validation against data ranges
-   **ML Training:** Feature extraction matching training data

## 🚨 Common Issues

**Encoding Problems:**

```python
pd.read_csv('stunting_wasting_dataset.csv', encoding='utf-8')
```

**Memory Issues:**

```python
# Process in chunks for large files
for chunk in pd.read_csv('file.csv', chunksize=10000):
    process_chunk(chunk)
```

## 📞 Support

-   Check CSV encoding and delimiters
-   Validate data ranges against expected values
-   Review processing script logs for errors
-   Verify column mappings match database schema
