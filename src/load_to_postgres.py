import os
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dateutil.parser import parse

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / 'data' / 'prevalence_of_chikungunya.csv'
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/chikungunya_db')


# Load the dataset
def load_data():
    df = pd.read_csv(DATA_PATH, encoding='UTF-8')
    print(f'Dataset shape: {df.shape}')
    print(f'Dataset columns: {df.columns.tolist()}')
    print(df.head())
    return df

# Flexible date parsing function
def parse_flexible_date(date_str):
    if pd.isna(date_str):
        return pd.NaT
    try:
        # Use dateutil for flexible parsing, with dayfirst for dd/mm format
        return pd.to_datetime(parse(str(date_str), dayfirst=True))
    except:
        return pd.NaT

# Split columns for blood pressure and semicolon-separated lists
def split_columns(df):
    # Split blood pressure
    if 'blood_pressure' in df.columns:
        bp_split = df['blood_pressure'].str.split('/', expand=True).astype(float)
        df['systolic_bp'] = bp_split[0]
        df['diastolic_bp'] = bp_split[1]

    # Keep list-like text columns as strings for PostgreSQL string_to_array queries.
    return df

# Clean the dataset
def clean_data(df):
    df.columns = df.columns.str.lower().str.replace(' ','_')
    df.columns = df.columns.str.replace('[^a-zA-Z0-9_]','', regex=True)
    df.replace(['-', ''], np.nan, inplace=True)
    
    # Converting numerics
    numeric_cols = ['age', 'onset_to_admission_duration_in_days', 'number_of_joints', 'pulse', 'spo2', 'respiratory_rate', 'length_of_stay']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Apply the flexible date parser to the relevant columns
    df['onset_date'] = df['onset_date'].apply(parse_flexible_date)
    # Split columns
    split_columns(df)
    
    # Add binary outcomes for correlation
    df['mortality_binary'] = df['mortality'].str.lower().eq('yes').fillna(False).astype(int)
    df['icu_binary'] = df['icu_admission'].str.lower().eq('yes').fillna(False).astype(int)
    
    return df


def main():
    engine = create_engine(DATABASE_URL)
    df = load_data()
    df = clean_data(df)
    df.to_sql('chikungunya_cases', engine, if_exists='replace', index=False)
    print(f"Loaded {len(df)} rows into chikungunya_db.chikungunya_cases")


if __name__ == '__main__':
    main()



