import os
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/chikungunya_db')

# Query names matching the SQL file order (12 total)
query_names = [
    'overall_prevalence',
    'age_sex_breakdown',
    'comorbidity_risk',
    'complication_frequency',
    'weekly_incidence',
    'icu_mortality_by_age',
    'residence_pattern',
    'treatment_outcomes',
    'functional_status',
    'resource_utilization',
    'presenting_symptoms',
    'diagnostic_tests'
]

def load_queries():
    sql_file = Path(__file__).parent / 'sql_queries.sql'
    with open(sql_file, 'r') as f:
        sql_content = f.read()

    query_blocks = re.split(r'(?=-- \d+\.)', sql_content)

    queries = []
    for block in query_blocks:
        lines = block.split('\n')
        query_lines = [line for line in lines if not line.strip().startswith('--')]
        query_text = '\n'.join(query_lines).strip()
        if query_text:
            queries.append(query_text)

    if len(queries) != len(query_names):
        raise ValueError(
            f"Expected {len(query_names)} queries but found {len(queries)} in sql_queries.sql."
        )

    return queries


def main():
    engine = create_engine(DATABASE_URL)
    queries = load_queries()

    print(f"Found {len(queries)} queries to execute\n")
    try:
        for i, (query, name) in enumerate(zip(queries, query_names), 1):
            if query.strip():
                try:
                    df = pd.read_sql(query, engine)
                    csv_path = OUTPUT_DIR / f'{name}.csv'
                    df.to_csv(csv_path, index=False)
                    print(f"✓ [{i:2d}] {name}.csv saved ({len(df)} rows)")
                except Exception as e:
                    print(f"✗ [{i:2d}] {name}: {str(e)[:100]}")
            else:
                print(f"⊘ [{i:2d}] Skipped - empty query")
    finally:
        engine.dispose()

    print("\n✅ Query execution complete!")


if __name__ == '__main__':
    main()
