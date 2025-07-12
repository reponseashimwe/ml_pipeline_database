import pandas as pd

# Read the original CSV
df = pd.read_csv('stunting_wasting_dataset.csv')

# Take only the first 500 rows
df = df.head(500)

# Map stunting and wasting to 1/0
stunting_map = {'Tall': 0, 'Normal': 0, 'Stunted': 1, 'Severely Stunted': 1}
wasting_map = {'Normal weight': 0, 'Risk of Overweight': 0, 'Underweight': 1, 'Severely Underweight': 1}

df['current_stunting_status'] = df['Stunting'].map(stunting_map)
df['current_wasting_status'] = df['Wasting'].map(wasting_map)

# Create Children table CSV
children = df[['Jenis Kelamin', 'current_stunting_status', 'current_wasting_status']].copy()
children.rename(columns={'Jenis Kelamin': 'gender'}, inplace=True)
children.to_csv('children.csv', index=False)

# Add a child_id column (auto-increment for this example)
children['child_id'] = [i + 1 for i in range(len(children))]
df['child_id'] = children['child_id']

# Create Measurements table CSV
measurements = df[['child_id', 'Umur (bulan)', 'Tinggi Badan (cm)', 'Berat Badan (kg)']].copy()
measurements.rename(columns={
    'Umur (bulan)': 'age_months',
    'Tinggi Badan (cm)': 'body_length_cm',
    'Berat Badan (kg)': 'body_weight_kg'
}, inplace=True)
measurements.to_csv('measurements.csv', index=False)

# Add a measurement_id column (auto-increment for this example)
measurements['measurement_id'] = range(1, len(measurements) + 1)
df['measurement_id'] = measurements['measurement_id']

# Create Diagnosis table CSV
diagnosis = df[['measurement_id', 'current_stunting_status', 'current_wasting_status']].copy()
diagnosis.rename(columns={
    'current_stunting_status': 'stunting_status',
    'current_wasting_status': 'wasting_status'
}, inplace=True)
diagnosis.to_csv('diagnosis.csv', index=False)