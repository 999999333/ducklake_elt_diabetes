with diagnosis as (
    select
        *
    from {{ ref('stg_idc_9__diagnosis') }}
),

standardize_diagnosis as (
    select

        case
            when diagnosis_key like '250%' then
                rpad(diagnosis_key, 5, '0')
            else
                rpad(left(diagnosis_key, 3), 5, '0')
        end as diagnosis_id,
        coalesce(
            try_cast(substr(diagnosis_key, 4, 1) as int),
            0
        ) as next_digit,
        diagnosis_key,
        diagnosis_name,
    from diagnosis
),

rank_diagnosis as (
    select
        *,
        row_number() over (
            partition by diagnosis_id
            order by next_digit asc
        ) as rn
    from standardize_diagnosis
),

filtered as (
    select
        diagnosis_id,
        diagnosis_key,
        diagnosis_name
    from rank_diagnosis
    where rn = 1
)

select * from filtered