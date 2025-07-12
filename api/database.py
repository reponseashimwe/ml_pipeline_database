from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql
import pandas as pd
import os
from datetime import datetime

# Database connection configuration
DATABASE_URL = "mysql+pymysql://root:00990099@localhost:3306/malnutrition_db"

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
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_dir = os.path.join(current_dir, 'sql')
        
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # First drop existing procedures and triggers
                drop_statements = [
                    "DROP PROCEDURE IF EXISTS GenerateChildUniqueID",
                    "DROP TRIGGER IF EXISTS before_insert_children_set_id",
                    "DROP TRIGGER IF EXISTS after_diagnosis_insert_update_child_status"
                ]
                
                for stmt in drop_statements:
                    conn.execute(text(stmt))
                
                # Create stored procedure with microsecond precision for uniqueness
                stored_proc = """
                CREATE PROCEDURE GenerateChildUniqueID(OUT generated_id VARCHAR(20))
                BEGIN
                    DECLARE micro_time VARCHAR(6);
                    SELECT SUBSTRING(MICROSECOND(NOW(6)), 1, 6) INTO micro_time;
                    
                    SET generated_id := CONCAT(
                        DATE_FORMAT(CURDATE(), '%Y%m'),
                        '-',
                        UPPER(
                            SUBSTRING(
                                MD5(CONCAT(RAND(), micro_time, UUID())),
                                1, 6
                            )
                        )
                    );
                END
                """
                conn.execute(text(stored_proc))
                
                # Create before insert trigger
                before_trigger = """
                CREATE TRIGGER before_insert_children_set_id
                BEFORE INSERT ON Children
                FOR EACH ROW
                BEGIN
                    IF NEW.child_id IS NULL OR NEW.child_id = '' THEN
                        CALL GenerateChildUniqueID(@new_id);
                        SET NEW.child_id = @new_id;
                    END IF;
                END
                """
                conn.execute(text(before_trigger))
                
                # Create after insert trigger
                after_trigger = """
                CREATE TRIGGER after_diagnosis_insert_update_child_status
                AFTER INSERT ON Diagnosis
                FOR EACH ROW
                BEGIN
                    DECLARE v_child_id VARCHAR(20);
                    SELECT child_id INTO v_child_id FROM Measurements WHERE measurement_id = NEW.measurement_id;
                    UPDATE Children
                    SET current_stunting_status = NEW.stunting_status,
                        current_wasting_status = NEW.wasting_status
                    WHERE child_id = v_child_id;
                END
                """
                conn.execute(text(after_trigger))
                
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
        data_dir = os.path.join(current_dir, 'data')
        
        # Load all CSV files once
        children_df = pd.read_csv(os.path.join(data_dir, 'children.csv'))
        measurements_df = pd.read_csv(os.path.join(data_dir, 'measurements.csv'))
        diagnosis_df = pd.read_csv(os.path.join(data_dir, 'diagnosis.csv'))
        
        with engine.connect() as conn:
            # Check if we have any existing children
            result = conn.execute(text("SELECT COUNT(*) FROM children")).scalar()
            if result > 0:
                print("Children table already has data, skipping initial load")
                return True
            
            # Limit to maximum 500 rows
            max_rows = min(500, len(children_df))
            children_df = children_df.head(max_rows)
            
            print(f"Loading {len(children_df)} children records in batches of 100...")
            
            # Process in batches of 100
            batch_size = 100
            total_processed = 0
            
            for i in range(0, len(children_df), batch_size):
                batch = children_df.iloc[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                print(f"Processing batch {batch_num} ({len(batch)} records)...")
                
                with engine.begin() as batch_conn:
                    for _, child_row in batch.iterrows():
                        try:
                            # Insert child record
                            child_stmt = text("""
                                INSERT INTO children (gender, current_stunting_status, current_wasting_status)
                                VALUES (:gender, :stunting, :wasting)
                            """)
                            batch_conn.execute(child_stmt, {
                                'gender': child_row['gender'],
                                'stunting': child_row.get('current_stunting_status', None),
                                'wasting': child_row.get('current_wasting_status', None)
                            })
                            
                            # Get the generated child_id for this record
                            child_id_stmt = text("SELECT child_id FROM children WHERE child_id = (SELECT MAX(child_id) FROM children)")
                            child_id = batch_conn.execute(child_id_stmt).scalar()
                            
                            # Find corresponding measurements for this child
                            child_measurements = measurements_df[measurements_df['child_id'] == child_row.name]
                            
                            for _, meas_row in child_measurements.iterrows():
                                # Insert measurement record
                                meas_stmt = text("""
                                    INSERT INTO measurements 
                                    (child_id, age_months, body_length_cm, body_weight_kg, measurement_date)
                                    VALUES (:child_id, :age, :length, :weight, :date)
                                """)
                                batch_conn.execute(meas_stmt, {
                                    'child_id': child_id,
                                    'age': meas_row['age_months'],
                                    'length': meas_row['body_length_cm'],
                                    'weight': meas_row['body_weight_kg'],
                                    'date': datetime.now().date()
                                })
                                
                                # Get the measurement_id
                                meas_id_stmt = text("SELECT measurement_id FROM measurements WHERE measurement_id = (SELECT MAX(measurement_id) FROM measurements)")
                                meas_id = batch_conn.execute(meas_id_stmt).scalar()
                                
                                # Find corresponding diagnosis for this measurement
                                meas_diagnosis = diagnosis_df[diagnosis_df['measurement_id'] == meas_row.name]
                                
                                for _, diag_row in meas_diagnosis.iterrows():
                                    # Insert diagnosis record
                                    diag_stmt = text("""
                                        INSERT INTO diagnosis 
                                        (measurement_id, stunting_status, wasting_status, diagnosis_date)
                                        VALUES (:measurement_id, :stunting, :wasting, :date)
                                    """)
                                    batch_conn.execute(diag_stmt, {
                                        'measurement_id': meas_id,
                                        'stunting': diag_row['stunting_status'],
                                        'wasting': diag_row['wasting_status'],
                                        'date': datetime.now().date()
                                    })
                            
                            total_processed += 1
                            
                        except Exception as e:
                            print(f"Error processing child record {child_row.name}: {e}")
                            continue
                
                print(f"Batch {batch_num} completed. Total processed: {total_processed}")
            
            print(f"Data loading completed. Total children processed: {total_processed}")
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
            conn.execute(text("CREATE DATABASE IF NOT EXISTS malnutrition_db;"))
            conn.execute(text("USE malnutrition_db;"))
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
