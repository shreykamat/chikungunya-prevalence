# Chikungunya Prevalence Analysis

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](#requirements)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)](#run-the-streamlit-app)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)](#database-setup)

This project analyzes chikungunya case data and presents the results in a Streamlit dashboard.

A small end-to-end data project that takes raw chikungunya case records, prepares them for analysis, generates SQL-based summary outputs, and presents the results in an interactive dashboard.

## Live App

Streamlit app link:

```text
https://your-app-name.streamlit.app
```

## Highlights

- End-to-end workflow from raw CSV to dashboard
- PostgreSQL-backed analytical pipeline
- Streamlit app for interactive exploration
- Automated generation of reusable CSV outputs
- Exploratory analysis with summary visualizations

## Overview

The project combines:

- a raw clinical dataset
- a local PostgreSQL loading step
- SQL-based analytical outputs
- exploratory visual analysis
- a Streamlit dashboard for interactive reporting

The dashboard highlights summary prevalence metrics, demographic patterns, hospital stay trends, comorbidity burden, time-based case trends, symptom frequency, and diagnostic test distribution.

## Features

- Prevalence summary metrics for total cases, mortality, ICU admission, and hospital stay
- Demographic analysis by age group and sex
- Length-of-stay comparisons across groups
- Comorbidity frequency reporting
- Weekly incidence trend analysis
- Symptom frequency exploration
- Diagnostic test distribution visualization

## Tech Stack

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Streamlit
- Plotly
- Matplotlib
- Seaborn

## Project Structure

- `data/prevalence_of_chikungunya.csv`: Raw dataset
- `src/load_to_postgres.py`: Cleans the raw data and loads it into PostgreSQL
- `src/sql_queries.sql`: SQL queries used to generate analysis outputs
- `src/run_queries.py`: Runs SQL queries and writes output CSVs to `outputs/`
- `src/eda.py`: Generates exploratory analysis outputs and plots
- `src/app.py`: Streamlit dashboard
- `outputs/`: Generated CSVs and plots used by the app

## Requirements

- Python 3.9+
- PostgreSQL
- Packages listed in `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Setup

The data-loading and query scripts use PostgreSQL through `DATABASE_URL`.

Default:

```bash
postgresql://localhost:5432/chikungunya_db
```

If needed, set your own connection string before running the scripts:

```bash
export DATABASE_URL='postgresql://username:password@localhost:5432/chikungunya_db'
```

## Run the Pipeline

From the project root:

```bash
python src/load_to_postgres.py
python src/run_queries.py
python src/eda.py
```

This will populate the root `outputs/` folder with generated CSVs and plots.

## Run the Streamlit App

```bash
streamlit run src/app.py
```

## Dashboard Sections

The Streamlit app currently includes:

- Overview
- Age & Sex
- Length of Patient Stay
- Comorbidities
- Timeline
- Symptoms
- Diagnostics

## Expected Output Files

The app depends on generated files in `outputs/`, including:

- `overall_prevalence.csv`
- `age_sex_breakdown.csv`
- `comorbidity_risk.csv`
- `weekly_incidence.csv`
- `presenting_symptoms.csv`
- `diagnostic_tests.csv`

If these files are missing, the app will show warnings instead of crashing.

## Results and Screenshots

You can include screenshots of the dashboard here after deployment or local execution.

Suggested screenshots:

- Overview metrics page
- Age and sex distribution chart
- Weekly incidence timeline
- Symptoms frequency chart

If you want to add images later, place them in a folder like `assets/` and reference them here with Markdown:

```md
![Overview Dashboard](assets/overview.png)
```

Suggested layout if you add screenshots:

```md
### Overview
![Overview Dashboard](assets/overview.png)

### Demographics
![Age and Sex Distribution](assets/age-sex.png)

### Timeline
![Weekly Incidence](assets/timeline.png)
```

## Streamlit Community Cloud Deployment

To deploy on Streamlit Community Cloud:

1. Generate the output CSVs locally.
2. Make sure the required `outputs/*.csv` files are present in the repository.
3. Push the repository to GitHub.
4. In Streamlit Community Cloud, set the main file path to:

```text
src/app.py
```

Notes:

- `requirements.txt` must be in the repo root.
- The deployed app does not create PostgreSQL outputs on its own.
- Since the app reads pre-generated CSVs, those files need to be committed before deployment.

## Notes

- The app reads output files from the repo-root `outputs/` directory.
- The ETL and query scripts are designed for local execution.
- `notebooks/outputs/` contains older notebook artifacts and is separate from the app's runtime `outputs/` folder.
