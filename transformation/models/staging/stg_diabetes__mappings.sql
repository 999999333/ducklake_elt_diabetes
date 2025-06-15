with source as (
        select * from {{ source('diabetes', 'mappings') }}
  ),
  renamed as (
      select
        trim({{ adapter.quote("mapping_name") }}) as mapping_name,
        {{ adapter.quote("id") }} as id,
        trim({{ adapter.quote("description") }}) as description

      from source
  )
  select * from renamed
    