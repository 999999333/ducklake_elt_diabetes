with patient_record as (
    select *
    from {{ ref('stg_diabetes__patient_records') }}
),

unpivot_diagnosis as (
    select
        encounter_id,
        diag_1 as diagnosis_key
    from patient_record
    where diag_1 is not null
    union all
    select
        encounter_id,
        diag_2 as diagnosis_key
    from patient_record
    where diag_2 is not null
    union all
    select
        encounter_id,
        diag_3 as diagnosis_key
    from patient_record
    where diag_3 is not null    
),

order_by_encounter as (
    select * from unpivot_diagnosis
    order by diagnosis_key
),

standardize_diagnosis as (
    select
        encounter_id,

        case
            when diagnosis_key like '250%' then
                rpad(
                    replace(diagnosis_key,'.',''),
                    5,
                    '0'
                    )
            else
                rpad(left(diagnosis_key, 3), 5, '0')
        end as diagnosis_id
        
    from order_by_encounter
)

select * from standardize_diagnosis