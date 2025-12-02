import random
import datetime
import json
from databricks.sdk import WorkspaceClient


def set_config_for_bundle(dbutils, catalog='default', schema=None):
    """
    Create configuration for DAB-based deployment.
    
    This configuration is used by the setup notebook to create the schema and volumes.
    The DLT pipeline will receive catalog and schema via DAB variables.
    
    Args:
        dbutils: Databricks utilities
        catalog: Unity Catalog catalog name
        schema: Schema name (auto-generated if None)
    
    Returns:
        Dictionary with configuration values
    """
    w = WorkspaceClient()
    
    if not schema:
        username = w.current_user.me().user_name
        schema = 'iot_anomaly_detection_' + username.replace('@', '_').replace('.', '_')
    
    # Standard table names following medallion architecture
    sensor_name = 'sensor_bronze'
    inspection_name = 'inspection_bronze'
    silver_name = 'inspection_silver'
    anomaly_name = 'anomaly_detected'
    gold_name = 'inspection_gold'
    
    config = {
        'catalog': catalog,
        'schema': schema,
        'checkpoints': f'/Volumes/{catalog}/{schema}/iot_checkpoints',
        'sensor_landing': f'/Volumes/{catalog}/{schema}/{sensor_name}',
        'inspection_landing': f'/Volumes/{catalog}/{schema}/{inspection_name}',
        'sensor_name': sensor_name,
        'inspection_name': inspection_name,
        'silver_name': silver_name,
        'anomaly_name': anomaly_name,
        'gold_name': gold_name,
        'sensor_table': f'{catalog}.{schema}.{sensor_name}',
        'inspection_table': f'{catalog}.{schema}.{inspection_name}',
        'silver_table': f'{catalog}.{schema}.{silver_name}',
        'anomaly_table': f'{catalog}.{schema}.{anomaly_name}',
        'gold_table': f'{catalog}.{schema}.{gold_name}'
    }
    
    return config


def set_config(dbutils, catalog='default', schema=None):
    """
    Legacy configuration function for backward compatibility.
    
    Creates configuration and writes it to a file (old approach).
    Use set_config_for_bundle() for new DAB-based deployments.
    """
    w = WorkspaceClient()
    dbx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    notebook_path = dbx.notebookPath().get()
    folder_path = '/'.join(str(x) for x in notebook_path.split('/')[:-1])
    
    config = set_config_for_bundle(dbutils, catalog, schema)
    
    # Write configuration file (legacy approach)
    with open(f'/Workspace/{folder_path}/util/configuration.py', 'w') as f:
        f.write("config=")
        json.dump(config, f)
    
    return config


def reset_tables(spark, config, dbutils):
    """
    Reset schema and create required volumes.
    
    WARNING: This will drop the entire schema and recreate it, deleting all data.
    
    Args:
        spark: SparkSession
        config: Configuration dictionary
        dbutils: Databricks utilities
    """
    try:
        print('Resetting schema and volumes...')
        spark.sql(f"DROP SCHEMA IF EXISTS {config['catalog']}.{config['schema']} CASCADE")
        spark.sql(f"CREATE SCHEMA {config['catalog']}.{config['schema']}")
        print(f"  ✓ Schema {config['catalog']}.{config['schema']} created")

        # Create sensor landing volume
        sensor_volume = '.'.join(config['sensor_landing'].split('/')[2:])
        spark.sql(f"DROP VOLUME IF EXISTS {sensor_volume}")
        spark.sql(f"CREATE VOLUME {sensor_volume}")
        print(f"  ✓ Volume {sensor_volume} created")
        
        # Create inspection landing volume
        inspection_volume = '.'.join(config['inspection_landing'].split('/')[2:])
        spark.sql(f"DROP VOLUME IF EXISTS {inspection_volume}")
        spark.sql(f"CREATE VOLUME {inspection_volume}")
        print(f"  ✓ Volume {inspection_volume} created")
        
        # Create checkpoint volume
        checkpoint_volume = '.'.join(config['checkpoints'].split('/')[2:])
        spark.sql(f"DROP VOLUME IF EXISTS {checkpoint_volume}")
        spark.sql(f"CREATE VOLUME {checkpoint_volume}")
        print(f"  ✓ Volume {checkpoint_volume} created")
        
        print('\nSchema and volumes reset successfully!')
        
    except Exception as e:
        if 'NO_SUCH_CATALOG_EXCEPTION' in str(e):
            print(f"\nCatalog {config['catalog']} does not exist. Creating it...")
            spark.sql(f"CREATE CATALOG {config['catalog']}")
            print(f"  ✓ Catalog {config['catalog']} created")
            reset_tables(spark, config, dbutils)
        else:
            raise


def new_data_config(dgconfig, rows=None, devices=None, start=None, end=None, year=False, mean_temp=30):
    """
    Generate new data configuration for incremental data landing.
    
    Args:
        dgconfig: Base data generation configuration
        rows: Number of rows to generate
        devices: Number of devices
        start: Start datetime
        end: End datetime
        year: Whether to use yearly temperature pattern
        mean_temp: Mean temperature
    
    Returns:
        Updated configuration dictionary
    """
    if not rows:
        rows = random.randint(7500, 12500)
    if not devices:
        devices = random.randint(8, 12)
    if not start:
        start = datetime.datetime(2024, 1, 1, 0, 0, 0)
    if not end:
        end = datetime.datetime(2024, 2, 1, 0, 0, 0)
    
    dgconfig['shared']['num_rows'] = rows
    dgconfig['shared']['num_devices'] = devices
    dgconfig['shared']['start'] = start
    dgconfig['shared']['end'] = end
    dgconfig['temperature']['lifetime']['year'] = year
    dgconfig['temperature']['lifetime']['mean'] = mean_temp
    
    return dgconfig


# Default data generation configuration
dgconfig = {
    "shared": {
        "num_rows": random.randint(390000, 410000),
        "num_devices": random.randint(58, 62),
        "start": datetime.datetime(2023, 1, 1, 0, 0, 0),
        "end": datetime.datetime(2023, 12, 31, 23, 59, 59),
        "frequency": 0.35,
        "amplitude": 1.2,
    },
    "timestamps": {
        "column_name": "timestamp",
        "minimum": 10,
        "maximum": 350,
    },
    "temperature": {
      "lifetime": {
        "column_name": "temperature",
        "noisy": 0.3,
        "trend": 0.1,
        "mean": 58,
        "std_dev": 17,
      },
      "trip": {
        "trend": -0.8,
        "noisy": 1,
      }
    },
    "air_pressure": {
      "column_name": "air_pressure",
      "depedent_on": "temperature",
      "min": 913,
      "max": 1113,
      "subtract": 15 
    },
    "lifetime": {
        "trend": 0.4,
        "noisy": 0.6,
    },
    "trip": {
        "trend": 0.2,
        "noisy": 1.2,
    },
}
