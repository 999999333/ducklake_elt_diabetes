import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source(
    {
        "client": {
            "base_url": "https://jaffle-shop.dlthub.com/api/v1",
            },
            "resources": ["customers", "products", "stores"],
        },
    )

pipeline = dlt.pipeline(
    pipeline_name="rest_api_example",
    destination="duckdb",
    dataset_name="rest_api_data",
)

pipeline.run(source)