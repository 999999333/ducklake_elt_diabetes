-- models/marts/facts/fct_patient_encounters.sql
{{ config(
    materialized = 'incremental',
    unique_key   = 'encounter_id'
) }}

with patient_record as (
    select *
    from {{ ref('stg_diabetes__patient_records') }}

),

final as (

    select
        -- ── Keys / identifiers ────────────────────────────────────────────
        encounter_id,
        patient_id,
        admission_type_id,
        discharge_disposition_id,
        admission_source_id,
        diag_1,
        diag_2,
        diag_3,

        -- ── Numeric measures (fully additive) ─────────────────────────────
        time_in_hospital,
        num_lab_procedures,
        num_procedures,
        num_medications,
        number_outpatient,
        number_emergency,
        number_inpatient,
        number_diagnoses,

        -- ── Attributes you may want for analysis / filtering ──────────────
        race,
        gender,
        age,
        weight,
        payer_code,
        medical_specialty,
        max_glu_serum,
        a1c_result,
        diabetes_medication,
        readmitted,

        -- individual medication columns
        metformin,
        repaglinide,
        nateglinide,
        chlorpropamide,
        glimepiride,
        acetohexamide,
        glipizide,
        glyburide,
        tolbutamide,
        pioglitazone,
        rosiglitazone,
        acarbose,
        miglitol,
        troglitazone,
        tolazamide,
        examide,
        citoglipton,
        insulin,
        glyburide_metformin,
        glipizide_metformin,
        glimepiride_pioglitazone,
        metformin_rosiglitazone,
        metformin_pioglitazone,
        change,

        -- ── Load metadata ─────────────────────────────────────────────────
        get_current_time()  as load_ts

    from patient_record

    {% if is_incremental() %}
        -- only new encounters
        where encounter_id not in (select encounter_id from {{ this }})
    {% endif %}

)

select * from final