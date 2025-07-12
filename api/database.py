from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
from datetime import datetime
from enum import Enum
import dotenv

# Load environment variables
dotenv.load_dotenv()

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
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

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

def load_sql_file(filepath):
    """Helper function to read SQL file content"""
    with open(filepath, 'r') as f:
        return f.read()

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
                
                # Get SQL directory path
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sql_dir = os.path.join(current_dir, 'sql')
                
                # Load and execute stored procedures
                procedures = [
                    '01-procedure-generate_child_id.sql',
                    '02-procedure-set_gender_text.sql'
                ]
                for proc in procedures:
                    sql = load_sql_file(os.path.join(sql_dir, proc))
                    conn.execute(text(sql))
                    print(f"Created procedure from {proc}")
                
                # Load and execute triggers
                triggers = [
                    '03-trigger-before_insert_children.sql',
                    '04-trigger-before_update_children.sql'
                ]
                for trig in triggers:
                    sql = load_sql_file(os.path.join(sql_dir, trig))
                    conn.execute(text(sql))
                    print(f"Created trigger from {trig}")
                
                trans.commit()
                return True
            except Exception as e:
                trans.rollback()
                print(f"Error setting up stored procedures and triggers: {e}")
                return False
    except Exception as e:
        print(f"Error connecting to database: {e}")
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
            result = conn.execute(text('SELECT COUNT(*) FROM children')).scalar()
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
            current_time = datetime.utcnow()
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                print(f"Processing batch {batch_num} ({len(batch)} records)...")
                
                with engine.begin() as batch_conn:
                    for _, row in batch.iterrows():
                        try:
                            # Insert child record
                            child_stmt = text("""
                                INSERT INTO children 
                                (gender, current_stunting_status, current_wasting_status, created_at, updated_at)
                                VALUES (:gender, :stunting, :wasting, :created_at, :updated_at)
                            """)
                            batch_conn.execute(child_stmt, {
                                'gender': row['Jenis Kelamin'],
                                'stunting': row['Stunting'],
                                'wasting': row['Wasting'],
                                'created_at': current_time,
                                'updated_at': current_time
                            })
                            
                            # Get the generated child_id
                            child_id_stmt = text("SELECT child_id FROM children WHERE child_id = (SELECT MAX(child_id) FROM children)")
                            child_id = batch_conn.execute(child_id_stmt).scalar()
                            
                            # Insert measurement record
                            measurement_date = datetime.now().date()
                            meas_stmt = text("""
                                INSERT INTO measurements 
                                (child_id, age_months, body_length_cm, body_weight_kg, measurement_date, created_at, updated_at)
                                VALUES (:child_id, :age, :length, :weight, :meas_date, :created_at, :updated_at)
                            """)
                            batch_conn.execute(meas_stmt, {
                                'child_id': child_id,
                                'age': row['Umur (bulan)'],
                                'length': row['Tinggi Badan (cm)'],
                                'weight': row['Berat Badan (kg)'],
                                'meas_date': measurement_date,
                                'created_at': current_time,
                                'updated_at': current_time
                            })
                            
                            # Get the measurement_id
                            meas_id_stmt = text("SELECT measurement_id FROM measurements WHERE measurement_id = (SELECT MAX(measurement_id) FROM measurements)")
                            meas_id = batch_conn.execute(meas_id_stmt).scalar()
                            
                            # Insert diagnosis record
                            diag_stmt = text("""
                                INSERT INTO diagnosis 
                                (measurement_id, stunting_status, wasting_status, diagnosis_date, created_at, updated_at)
                                VALUES (:measurement_id, :stunting, :wasting, :diag_date, :created_at, :updated_at)
                            """)
                            batch_conn.execute(diag_stmt, {
                                'measurement_id': meas_id,
                                'stunting': row['Stunting'],
                                'wasting': row['Wasting'],
                                'diag_date': measurement_date,
                                'created_at': current_time,
                                'updated_at': current_time
                            })
                            
                            total_processed += 1
                            print(f"Successfully processed record {total_processed}")
                            
                        except Exception as e:
                            print(f"Error processing record {row.name}: {str(e)}")
                            continue
                
                print(f"Batch {batch_num} completed. Total processed: {total_processed}")
            
            print(f"Data loading completed. Total records processed: {total_processed}")
            return True
            
    except Exception as e:
        print(f"Error loading initial data: {e}")
        return False

# Initialize database
def init_db():
    print("--- Starting database initialization ---", file=sys.stderr)
    try:
        # --- Step 1: Create Tables ---
        print("Attempting to create tables...", file=sys.stderr)
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Failed during table creation: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr) # Print full traceback
            return False # Exit early on this critical failure

        # --- Step 2: Set up Stored Procedures and Triggers ---
        print("Attempting to set up stored procedures and triggers...", file=sys.stderr)
        try:
            # You need to pass 'engine' or get a new connection here if setup_stored_procedures_and_triggers needs it
            # Assuming setup_stored_procedures_and_triggers() is defined elsewhere and uses 'engine'
            if not setup_stored_procedures_and_triggers():
                raise Exception("setup_stored_procedures_and_triggers returned False")
            print("Stored procedures and triggers set up successfully.", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Failed during procedures/triggers setup: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr) # Print full traceback
            return False # Exit early

        # --- Step 3: Check and Load Initial Data ---
        print("Checking if data needs to be loaded...", file=sys.stderr)
        try:
            with engine.connect() as conn:
                # IMPORTANT: Ensure 'Children' matches the actual table name casing on Railway
                # Based on your 'SHOW TABLES' output, it's 'Children' (initial capital)
                result = conn.execute(text("SELECT COUNT(*) FROM Children"))
                count = result.scalar()
                print(f"Current Children table row count: {count}", file=sys.stderr)

                if count == 0:
                    print("Loading initial data...", file=sys.stderr)
                    # You need to pass 'db' and 'csv_path' to load_stunting_wasting_dataset
                    # db = next(get_db()) # This is usually done in startup_event, not init_db
                    # You need to ensure csv_path is accessible on Render's filesystem
                    # current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    # csv_path = os.path.join(current_dir, 'data', 'stunting_wasting_dataset.csv')
                    # if not crud.load_stunting_wasting_dataset(db, csv_path):
                    #     raise Exception("Failed to load initial data")
                    
                    # For now, let's simplify this part for debugging startup
                    # If load_stunting_wasting_dataset is the issue, we'll get there.
                    # Temporarily, you might comment out the actual data loading for startup debug.
                    print("Initial data loading logic skipped for debug (if not already commented).", file=sys.stderr)
                    # If you want to keep it, ensure crud.load_stunting_wasting_dataset is robust.
                    # For the sake of getting the app to start, you might temporarily return True here
                    # or comment out the actual load call if it's complex.
                else:
                    print("Data already exists, skipping initial load.", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Failed during data load check or initial data load: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr) # Print full traceback
            return False # Exit early

        print("--- Database initialization completed successfully! ---", file=sys.stderr)
        return True
    except Exception as e:
        # This catch-all should ideally not be hit if inner blocks are handled,
        # but it's a fallback.
        print(f"CRITICAL UNEXPECTED ERROR IN init_db: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr) # Print full traceback
        return False
