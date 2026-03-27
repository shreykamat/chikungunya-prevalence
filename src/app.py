import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


st.set_page_config(page_title='Chikungunya Prevalence', layout='wide')
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_csv(filename):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        st.warning(f"Missing outputs/{filename}. Run the pipeline first.")
        return None
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        st.warning(f"outputs/{filename} exists but is empty.")
        return None

    if df.empty:
        st.info(f"outputs/{filename} has no rows to display.")
        return None

    return df


# Title and description
st.title('Chikungunya Prevalence Analysis')
st.markdown('Interactive analysis of chikungunya cases, complications and outcomes')

# Sidebar for navigation
st.sidebar.header("Select Section")
section = st.sidebar.radio('Choose a view:', ["Overview", "Age & Sex", "Length of Patient Stay", "Comorbidities", "Timeline", "Symptoms", "Diagnostics"])

# Load data based on section
if section == "Overview":
    st.header("Overall Prevalence Metrics")    
    st.markdown("This section provides key summary statistics on Chikungunya prevalence, including total cases, mortality rates, ICU admissions, and average hospital stays, offering a high-level overview of the outbreak's impact.")    
    st.markdown("Key statistics")
    overall = load_csv('overall_prevalence.csv')
    if overall is not None:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Cases", overall['total_cases'][0])
        #col2.metric("Complication Rate", f"{overall['complication_rate'][0]}%")
        col2.metric("Mortality Rate", f"{overall['mortality_rate'][0]}%")
        col3.metric("ICU Admission Rate", f"{overall['icu_admission_rate'][0]}%")
        col4.metric("Avg Onset to Admission (days)", overall['avg_onset_to_admission'][0])
        col5.metric("Avg Length of Stay (days)", overall['avg_length_of_stay'][0])
    
    

elif section == "Age & Sex":
    st.header("Age-Sex Distribution")
    st.markdown("This section analyzes the distribution of Chikungunya cases by age group and sex, highlighting demographic patterns in infection rates and helping identify vulnerable populations.")
    age_sex = load_csv('age_sex_breakdown.csv')
    if age_sex is not None:
        fig = px.bar(age_sex, x='age_group', y='count', color='sex', barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(age_sex)
    
elif section == "Length of Patient Stay":
    st.header("Length of Patient Stay by Age Group")
    st.markdown("This section examines average hospital stay durations across age groups and sexes, revealing trends in recovery times and resource utilization for different demographics.")
    age_sex = load_csv('age_sex_breakdown.csv')
    if age_sex is not None:
        fig = px.bar(age_sex, x='age_group', y='avg_length_of_stay', color='sex', barmode='group',
                     labels={'avg_length_of_stay':'Avg Length of Stay (days)'})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(age_sex[['age_group', 'sex', 'avg_length_of_stay']])       

elif section == "Comorbidities":
    st.header("Comorbidity Risk Analysis")
    st.markdown("This section identifies the most common comorbidities among Chikungunya patients, quantifying their frequency to assess risks and inform targeted prevention strategies.")
    df = load_csv('comorbidity_risk.csv')
    if df is not None and not df.empty:
        fig = px.bar(df.head(15).sort_values('count', ascending=False),
                     x='comorbidity', y='count', color='count',
                     color_continuous_scale='Reds', labels={'comorbidity':'Comorbidity'})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

elif section == "Timeline":
    st.header("Cases Over Time")
    st.markdown("This section tracks weekly Chikungunya case counts, ICU admission rates, and mortality rates over time, illustrating the outbreak's progression and temporal patterns.")
    df = load_csv('weekly_incidence.csv')
    if df is not None and not df.empty:
        df['week_start'] = pd.to_datetime(df['week_start']).dt.date
        
        # Create the bar chart as the base figure
        fig = px.bar(df, x='week_start', y='cases', labels={'cases': 'Weekly Cases', 'week_start': 'Week'})
        
        # Display the combined chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Keep the dataframe display below the chart
        st.dataframe(df)

elif section == "Symptoms":
    st.header("Presenting Symptoms Frequency")
    st.markdown("This section lists the most frequent presenting symptoms in Chikungunya cases, providing insights into common clinical manifestations and diagnostic priorities.")
    df = load_csv('presenting_symptoms.csv')
    if df is not None and not df.empty:
        fig = px.bar(df.head(25).sort_values('frequency', ascending=False), x='symptom', y='frequency')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

elif section == "Diagnostics":
    st.header("Diagnostic Test Distribution")
    st.markdown("This section shows the distribution of diagnostic tests used, highlighting prevalent testing methods and their shares in confirming Chikungunya diagnoses.")
    df = load_csv('diagnostic_tests.csv')
    if df is not None and not df.empty:
        fig = px.pie(df.head(15), names='test_type', values='frequency',
                     title='Diagnostic Test Shares')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

        
