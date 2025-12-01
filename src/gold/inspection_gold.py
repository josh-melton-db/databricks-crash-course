"""
Gold Layer: Aggregated Inspection Metrics

Calculates defect rates and aggregated sensor metrics by device, factory, and model.
Provides business-level insights for monitoring and dashboarding.
"""

from pyspark import pipelines as dp
from pyspark.sql.functions import col, avg, count


@dp.materialized_view(
    name="inspection_gold",
    comment="Aggregates defects by categorical variables"
)
def inspection_gold():
    """
    Aggregate inspection data with sensor metrics.
    
    Groups by:
    - device_id: Individual device tracking
    - factory_id: Factory-level performance monitoring
    - model_id: Model-specific defect patterns
    - defect: Defect flag (0 = no defect, 1 = defect)
    
    Provides:
    - Count of inspections
    - Average sensor readings (temperature, density, delay, rotation speed, air pressure)
    """
    silver = spark.read.table("inspection_silver")
    
    return (
        silver
        .groupBy("device_id", "factory_id", "model_id", "defect")
        .agg(
            count("*").alias("count"),
            avg(col("sensor_temperature")).alias("average_temperature"),
            avg(col("sensor_density")).alias("average_density"),
            avg(col("sensor_delay")).alias("average_delay"),
            avg(col("sensor_rotation_speed")).alias("average_rotation_speed"),
            avg(col("sensor_air_pressure")).alias("average_air_pressure")
        )
    )
