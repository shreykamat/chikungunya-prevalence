-- 1. OVERALL PREVALENCE
SELECT 
    COUNT(*) as total_cases,
    --ROUND(CAST(SUM(CASE WHEN complications IS NOT NULL THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(*) * 100, 2) as complication_rate,
    ROUND(CAST(SUM(mortality_binary) AS NUMERIC) / COUNT(*) * 100, 2) as mortality_rate,
    ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as icu_admission_rate,
        ROUND(CAST(AVG(onset_to_admission_duration_in_days) AS NUMERIC), 1) as avg_onset_to_admission,
    ROUND(CAST(AVG(length_of_stay) AS NUMERIC), 1) as avg_length_of_stay
FROM chikungunya_cases;

-- 2. AGE-SEX BREAKDOWN
SELECT 
    CASE 
        WHEN age < 11 THEN '0-10'
        WHEN age < 21 THEN '11-20'
        WHEN age < 31 THEN '21-30'
        WHEN age < 41 THEN '31-40'
        WHEN age < 51 THEN '41-50'
        WHEN age < 61 THEN '51-60'
        WHEN age < 71 THEN '61-70'
        WHEN age < 81 THEN '71-80'
        ELSE '81+'
    END as age_group,
    sex,
    COUNT(*) as count,
    --ROUND(CAST(SUM(CASE WHEN complications IS NOT NULL THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(*) * 100, 2) as complication_rate,
    --ROUND(CAST(SUM(mortality_binary) AS NUMERIC) / COUNT(*) * 100, 2) as mortality_rate,
    ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as icu_rate,
    ROUND(CAST(AVG(onset_to_admission_duration_in_days) AS NUMERIC), 1) as avg_onset_to_admission,
    ROUND(CAST(AVG(length_of_stay) AS NUMERIC), 1) as avg_length_of_stay
FROM chikungunya_cases
WHERE age IS NOT NULL AND sex IS NOT NULL
GROUP BY age_group, sex
ORDER BY age_group, sex;



-- 3. COMORBIDITY RISK
WITH comorb_unnested AS (
    SELECT 
        TRIM(unnest(string_to_array(comorbidities, ';'))) as comorbidity,
        CASE WHEN complications IS NOT NULL THEN 1 ELSE 0 END as has_complication,
        mortality_binary,
        icu_binary
    FROM chikungunya_cases
    WHERE comorbidities IS NOT NULL AND comorbidities != ''
)
SELECT 
    comorbidity,
    COUNT(*) as count,
    ROUND(CAST(SUM(mortality_binary) AS NUMERIC) / COUNT(*) * 100, 2) as mortality_rate,
    ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as icu_rate
FROM comorb_unnested
WHERE comorbidity != ''
GROUP BY comorbidity
ORDER BY count DESC;

-- 4. COMPLICATION FREQUENCY
WITH comp_unnested AS (
    SELECT TRIM(unnest(string_to_array(complications, ';'))) as complication
    FROM chikungunya_cases
    WHERE complications IS NOT NULL AND complications != ''
)
SELECT 
    complication,
    COUNT(*) as frequency,
    ROUND(CAST(COUNT(*) AS NUMERIC) / (SELECT COUNT(*) FROM chikungunya_cases) * 100, 2) as prevalence_pct
FROM comp_unnested
WHERE complication != ''
GROUP BY complication
ORDER BY frequency DESC;

-- 5. TIME-SERIES (WEEKLY INCIDENCE)
SELECT 
    DATE_TRUNC('week', onset_date)::DATE as week_start,
    COUNT(*) as cases,
    --ROUND(CAST(SUM(CASE WHEN complications IS NOT NULL THEN 1 ELSE 0 END) AS NUMERIC) / --COUNT(*) * 100, 2) as complication_rate,
    --ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as icu_rate,
    --ROUND(CAST(SUM(mortality_binary) AS NUMERIC) / COUNT(*) * 100, 2) as mortality_rate
FROM chikungunya_cases
WHERE onset_date IS NOT NULL
GROUP BY DATE_TRUNC('week', onset_date)
ORDER BY week_start;

-- 6. ICU & MORTALITY BY AGE GROUP
SELECT 
    CASE 
        WHEN age < 11 THEN '0-10'
        WHEN age < 21 THEN '11-20'
        WHEN age < 31 THEN '21-30'
        WHEN age < 41 THEN '31-40'
        WHEN age < 51 THEN '41-50'
        WHEN age < 61 THEN '51-60'
        WHEN age < 71 THEN '61-70'
        WHEN age < 81 THEN '71-80'
        ELSE '81+'
    END as age_group,
    COUNT(*) as total,
    ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as icu_rate,
    ROUND(CAST(SUM(mortality_binary) AS NUMERIC) / COUNT(*) * 100, 2) as mortality_rate
FROM chikungunya_cases
WHERE age IS NOT NULL
GROUP BY age_group
ORDER BY age_group;

-- 7. RESIDENCE PATTERN
SELECT 
    residence,
    COUNT(*) as count,
    ROUND(CAST(SUM(CASE WHEN complications IS NOT NULL THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(*) * 100, 2) as complication_rate,
    ROUND(CAST(SUM(mortality_binary) AS NUMERIC) / COUNT(*) * 100, 2) as mortality_rate,
    ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as icu_rate
FROM chikungunya_cases
WHERE residence IS NOT NULL AND residence != ''
GROUP BY residence
ORDER BY count DESC;

-- 8. TREATMENT OUTCOMES (BY SYSTEMIC STEROIDS)
SELECT 
    CASE WHEN systemic_steroids IS NOT NULL AND systemic_steroids != '' THEN 'With Steroids' ELSE 'No Steroids' END as steroid_status,
    COUNT(*) as count,
    ROUND(AVG(CAST(length_of_stay AS NUMERIC)), 1) as avg_los,
    ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as icu_rate,
    ROUND(CAST(SUM(mortality_binary) AS NUMERIC) / COUNT(*) * 100, 2) as mortality_rate
FROM chikungunya_cases
GROUP BY steroid_status;

-- 9. FUNCTIONAL STATUS AT DISCHARGE
SELECT 
    functional_status_at_discharge,
    COUNT(*) as count,
    ROUND(CAST(COUNT(*) AS NUMERIC) / (SELECT COUNT(*) FROM chikungunya_cases WHERE functional_status_at_discharge IS NOT NULL) * 100, 2) as percentage
FROM chikungunya_cases
WHERE functional_status_at_discharge IS NOT NULL AND functional_status_at_discharge != ''
GROUP BY functional_status_at_discharge
ORDER BY count DESC;

-- 10. RESOURCE UTILIZATION SUMMARY
SELECT 
    ROUND(CAST(SUM(icu_binary) AS NUMERIC) / COUNT(*) * 100, 2) as pct_icu,
    CAST(COUNT(CASE WHEN mechanical_ventilation ILIKE '%Yes%' THEN 1 END) AS INTEGER) as ventilation_count,
    CAST(COUNT(CASE WHEN inotropic_support ILIKE '%Yes%' THEN 1 END) AS INTEGER) as inotropic_count,
    CAST(COUNT(CASE WHEN renal_replacement_therapy ILIKE '%Yes%' THEN 1 END) AS INTEGER) as rrt_count,
    ROUND(AVG(CAST(length_of_stay AS NUMERIC)), 1) as avg_length_of_stay,
    CAST(COUNT(CASE WHEN readmission_within_30_days ILIKE '%Yes%' THEN 1 END) AS INTEGER) as readmit_30d_count
FROM chikungunya_cases;

-- 11. PRESENTING SYMPTOMS FREQUENCY
WITH symp_unnested AS (
    SELECT TRIM(unnest(string_to_array(presenting_symptoms, ';'))) as symptom
    FROM chikungunya_cases
    WHERE presenting_symptoms IS NOT NULL AND presenting_symptoms != ''
)
SELECT 
    symptom,
    COUNT(*) as frequency,
    ROUND(CAST(COUNT(*) AS NUMERIC) / (SELECT COUNT(*) FROM chikungunya_cases) * 100, 2) as prevalence_pct
FROM symp_unnested
WHERE symptom != ''
GROUP BY symptom
ORDER BY frequency DESC;

-- 12. DIAGNOSTIC TEST DISTRIBUTION
WITH diag_unnested AS (
    SELECT TRIM(unnest(string_to_array(diagnostic_test, ';'))) as test_type
    FROM chikungunya_cases
    WHERE diagnostic_test IS NOT NULL AND diagnostic_test != ''
)
SELECT 
    test_type,
    COUNT(*) as frequency,
    ROUND(CAST(COUNT(*) AS NUMERIC) / CAST((SELECT COUNT(DISTINCT diagnostic_test) FROM chikungunya_cases WHERE diagnostic_test IS NOT NULL) AS NUMERIC) * 100, 2) as prevalence_pct
FROM diag_unnested
WHERE test_type != ''
GROUP BY test_type
ORDER BY frequency DESC;