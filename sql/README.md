# SQL Documentation - Database Schema & Management

MySQL database schema with automated procedures and triggers for the malnutrition analysis system.

## 🗄️ Database Overview

```
sql/
├── 00-create_tables.sql              # Core schema
├── 01-procedure-generate_child_id.sql # ID generation
├── 02-procedure-set_gender_text.sql   # Gender mapping
├── 03-trigger-before_insert_children.sql # Insert trigger
├── 04-trigger-before_update_children.sql # Update trigger
├── 10-insert_data.sql                # Sample data
└── erd_diagram.png                   # Entity diagram
```

## 🏗️ Database Schema

### Entity Relationship Diagram

![ERD Diagram](https://github.com/reponseashimwe/ml_pipeline_database/blob/main/sql/erd_diagram.png)

### Core Tables

**`children`** - Child demographics

-   `child_id` (VARCHAR(24), Primary Key) - Format: YYYYMMDD-HHMMSS-XXXX
-   `gender` (VARCHAR(10)) - 'Laki-laki' or 'Perempuan'
-   `gender_text` (VARCHAR(20)) - 'Male' or 'Female'
-   `current_stunting_status`, `current_wasting_status` - Latest diagnosis
-   Auto timestamps: `created_at`, `updated_at`

**`measurements`** - Anthropometric data

-   `measurement_id` (INT, Auto-increment)
-   `child_id` (VARCHAR(24), Foreign Key)
-   `age_months`, `body_length_cm`, `body_weight_kg`
-   `measurement_date` (DATE)

**`diagnosis`** - ML classifications

-   `diagnosis_id` (INT, Auto-increment)
-   `measurement_id` (INT, Foreign Key)
-   `stunting_status`, `wasting_status`
-   `diagnosis_date` (DATE)

## 🔧 Automated Features

### Stored Procedures

-   **`GenerateChildUniqueID()`** - Creates unique child IDs
-   **`SetGenderText()`** - Maps Indonesian gender to English

### Triggers

-   **`before_insert_children`** - Auto-generates ID and sets gender_text
-   **`before_update_children`** - Syncs gender changes

### Key Features

-   **Cascade Deletes** - Automatic cleanup of related records
-   **Foreign Key Constraints** - Data integrity enforcement
-   **Timestamp Automation** - Automatic created/updated tracking

## 🚀 Setup Process

```bash
# 1. Create database
mysql -u username -p -e "CREATE DATABASE malnutrition; USE malnutrition;"

# 2. Run scripts in order
mysql -u username -p malnutrition < 00-create_tables.sql
mysql -u username -p malnutrition < 01-procedure-generate_child_id.sql
mysql -u username -p malnutrition < 02-procedure-set_gender_text.sql
mysql -u username -p malnutrition < 03-trigger-before_insert_children.sql
mysql -u username -p malnutrition < 04-trigger-before_update_children.sql
mysql -u username -p malnutrition < 10-insert_data.sql
```

## 🔍 Usage Examples

```sql
-- Create child (ID auto-generated)
INSERT INTO children (gender) VALUES ('Laki-laki');

-- Add measurement
INSERT INTO measurements (child_id, age_months, body_length_cm, body_weight_kg)
VALUES ('20241201-143025-A1B2', 24, 85.5, 12.3);

-- Add diagnosis
INSERT INTO diagnosis (measurement_id, stunting_status, wasting_status)
VALUES (1, 'Normal', 'Normal weight');
```

## 🔒 Security

```sql
-- Create limited privilege user
CREATE USER 'malnutrition_app'@'localhost' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON malnutrition.* TO 'malnutrition_app'@'localhost';
GRANT EXECUTE ON PROCEDURE malnutrition.* TO 'malnutrition_app'@'localhost';
```

## 🚨 Common Issues

**Foreign Key Violations:**

-   Ensure parent records exist before inserting children

**Duplicate Child ID:**

-   Verify `GenerateChildUniqueID()` procedure working correctly

**Trigger Errors:**

-   Check stored procedures are created before triggers

## 📈 Maintenance

```sql
-- Check table sizes
SELECT table_name,
       ROUND((data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'malnutrition';

-- Backup database
mysqldump -u username -p --single-transaction malnutrition > backup.sql
```

## 📞 Support

-   Verify DATABASE_URL format in API configuration
-   Check MySQL service status and user permissions
-   Review foreign key relationships for data integrity
-   Test stored procedures and triggers functionality
