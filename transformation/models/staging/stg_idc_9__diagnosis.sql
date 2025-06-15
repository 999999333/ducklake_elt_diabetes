with source as (
        select * from {{ source('idc_9', 'diagnosis') }}
  ),
  renamed as (
      select
        {{ adapter.quote("diagnosis_id") }} as diagnosis_key,
        {{ adapter.quote("diagnosis_name") }}

      from source
  )
  select * from renamed
    