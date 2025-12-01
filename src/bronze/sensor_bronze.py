"""
Bronze Layer: Sensor Data Ingestion

Loads raw sensor data from Unity Catalog Volumes using Autoloader.
Provides schema hints and data quality checks for incoming CSV files.
"""

from pyspark import pipelines as dp
from pyspark.sql.functions import col


@dp.table(name="sensor_bronze", comment="Loads raw sensor data into the bronze layer")
@dp.expect("valid pressure", "air_pressure > 0")
def sensor_bronze():
    """
    Stream raw sensor data from Unity Catalog Volume landing zone.
    
    Uses Autoloader with schema hints to:
    - Cast columns to appropriate types
    - Save unexpected columns to _rescued_data
    - Handle schema evolution from upstream producers
    """
    config = spark.conf
    
    # Get configuration from pipeline settings
    catalog = config.get("catalog", "default")
    schema = config.get("schema")
    
    # Construct paths
    sensor_landing = f"/Volumes/{catalog}/{schema}/sensor_bronze"
    checkpoint_location = f"/Volumes/{catalog}/{schema}/iot_checkpoints/sensor"
    
    # Define expected schema hints
    schema_hints = (
        "device_id integer, trip_id integer, factory_id string, model_id string, "
        "timestamp timestamp, airflow_rate double, rotation_speed double, "
        "air_pressure float, temperature float, delay float, density float"
    )
    
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaHints", schema_hints)
        .option("cloudFiles.schemaLocation", checkpoint_location)
        .load(sensor_landing)
    )
