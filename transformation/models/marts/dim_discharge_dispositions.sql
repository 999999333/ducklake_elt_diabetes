{{ config(materialized='table') }}

with mappings as (
    select *
    from {{ ref('stg_diabetes__mappings') }}
),

final as (
    select
        id as discharge_disposition_id,
        description
    from mappings
    where mapping_name = 'discharge_disposition_id'
)

select * from final