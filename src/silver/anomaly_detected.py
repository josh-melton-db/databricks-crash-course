"""
Silver Layer: Anomaly Detection

Uses physics-based modeling to identify anomaly warnings from sensor data.
Flags potential issues based on field maintenance engineering rules.
Feeds Databricks SQL Alerts for real-time notification.
"""

from pyspark import pipelines as dp
from pyspark.sql.functions import col


@dp.table(
    name="anomaly_detected",
    comment="Uses physics-based modeling to predict anomaly warnings. Feeds Databricks SQL Alerts"
)
def anomaly_detected():
    """
    Apply condition-based threshold monitoring rules to detect anomalies.
    
    Rules defined by field maintenance engineers:
    - High delay + high rotation speed
    - Excessive temperature
    - High density + low air pressure
    """
    bronze = spark.readStream.table("sensor_bronze")
    
    return (
        bronze.where(
            ((col("delay") > 155) & (col("rotation_speed") > 800)) |
            (col("temperature") > 101) |
            ((col("density") > 4.6) & (col("air_pressure") < 840))
        )
    )
