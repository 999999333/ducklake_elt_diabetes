{{ 
config(
    materialized='external',
    location='../lakehouse/export/diabetes_patients.csv',
    file_format='parquet')
}}

with diagnosis as (
    select *
    from {{ ref('dim_diagnosis') }}
),

bridge_patient_diagnosis as (
    select *
    from {{ ref('bridge_patient_visits_diagnosis') }}
),

patient_visit as (
    select *
    from {{ ref('fact_patient_visits') }}
),

discharge as (
    select *
    from {{ ref('dim_discharge_dispositions') }}
),

patients_with_diabetes as (
    select
        
        patient_visit.encounter_id,
        patient_visit.patient_id,
        patient_visit.age,
        diagnosis.diagnosis_name,
        diagnosis.diagnosis_key,
        patient_visit.time_in_hospital,
        discharge.description as discharge_disposition

    from diagnosis
    left join bridge_patient_diagnosis
        on diagnosis.diagnosis_id = bridge_patient_diagnosis.diagnosis_id
    left join patient_visit
        on bridge_patient_diagnosis.encounter_id = patient_visit.encounter_id
    left join discharge
        on patient_visit.discharge_disposition_id = discharge.discharge_disposition_id
    
    where diagnosis.diagnosis_key like '250%'               -- 250% is the ICD-9 code for diabetes
        and patient_visit.encounter_id is not null
)

select * from patients_with_diabetes