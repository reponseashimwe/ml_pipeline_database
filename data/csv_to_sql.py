import pandas as pd

csv_file = 'diagnosis.csv'
table_name = 'Diagnosis'

# Read the CSV file
df = pd.read_csv(csv_file)

# Specify the columns to insert (exclude child_id)
columns = ['measurement_id', 'stunting_status', 'wasting_status']

with open('diagnosis.sql', 'w') as f:
    for _, row in df.iterrows():
        vals = [row[col] for col in columns]
        quoted = []
        for val in vals:
            # Quote strings, leave numbers unquoted
            if isinstance(val, str):
                quoted.append(f"'{val}'")
            else:
                quoted.append(str(val))
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(quoted)});\n"
        f.write(sql)