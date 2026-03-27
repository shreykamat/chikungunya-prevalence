# Exploratory Data Analysis for Chikungunya Prevalence

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dateutil.parser import parse
import warnings

warnings.filterwarnings('ignore')

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / 'data' / 'prevalence_of_chikungunya.csv'
OUTPUT_DIR = REPO_ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)


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

    # Split semicolon-separated fields
    list_cols = ['presenting_symptoms', 'comorbidities', 'complications', 'diagnostic_test', 'coinfections']
    for col in list_cols:
        if col in df.columns:
            df[col] = df[col].str.split(';')
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
    return df


# Correlation

def create_correlation_matrix(df):
    """Create and save correlation matrix for numeric features."""
    # Select numeric columns
    numeric_cols = ['age', 'pulse', 'systolic_bp', 'diastolic_bp', 'spo2', 'respiratory_rate']
    
    # Add binary outcomes for correlation
    df['mortality_binary'] = df['mortality'].str.lower().eq('yes').fillna(False).astype(int)
    df['icu_binary'] = df['icu_admission'].str.lower().eq('yes').fillna(False).astype(int)
    
    # Combine
    corr_cols = numeric_cols + ['mortality_binary', 'icu_binary']
    corr_df = df[corr_cols].dropna()
    
    if corr_df.empty:
        print("No data for correlation matrix.")
        return
    
    # Compute correlation
    corr_matrix = corr_df.corr()
    
    # Plot heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
    plt.title('Correlation Matrix: Numeric Features vs Outcomes')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'correlation_matrix.png')
    plt.close()
    
    # Save to CSV
    corr_matrix.to_csv(OUTPUT_DIR / 'correlation_matrix.csv')
    
    print("Correlation matrix saved to outputs/correlation_matrix.png and .csv")
    
    

def calculate_prevalence(df):
    """Calculate prevalence metrics."""
    results = {}
    
    # Overall
    results['total_cases'] = len(df)
    results['overall_prevalence'] = 1.0  # All are cases
    
    # By sex
    sex_counts = df['sex'].value_counts()
    results['sex_prevalence'] = (sex_counts / len(df)).to_dict()
    
    # By residence
    residence_counts = df['residence'].value_counts()
    results['residence_prevalence'] = (residence_counts / len(df)).to_dict()
    
    # By age groups
    df['age_group'] = pd.cut(df['age'], bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 100], labels=['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81+'])
    age_counts = df['age_group'].value_counts()
    results['age_group_prevalence'] = (age_counts / len(df)).to_dict()
    
    # By comorbidity
    comorbidity_counts = df['comorbidities'].explode().value_counts()
    results['comorbidity_prevalence'] = (comorbidity_counts / len(df)).to_dict()
    
    # By complications
    complication_counts = df['complications'].explode().value_counts()
    results['complication_prevalence'] = (complication_counts / len(df)).to_dict()
    
    # Time-based incidence (by month)
    df['onset_month'] = df['onset_date'].dt.to_period('M')
    monthly_counts = df.groupby('onset_month').size()
    results['monthly_incidence'] = monthly_counts.to_dict()
    
    # Save to CSV
    pd.DataFrame.from_dict(results, orient='index').to_csv(OUTPUT_DIR / 'prevalence_summary.csv')
    
    print("Prevalence calculations saved to outputs/prevalence_summary.csv")
    return results


def create_plots(df):
    # Figure 1: Age distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['age'], bins=20, kde=True)
    plt.title('Age Distribution of Chikungunya Patients')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.savefig(OUTPUT_DIR / 'age_distribution.png')
    plt.close()

    # Figure 2: Sex distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['sex'])
    plt.title('Sex Distribution of Chikungunya Patients')
    plt.xlabel('Sex')
    plt.ylabel('Frequency')
    plt.savefig(OUTPUT_DIR / 'sex_distribution.png')
    plt.close()


def main():
    df = load_data()
    df = clean_data(df)

    create_correlation_matrix(df)
    create_plots(df)
    prevalence_results = calculate_prevalence(df)
    print('Prevalence results: ', prevalence_results)


if __name__ == '__main__':
    main()
