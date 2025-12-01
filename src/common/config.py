"""
Configuration management for DLT pipeline.

Loads configuration from Databricks Asset Bundle variables passed
via pipeline configuration settings.
"""

from pyspark.sql import SparkSession


class PipelineConfig:
    """Configuration for IoT Time Series Analysis DLT Pipeline."""
    
    def __init__(self, spark: SparkSession = None):
        """
        Initialize configuration from pipeline settings.
        
        Args:
            spark: SparkSession instance. If None, gets current session.
        """
        if spark is None:
            spark = SparkSession.getActiveSession()
        
        self.spark = spark
        self.conf = spark.conf
        
        # Core configuration
        self.catalog = self.conf.get("catalog", "default")
        self.schema = self.conf.get("schema")
        
        if not self.schema:
            raise ValueError(
                "Schema must be specified in pipeline configuration. "
                "Set 'schema' in pipeline configuration."
            )
        
        # Table names (standard medallion architecture naming)
        self.sensor_bronze = "sensor_bronze"
        self.inspection_bronze = "inspection_bronze"
        self.anomaly_detected = "anomaly_detected"
        self.inspection_silver = "inspection_silver"
        self.inspection_gold = "inspection_gold"
        
        # Volume paths
        self.sensor_landing = f"/Volumes/{self.catalog}/{self.schema}/{self.sensor_bronze}"
        self.inspection_landing = f"/Volumes/{self.catalog}/{self.schema}/{self.inspection_bronze}"
        self.checkpoints = f"/Volumes/{self.catalog}/{self.schema}/iot_checkpoints"
        
        # Fully qualified table names
        self.sensor_table = f"{self.catalog}.{self.schema}.{self.sensor_bronze}"
        self.inspection_table = f"{self.catalog}.{self.schema}.{self.inspection_bronze}"
        self.silver_table = f"{self.catalog}.{self.schema}.{self.inspection_silver}"
        self.anomaly_table = f"{self.catalog}.{self.schema}.{self.anomaly_detected}"
        self.gold_table = f"{self.catalog}.{self.schema}.{self.inspection_gold}"
    
    def to_dict(self):
        """Export configuration as dictionary."""
        return {
            "catalog": self.catalog,
            "schema": self.schema,
            "sensor_bronze": self.sensor_bronze,
            "inspection_bronze": self.inspection_bronze,
            "anomaly_detected": self.anomaly_detected,
            "inspection_silver": self.inspection_silver,
            "inspection_gold": self.inspection_gold,
            "sensor_landing": self.sensor_landing,
            "inspection_landing": self.inspection_landing,
            "checkpoints": self.checkpoints,
            "sensor_table": self.sensor_table,
            "inspection_table": self.inspection_table,
            "silver_table": self.silver_table,
            "anomaly_table": self.anomaly_table,
            "gold_table": self.gold_table,
        }
    
    def __repr__(self):
        return f"PipelineConfig(catalog={self.catalog}, schema={self.schema})"


def get_config(spark: SparkSession = None) -> PipelineConfig:
    """
    Get pipeline configuration.
    
    Args:
        spark: SparkSession instance. If None, gets current session.
        
    Returns:
        PipelineConfig instance with all configuration values.
    """
    return PipelineConfig(spark)
