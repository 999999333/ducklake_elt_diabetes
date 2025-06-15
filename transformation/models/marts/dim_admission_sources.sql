{{ config(materialized='table') }}

with mappings as (
    select *
    from {{ ref('stg_diabetes__mappings') }}
),

final as (
    select
        id as admission_source_id,
        description
    from mappings
    where mapping_name = 'admission_source_id'
)

select * from final