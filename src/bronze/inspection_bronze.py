"""
Bronze Layer: Inspection Data Ingestion

Loads raw inspection/defect warning data from Unity Catalog Volumes.
Enforces data quality by dropping rows with missing critical fields.
"""

from pyspark import pipelines as dp


@dp.table(name="inspection_bronze", comment="Loads raw inspection files into the bronze layer")
@dp.expect_or_drop("valid timestamp", "`timestamp` is not null")
@dp.expect_or_drop("valid device id", "device_id is not null")
def inspection_bronze():
    """
    Stream raw inspection data from Unity Catalog Volume landing zone.
    
    Drops rows where timestamp or device_id are null, as these fields
    are required for joining with sensor data in downstream processing.
    """
    config = spark.conf
    
    # Get configuration from pipeline settings
    catalog = config.get("catalog", "default")
    schema = config.get("schema")
    
    # Construct paths
    inspection_landing = f"/Volumes/{catalog}/{schema}/inspection_bronze"
    checkpoint_location = f"/Volumes/{catalog}/{schema}/iot_checkpoints/inspection"
    
    # Define expected schema hints
    schema_hints = "defect float, timestamp timestamp, device_id integer"
    
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaHints", schema_hints)
        .option("cloudFiles.schemaLocation", checkpoint_location)
        .load(inspection_landing)
    )
