"""
Silver Layer: Time Series Feature Engineering

Joins sensor data with inspection defect reports using as-of join.
Creates time series features including exponential moving averages and resampling.
Uses Tempo library for distributed time series operations.
"""

from pyspark import pipelines as dp
from pyspark.sql.functions import col, when
from tempo import TSDF


@dp.materialized_view(
    name="inspection_silver",
    comment="Joins bronze sensor data with defect reports"
)
def inspection_silver():
    """
    Create enriched inspection dataset with time series features.
    
    Process:
    1. Read inspection and sensor data from bronze layer
    2. Convert to Tempo TSDF (Time Series DataFrames)
    3. Calculate exponential moving average on rotation speed
    4. Resample sensor data to hourly intervals
    5. Perform as-of join (attaches most recent sensor data to each inspection)
    
    The as-of join ensures we only use sensor data that occurred BEFORE
    the inspection timestamp, avoiding data leakage for predictive modeling.
    """
    # Read bronze layer data
    inspections = spark.read.table("inspection_bronze").drop("_rescued_data")
    raw_sensors = (
        spark.read.table("sensor_bronze")
        .drop("_rescued_data")
        # Fix negative air pressure values (data quality issue)
        .withColumn(
            "air_pressure",
            when(col("air_pressure") < 0, -col("air_pressure"))
            .otherwise(col("air_pressure"))
        )
    )
    
    # Convert to Time Series DataFrames
    inspections_tsdf = TSDF(
        inspections,
        ts_col="timestamp",
        partition_cols=["device_id"]
    )
    
    sensors_tsdf = (
        TSDF(
            raw_sensors,
            ts_col="timestamp",
            partition_cols=["device_id", "trip_id", "factory_id", "model_id"]
        )
        .EMA("rotation_speed", window=5)  # Exponential moving average over 5 rows
        .resample(freq="1 hour", func="mean")  # Resample to 1 hour intervals
    )
    
    # Perform as-of join (price is right rules: most recent sensor data <= inspection time)
    return (
        inspections_tsdf
        .asofJoin(sensors_tsdf, right_prefix="sensor")
        .df  # Convert back to vanilla Spark DataFrame
        .withColumnRenamed("sensor_trip_id", "trip_id")
        .withColumnRenamed("sensor_model_id", "model_id")
        .withColumnRenamed("sensor_factory_id", "factory_id")
    )
