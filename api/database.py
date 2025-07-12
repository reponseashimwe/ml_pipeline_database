from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql
import pandas as pd
import os
from datetime import datetime
from enum import Enum

# Status Enums
class StuntingStatus(str, Enum):
    SEVERELY_STUNTED = "Severely Stunted"
    STUNTED = "Stunted"
    NORMAL = "Normal"
    TALL = "Tall"

class WastingStatus(str, Enum):
    SEVERELY_UNDERWEIGHT = "Severely Underweight"
    UNDERWEIGHT = "Underweight"
    NORMAL = "Normal weight"
    RISK_OVERWEIGHT = "Risk of Overweight"

class Gender(str, Enum):
    MALE = "Laki-laki"
    FEMALE = "Perempuan"

# Database connection configuration
DATABASE_URL = "mysql+pymysql://root:00990099@localhost:3306/malnutrition"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable automatic reconnection
    pool_size=5,         # Maximum number of connections in the pool
    max_overflow=10      # Maximum number of connections that can be created beyond pool_size
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def setup_stored_procedures_and_triggers():
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Drop existing procedures and triggers
                drop_statements = [
                    "DROP PROCEDURE IF EXISTS GenerateChildUniqueID",
                    "DROP PROCEDURE IF EXISTS SetGenderText",
                    "DROP TRIGGER IF EXISTS before_insert_children",
                    "DROP TRIGGER IF EXISTS before_update_children"
                ]
                
                for stmt in drop_statements:
                    conn.execute(text(stmt))
                
                # Create stored procedure for ID generation
                stored_proc = """
                CREATE PROCEDURE GenerateChildUniqueID(OUT generated_id VARCHAR(24))
                BEGIN
                    SET generated_id := CONCAT(
                        DATE_FORMAT(NOW(), '%Y%m%d-%H%i%s-'),
                        UPPER(SUBSTRING(MD5(RAND()), 1, 4))
                    );
                END
                """
                conn.execute(text(stored_proc))
                
                # Create procedure for gender text conversion
                gender_proc = """
                CREATE PROCEDURE SetGenderText(IN gender_value VARCHAR(10), OUT gender_text_value VARCHAR(20))
                BEGIN
                    IF gender_value = 'Laki-laki' THEN
                        SET gender_text_value := 'Male';
                    ELSEIF gender_value = 'Perempuan' THEN
                        SET gender_text_value := 'Female';
                    ELSE
                        SET gender_text_value := 'Unknown';
                    END IF;
                END
                """
                conn.execute(text(gender_proc))
                
                # Create before insert trigger for children
                before_insert_trigger = """
                CREATE TRIGGER before_insert_children
                BEFORE INSERT ON Children
                FOR EACH ROW
                BEGIN
                    DECLARE gender_text_val VARCHAR(20);
                    
                    -- Generate child ID if not provided
                    IF NEW.child_id IS NULL OR NEW.child_id = '' THEN
                        CALL GenerateChildUniqueID(@new_id);
                        SET NEW.child_id = @new_id;
                    END IF;
                    
                    -- Set gender text
                    CALL SetGenderText(NEW.gender, gender_text_val);
                    SET NEW.gender_text = gender_text_val;
                END
                """
                conn.execute(text(before_insert_trigger))
                
                # Create before update trigger for children
                before_update_trigger = """
                CREATE TRIGGER before_update_children
                BEFORE UPDATE ON Children
                FOR EACH ROW
                BEGIN
                    DECLARE gender_text_val VARCHAR(20);
                    
                    -- Update gender text if gender changed
                    IF NEW.gender != OLD.gender THEN
                        CALL SetGenderText(NEW.gender, gender_text_val);
                        SET NEW.gender_text = gender_text_val;
                    END IF;
                END
                """
                conn.execute(text(before_update_trigger))
                
                trans.commit()
                return True
            except Exception as e:
                trans.rollback()
                raise e
    except Exception as e:
        print(f"Error setting up stored procedures and triggers: {e}")
        return False

def load_initial_data():
    try:
        # Get the path to the data directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_file = os.path.join(current_dir, 'data', 'stunting_wasting_dataset.csv')
        
        # Load the dataset
        df = pd.read_csv(data_file)
        
        with engine.connect() as conn:
            # Check if we have any existing children
            result = conn.execute(text("SELECT COUNT(*) FROM children")).scalar()
            if result > 0:
                print("Children table already has data, skipping initial load")
                return True
            
            # Limit to maximum 500 rows
            max_rows = min(500, len(df))
            df = df.head(max_rows)
            
            print(f"Loading {len(df)} records in batches of 100...")
            
            # Process in batches of 100
            batch_size = 100
            total_processed = 0
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                print(f"Processing batch {batch_num} ({len(batch)} records)...")
                
                with engine.begin() as batch_conn:
                    for _, row in batch.iterrows():
                        try:
                            # Insert child record
                            child_stmt = text("""
                                INSERT INTO children (gender, current_stunting_status, current_wasting_status)
                                VALUES (:gender, NULL, NULL)
                            """)
                            batch_conn.execute(child_stmt, {
                                'gender': row['gender']
                            })
                            
                            # Get the generated child_id
                            child_id_stmt = text("SELECT child_id FROM children WHERE child_id = (SELECT MAX(child_id) FROM children)")
                            child_id = batch_conn.execute(child_id_stmt).scalar()
                            
                            # Insert measurement record
                            meas_stmt = text("""
                                INSERT INTO measurements 
                                (child_id, age_months, body_length_cm, body_weight_kg, measurement_date)
                                VALUES (:child_id, :age, :length, :weight, :date)
                            """)
                            batch_conn.execute(meas_stmt, {
                                'child_id': child_id,
                                'age': row['age_months'],
                                'length': row['body_length_cm'],
                                'weight': row['body_weight_kg'],
                                'date': datetime.now().date()
                            })
                            
                            # Get the measurement_id
                            meas_id_stmt = text("SELECT measurement_id FROM measurements WHERE measurement_id = (SELECT MAX(measurement_id) FROM measurements)")
                            meas_id = batch_conn.execute(meas_id_stmt).scalar()
                            
                            # Insert diagnosis record
                            diag_stmt = text("""
                                INSERT INTO diagnosis 
                                (measurement_id, stunting_status, wasting_status, diagnosis_date)
                                VALUES (:measurement_id, :stunting, :wasting, :date)
                            """)
                            batch_conn.execute(diag_stmt, {
                                'measurement_id': meas_id,
                                'stunting': row['stunting_status'],
                                'wasting': row['wasting_status'],
                                'date': datetime.now().date()
                            })
                            
                            total_processed += 1
                            
                        except Exception as e:
                            print(f"Error processing record {row.name}: {e}")
                            continue
                
                print(f"Batch {batch_num} completed. Total processed: {total_processed}")
            
            print(f"Data loading completed. Total records processed: {total_processed}")
            return True
            
    except Exception as e:
        print(f"Error loading initial data: {e}")
        return False

# Initialize database
def init_db():
    try:
        print("Starting database initialization...")
        # Create database if it doesn't exist
        engine_root = create_engine("mysql+pymysql://root:00990099@localhost:3306")
        print("Created root engine...")
        
        with engine_root.connect() as conn:
            print("Connected to MySQL...")
            conn.execute(text("CREATE DATABASE IF NOT EXISTS malnutrition;"))
            conn.execute(text("USE malnutrition;"))
            print("Created and selected database...")
            trans = conn.begin()
            try:
                trans.commit()
                print("Initial transaction committed...")
            except:
                trans.rollback()
                raise
            
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created...")
        
        # Set up stored procedures and triggers
        print("Setting up stored procedures and triggers...")
        if not setup_stored_procedures_and_triggers():
            raise Exception("Failed to set up stored procedures and triggers")
        print("Stored procedures and triggers set up...")
        
        # Check if database is empty and load initial data if needed
        with engine.connect() as conn:
            print("Checking if data needs to be loaded...")
            result = conn.execute(text("SELECT COUNT(*) FROM children"))
            count = result.scalar()
            if count == 0:
                print("Loading initial data...")
                if not load_initial_data():
                    raise Exception("Failed to load initial data")
                print("Initial data loaded successfully...")
            else:
                print("Data already exists, skipping initial load...")
        
        print("Database initialization completed successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
