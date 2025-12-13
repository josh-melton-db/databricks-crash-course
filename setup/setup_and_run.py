# Databricks notebook source
# MAGIC %md
# MAGIC # IoT Time Series Analysis - Simple Setup
# MAGIC
# MAGIC This notebook sets up the complete IoT anomaly detection demo by:
# MAGIC 1. Creating Unity Catalog schema and volumes
# MAGIC 2. Generating synthetic IoT sensor and inspection data
# MAGIC 3. Creating Bronze, Silver, and Gold tables
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Unity Catalog enabled workspace
# MAGIC - DBR 14.3 ML or later (for Tempo library support)
# MAGIC
# MAGIC **Simply click "Run All" to set up the complete demo!**

# COMMAND ----------

# DBTITLE 1,Install Dependencies
# MAGIC %pip install databricks-sdk>=0.35.0 dbl-tempo>=0.1.30 -q
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Configuration
# Configure your catalog and schema here
CATALOG = 'dwx_airops_insights_platform_dev_workspace'  # Change to your catalog name
SCHEMA = 'db_crash_course'  # Leave as None to auto-generate, or set to your schema name

# Data generation parameters
NUM_ROWS = 5_000_000  # Number of sensor readings to generate
NUM_DEVICES = 700   # Number of IoT devices

print(f"Configuration:")
print(f"  Catalog: {CATALOG}")
print(f"  Schema: {SCHEMA if SCHEMA else 'Auto-generate based on username'}")
print(f"  Data volume: {NUM_ROWS:,} rows across {NUM_DEVICES} devices")

# COMMAND ----------

# DBTITLE 1,Import Required Modules
from pyspark.sql.functions import (
    col, when, avg, count, current_timestamp, lit,
    rand, expr, dense_rank, to_date
)
from pyspark.sql import Window
from databricks.sdk import WorkspaceClient
import random
import datetime

# Get username for schema naming
w = WorkspaceClient()
username = w.current_user.me().user_name

# Set schema name
if not SCHEMA:
    SCHEMA = f'iot_anomaly_detection_{username.replace("@", "_").replace(".", "_")}'

print(f"\nUsing schema: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# DBTITLE 1,Create Schema and Volumes
print("Setting up Unity Catalog schema and volumes...")

# Drop and recreate schema (WARNING: deletes all existing data)
spark.sql(f"DROP SCHEMA IF EXISTS {CATALOG}.{SCHEMA} CASCADE")
spark.sql(f"CREATE SCHEMA {CATALOG}.{SCHEMA}")
print(f"  ✓ Created schema: {CATALOG}.{SCHEMA}")

# Create volumes for data landing
spark.sql(f"CREATE VOLUME {CATALOG}.{SCHEMA}.sensor_data")
print(f"  ✓ Created volume: {CATALOG}.{SCHEMA}.sensor_data")

spark.sql(f"CREATE VOLUME {CATALOG}.{SCHEMA}.inspection_data")
print(f"  ✓ Created volume: {CATALOG}.{SCHEMA}.inspection_data")

spark.sql(f"CREATE VOLUME {CATALOG}.{SCHEMA}.checkpoints")
print(f"  ✓ Created volume: {CATALOG}.{SCHEMA}.checkpoints")

# Set paths
SENSOR_LANDING = f"/Volumes/{CATALOG}/{SCHEMA}/sensor_data"
INSPECTION_LANDING = f"/Volumes/{CATALOG}/{SCHEMA}/inspection_data"
CHECKPOINT_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/checkpoints"

print("\n✅ Schema and volumes created successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Synthetic IoT Data
# MAGIC
# MAGIC This section generates realistic IoT sensor data with:
# MAGIC - Temperature, air pressure, rotation speed, airflow rate, density, delay
# MAGIC - Time series patterns (seasonality, trends, noise)
# MAGIC - Simulated defects based on physical conditions

# COMMAND ----------

# DBTITLE 1,Data Generation Functions
import pandas as pd
import numpy as np
from random import randint, shuffle, random as rand_uniform

def get_starting_temps(start, end, mean=58, std_dev=17, year=True):
    """Generate baseline temperature time series"""
    dates = pd.date_range(start, end)
    num_rows = len(dates)
    if year:
        normal1 = np.random.normal(loc=mean, scale=std_dev, size=num_rows // 2).clip(min=0, max=78)
        normal1 = np.sort(normal1)
        normal2 = np.random.normal(loc=mean, scale=std_dev, size=num_rows // 2 + num_rows % 2).clip(min=0, max=78)
        normal2 = np.sort(normal2)[::-1]
        normal = np.concatenate((normal1, normal2))
    else:
        normal = np.random.normal(loc=mean, scale=std_dev, size=num_rows).clip(min=0, max=78)
    
    noise = 9.5 * make_timeseries('autoregressive', num_rows, 0.35, 1.2, noisy=0.3, trend_factor=0.1)
    temps = normal + noise
    pdf = pd.DataFrame({'date': dates, 'starting_temp': temps})
    pdf['date'] = pdf['date'].dt.date
    return pdf

def make_timeseries(pattern, num_points, frequency, amplitude, trend_factor=0, noisy=0.3):
    """Generate synthetic time series with various patterns"""
    times = np.linspace(0, 10, num_points)
    noise = np.random.normal(loc=0, scale=noisy, size=num_points)
    trend = times * trend_factor
    
    timeseries = np.zeros(num_points)
    if num_points < 2: 
        return timeseries
    
    if pattern == 'sinusoid':
        for i in range(num_points):
            timeseries[i] = noise[i] + np.sin(2*np.pi*frequency * times[i]) * amplitude + trend[i]
    elif pattern == 'periodic':
        for i in range(num_points):
            freq_val = np.random.normal(loc=frequency, scale=0.5, size=1)
            amplitude_val = np.random.normal(loc=amplitude, scale=1.2, size=1)
            timeseries[i] = noise[i] + float(amplitude_val * np.sin(freq_val * times[i])) + trend[i]
    elif pattern == 'autoregressive':
        timeseries[0] = rand_uniform() + noisy
        timeseries[1] = (rand_uniform()+1) * (noisy + .5)
        for i in range(2, num_points):
            timeseries[i] = noise[i] + (timeseries[i-1] * (1+trend_factor)) - (timeseries[i-2] * (1-trend_factor))
    
    return timeseries

def timestamp_sequence_lengths(total, minimum=10, maximum=350):
    """Generate random sequence lengths for timestamps"""
    nums = []
    while total > 0:
        if total < 300:
            n = total
        else:
            n = randint(minimum, maximum)
        nums.append(n)
        total -= n
    shuffle(nums)
    return nums

def get_datetime_list(start_date, end_date, length):
    """Generate random datetime sequence"""
    time_diff = (end_date - start_date).total_seconds()
    random_second = randint(0, int(time_diff))
    rand_datetime = start_date + datetime.timedelta(seconds=random_second)
    return pd.date_range(start=str(rand_datetime), periods=length, freq='1 min')

def add_timestamps(pdf: pd.DataFrame) -> pd.DataFrame:
    """Add timestamp sequences to device data"""
    num_rows = len(pdf)
    start = datetime.datetime(2023, 1, 1, 0, 0, 0)
    end = datetime.datetime(2023, 12, 31, 23, 59, 59)
    
    lengths = timestamp_sequence_lengths(num_rows)
    timestamp_sequences = [pd.Series(get_datetime_list(start, end, length)) for length in lengths]
    pdf['timestamp'] = pd.concat(timestamp_sequences, ignore_index=True)
    return pdf

def add_weather(pdf: pd.DataFrame) -> pd.DataFrame:
    """Add temperature and air pressure features"""
    num_rows = len(pdf)
    start_temp = pdf['starting_temp'].iloc[0]
    pdf['pd_timestamp'] = pd.to_datetime(pdf['timestamp'])
    
    min_time = pdf['pd_timestamp'].min()
    coldest = pdf['pd_timestamp'].dt.normalize() + pd.DateOffset(hours=randint(5, 8))
    hottest = pdf['pd_timestamp'].dt.normalize() + pd.DateOffset(hours=randint(14, 18))
    hottest_time = hottest[0]
    coldest_time = coldest[0]
    
    upwards = min_time < hottest_time and min_time > coldest_time
    trend_factor = -0.8 if not upwards else 0.8
    
    pdf['temperature'] = start_temp + make_timeseries('periodic', num_rows, 0.35, 1.2, trend_factor, 1.0)
    pdf = pdf.drop('pd_timestamp', axis=1)
    
    random_lapse_rate = 1.2 + np.random.uniform(.5, 1.5)
    pdf['air_pressure'] = randint(913, 1113) - (pdf['temperature'] - 15) * random_lapse_rate
    
    return pdf

def add_lifetime_features(pdf: pd.DataFrame) -> pd.DataFrame:
    """Add density feature"""
    num_points = len(pdf)
    sinusoidal = make_timeseries('sinusoid', num_points, 0.35, 1.2, 0.4, 0.6)
    pdf['density'] = abs(sinusoidal - np.mean(sinusoidal)/2) 
    return pdf

def add_trip_features(pdf: pd.DataFrame) -> pd.DataFrame:
    """Add rotation speed, delay, and airflow rate features"""
    num_points = len(pdf)
    rotation = abs(make_timeseries('autoregressive', num_points, 0.35, 1.2)) * 100
    init_delay = make_timeseries('sinusoid', num_points, 0.35, 1.2, 0.2, 1.2)
    
    pdf['delay'] = abs(init_delay * np.sqrt(rotation))
    pdf['rotation_speed'] = rotation
    pdf['airflow_rate'] = pdf['rotation_speed'].shift(5) / pdf['air_pressure']
    pdf = pdf.fillna(method='bfill').fillna(method='ffill').fillna(0)
    
    return pdf

def add_defects(pdf: pd.DataFrame) -> pd.DataFrame:
    """Add defect labels based on sensor conditions"""
    pdf = pdf.sort_values(['timestamp'])
    pdf['temp_ewma'] = pdf['temperature'].shift(1).ewm(5).mean()
    pdf['temp_difference'] = pdf['temperature'] - pdf['temp_ewma']
    percentile89 = pdf['temperature'].quantile(0.89)
    percentile93 = pdf['temperature'].quantile(0.93)
    
    conditions = [
        (pdf['temp_difference'] > 1.8) & (pdf['factory_id'] == 'A06') & (pdf['temperature'] > percentile89),
        (pdf['temp_difference'] > 1.8) & (pdf['model_id'] == 'SkyJet234') & (pdf['temperature'] > percentile89),
        (pdf['temp_difference'] > 1.9) & (pdf['model_id'] == 'SkyJet334') & (pdf['temperature'] > percentile93),
        (pdf['delay'] > 39) & (pdf['rotation_speed'] > 590),
        (pdf['density'] > 4.2) & (pdf['air_pressure'] < 780),
    ]
    outcomes = [round(rand_uniform()+.8), round(rand_uniform()+.85), round(rand_uniform()+.85), 
                round(rand_uniform()+.85), round(rand_uniform()+.95)]
    pdf['defect'] = np.select(conditions, outcomes, default=0)
    pdf['defect'] = pdf['defect'].shift(20, fill_value=0)
    pdf = pdf.drop(['temp_difference', 'temp_ewma'], axis=1)
    
    return pdf

print("✓ Data generation functions loaded")

# COMMAND ----------

# DBTITLE 1,Generate IoT Sensor Data
print(f"Generating {NUM_ROWS:,} rows of IoT sensor data for {NUM_DEVICES} devices...")
print("This may take a few minutes...\n")

# Create initial device dataframe
factory_ls = ["'A06'", "'D18'", "'J15'", "'C04'", "'T10'"]
model_ls = ["'SkyJet134'", "'SkyJet234'", "'SkyJet334'", "'EcoJet1000'", "'JetLift7000'",
            "'EcoJet2000'", "'FlyForceX550'", "'TurboFan3200'", "'SkyBolt1'", "'SkyBolt2'",
            "'MightyWing1100'", "'EcoJet3000'", "'AeroGlider4150'", "'SkyBolt250'"]

initial_df = (
    spark.range(NUM_ROWS)
    .withColumn('device_id', (rand(seed=0)*NUM_DEVICES).cast('int') + 1)
    .withColumn('factory_id', expr(f"element_at(array({','.join(factory_ls)}), abs(hash(device_id)%{len(factory_ls)})+1)"))
    .withColumn('model_id', expr(f"element_at(array({','.join(model_ls)}), abs(hash(device_id)%{len(model_ls)})+1)"))
    .drop('id')
    .withColumn('device_id', col('device_id').cast('string'))
)

# Generate temperature baseline
start_date = datetime.datetime(2023, 1, 1, 0, 0, 0)
end_date = datetime.datetime(2023, 12, 31, 23, 59, 59)
temps = get_starting_temps(start_date, end_date)
starting_temps = spark.createDataFrame(temps)

# Define schemas for pandas UDF operations
timestamp_schema = 'device_id string, factory_id string, model_id string, timestamp timestamp'
weather_schema = '''device_id string, factory_id string, model_id string, timestamp timestamp, date date,
                    trip_id integer, starting_temp double, temperature double, air_pressure double'''
lifetime_schema = '''device_id string, trip_id int, factory_id string, model_id string, timestamp timestamp,  
                     air_pressure double, temperature double, density float'''
trip_schema = '''device_id string, trip_id int, factory_id string, model_id string, timestamp timestamp, airflow_rate double,  
                 rotation_speed double, air_pressure double, temperature double, delay float, density float'''
defect_schema = '''device_id string, trip_id int, factory_id string, model_id string, timestamp timestamp, airflow_rate double,  
                   rotation_speed double, air_pressure double, temperature double, delay float, density float, defect float'''

# Generate complete dataset with all features
print("  → Adding timestamps...")
iot_data = (
    initial_df
    .groupBy('device_id').applyInPandas(add_timestamps, timestamp_schema)
    .withColumn('date', to_date(col('timestamp')))
    .withColumn('trip_id', dense_rank().over(Window.partitionBy('device_id').orderBy('date')))
    .join(starting_temps, 'date', 'left')
)

print("  → Adding weather features (temperature, air pressure)...")
iot_data = iot_data.groupBy('trip_id', 'device_id').applyInPandas(add_weather, weather_schema).drop('starting_temp', 'date')

print("  → Adding lifetime features (density)...")
iot_data = iot_data.groupBy('device_id').applyInPandas(add_lifetime_features, lifetime_schema)

print("  → Adding trip features (rotation speed, delay, airflow)...")
iot_data = iot_data.groupBy('device_id', 'trip_id').applyInPandas(add_trip_features, trip_schema)

print("  → Adding defect labels...")
iot_data = iot_data.groupBy('device_id').applyInPandas(add_defects, defect_schema)

# Cache the generated data for reuse
iot_data.write.format('delta').mode('overwrite').save(f"{CHECKPOINT_PATH}/tmp")
iot_data = spark.read.format('delta').load(f"{CHECKPOINT_PATH}/tmp")

row_count = iot_data.count()
print(f"\n✅ Generated {row_count:,} rows of IoT data successfully!")

# COMMAND ----------

# DBTITLE 1,Prepare Sensor and Inspection Data
print("Preparing sensor and inspection datasets...\n")

# Sensor data: drop defect column and introduce some data quality issues
sensor_data = (
    iot_data.drop('defect')
    .withColumn('temperature', when(rand() < 0.1, None).otherwise(col('temperature')))  # 10% missing temps
    .withColumn('air_pressure', when(rand() < 0.05, -col('air_pressure')).otherwise(col('air_pressure')))  # 5% negative pressures
    .withColumn('timestamp', expr('timestamp + INTERVAL 3 SECONDS * rand()'))  # Add jitter to timestamps
)

# Inspection data: sample defects and non-defects, simulate delayed inspections
num_defects = int(iot_data.count() * 0.004)
defect_data = (
    iot_data.select('defect', 'timestamp', 'device_id')
    .where('defect = 1').orderBy(rand()).limit(int(num_defects/16))  # Few actual defects
    .union(
        iot_data.select('defect', 'timestamp', 'device_id')
        .where('defect = 0').orderBy(rand()).limit(int(15*num_defects/16))  # Mostly non-defects
    )
    .withColumn('timestamp', expr('timestamp + INTERVAL 2 HOURS * (2 + rand())'))  # Inspections happen 2-4 hours later
    .withColumn('timestamp', when(rand() < 0.05, None).otherwise(col('timestamp')))  # 5% missing timestamps
)

sensor_count = sensor_data.count()
inspection_count = defect_data.count()

print(f"  Sensor readings: {sensor_count:,} rows")
print(f"  Inspection records: {inspection_count:,} rows")

# COMMAND ----------

# DBTITLE 1,Land Data to Volumes
print("\nLanding data to Unity Catalog volumes...")

# Write sensor data as CSV files
sensor_data.write.mode('overwrite').csv(SENSOR_LANDING, header='true')
print(f"  ✓ Sensor data written to: {SENSOR_LANDING}")

# Write inspection data as CSV files
defect_data.write.mode('overwrite').csv(INSPECTION_LANDING, header='true')
print(f"  ✓ Inspection data written to: {INSPECTION_LANDING}")

# Clean up temp data
dbutils.fs.rm(f"{CHECKPOINT_PATH}/tmp", recurse=True)

print("\n✅ Data landing complete!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Dimension Tables
# MAGIC
# MAGIC Dimension tables provide reference data for factories, models, and devices with proper primary/foreign key relationships.

# COMMAND ----------

# DBTITLE 1,Import Dimension Table and System Table Generation Functions
from util.data_generator import generate_dimension_tables, generate_device_dimension, generate_synthetic_system_tables

print("✓ Dimension table and system table generation functions imported")

# COMMAND ----------

print("Creating dim_factories table with PRIMARY KEY...")

dim_factories, dim_models = generate_dimension_tables(spark)

# COMMAND ----------

# DBTITLE 1,Create dim_factories Table
# Create table with PRIMARY KEY constraint
spark.sql(f"""
    CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.dim_factories (
        factory_id STRING NOT NULL,
        factory_name STRING,
        region STRING,
        city STRING,
        state STRING,
        CONSTRAINT factories_pk PRIMARY KEY (factory_id) NOT ENFORCED
    ) USING DELTA
""").display()

# Insert data
dim_factories.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.dim_factories")
factory_count = dim_factories.count()
print(f"  → {factory_count} factories loaded")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.dim_factories with PRIMARY KEY (factory_id)\n")

# COMMAND ----------

print("Creating dim_models table with PRIMARY KEY...")

spark.sql(f"""
    CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.dim_models (
        model_id STRING NOT NULL,
        model_name STRING,
        model_family STRING,
        model_category STRING,
        release_year INT,
        CONSTRAINT models_pk PRIMARY KEY (model_id) NOT ENFORCED
    ) USING DELTA
""").display()

# COMMAND ----------

# DBTITLE 1,Create dim_models Table
# Insert data
dim_models.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.dim_models")
model_count = dim_models.count()
print(f"  → {model_count} models loaded")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.dim_models with PRIMARY KEY (model_id)\n")

# COMMAND ----------

print("Creating dim_devices table with PRIMARY KEY and FOREIGN KEYs...")

dim_devices = generate_device_dimension(spark, NUM_DEVICES)

# Create table with PRIMARY KEY and FOREIGN KEY constraints
spark.sql(f"""
    CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.dim_devices (
        device_id INT NOT NULL,
        factory_id STRING NOT NULL,
        model_id STRING NOT NULL,
        installation_date DATE,
        status STRING,
        CONSTRAINT devices_pk PRIMARY KEY (device_id) NOT ENFORCED,
        CONSTRAINT devices_factory_fk FOREIGN KEY (factory_id) REFERENCES {CATALOG}.{SCHEMA}.dim_factories(factory_id) NOT ENFORCED,
        CONSTRAINT devices_model_fk FOREIGN KEY (model_id) REFERENCES {CATALOG}.{SCHEMA}.dim_models(model_id) NOT ENFORCED
    ) USING DELTA
""").display()

# COMMAND ----------

# DBTITLE 1,Create dim_devices Table
# Insert data
dim_devices.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.dim_devices")
device_count = dim_devices.count()
print(f"  → {device_count} devices loaded")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.dim_devices with PRIMARY KEY and FOREIGN KEYs\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Bronze Layer Tables
# MAGIC
# MAGIC Bronze layer loads raw data from volumes with minimal transformations and foreign key relationships to dimension tables.

# COMMAND ----------

# DBTITLE 1,Create sensor_bronze Table
print("Creating sensor_bronze table with FOREIGN KEYs...")

sensor_bronze_df = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(SENSOR_LANDING)
    .select(
        col('device_id').cast('integer'),
        col('trip_id').cast('integer'),
        col('factory_id').cast('string'),
        col('model_id').cast('string'),
        col('timestamp').cast('timestamp'),
        col('airflow_rate').cast('double'),
        col('rotation_speed').cast('double'),
        col('air_pressure').cast('float'),
        col('temperature').cast('float'),
        col('delay').cast('float'),
        col('density').cast('float')
    )
)

# Data quality check: count invalid pressure readings
invalid_pressure_count = sensor_bronze_df.filter(col('air_pressure') <= 0).count()
total_count = sensor_bronze_df.count()
print(f"  → {total_count:,} sensor readings loaded")
print(f"  → {invalid_pressure_count:,} readings with invalid pressure (will be corrected in silver layer)")

# Create table with FOREIGN KEY constraints
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.sensor_bronze (
        device_id INT NOT NULL,
        trip_id INT,
        factory_id STRING NOT NULL,
        model_id STRING NOT NULL,
        timestamp TIMESTAMP,
        airflow_rate DOUBLE,
        rotation_speed DOUBLE,
        air_pressure FLOAT,
        temperature FLOAT,
        delay FLOAT,
        density FLOAT,
        CONSTRAINT sensor_device_fk FOREIGN KEY (device_id) REFERENCES {CATALOG}.{SCHEMA}.dim_devices(device_id) NOT ENFORCED,
        CONSTRAINT sensor_factory_fk FOREIGN KEY (factory_id) REFERENCES {CATALOG}.{SCHEMA}.dim_factories(factory_id) NOT ENFORCED,
        CONSTRAINT sensor_model_fk FOREIGN KEY (model_id) REFERENCES {CATALOG}.{SCHEMA}.dim_models(model_id) NOT ENFORCED
    ) USING DELTA
""")

# Write data
sensor_bronze_df.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.sensor_bronze")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.sensor_bronze with FOREIGN KEYs to dimension tables\n")

# COMMAND ----------

# DBTITLE 1,Create inspection_bronze Table
print("Creating inspection_bronze table with FOREIGN KEY...")

inspection_bronze_df = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(INSPECTION_LANDING)
    .select(
        col('defect').cast('float'),
        col('timestamp').cast('timestamp'),
        col('device_id').cast('integer')
    )
    # Drop records with missing critical fields
    .filter((col('timestamp').isNotNull()) & (col('device_id').isNotNull()))
)

inspection_count = inspection_bronze_df.count()
print(f"  → {inspection_count:,} inspection records loaded")

# Create table with FOREIGN KEY constraint
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.inspection_bronze (
        defect FLOAT,
        timestamp TIMESTAMP,
        device_id INT NOT NULL,
        CONSTRAINT inspection_device_fk FOREIGN KEY (device_id) REFERENCES {CATALOG}.{SCHEMA}.dim_devices(device_id) NOT ENFORCED
    ) USING DELTA
""")

# Write data
inspection_bronze_df.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.inspection_bronze")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.inspection_bronze with FOREIGN KEY to dim_devices\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Silver Layer Tables
# MAGIC
# MAGIC Silver layer performs data quality fixes, feature engineering, and joins.

# COMMAND ----------

# DBTITLE 1,Create anomaly_detected Table
print("Creating anomaly_detected table (anomaly detection)...")

# Apply threshold-based anomaly detection rules
anomaly_detected_df = (
    spark.table(f"{CATALOG}.{SCHEMA}.sensor_bronze")
    .filter(
        ((col("delay") > 155) & (col("rotation_speed") > 800)) |  # High delay + high rotation
        (col("temperature") > 101) |  # Excessive temperature
        ((col("density") > 4.6) & (col("air_pressure") < 840))  # High density + low pressure
    )
)

anomaly_count = anomaly_detected_df.count()
print(f"  → {anomaly_count:,} anomalies detected")

# Write silver table
anomaly_detected_df.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.anomaly_detected")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.anomaly_detected\n")

# COMMAND ----------

# DBTITLE 1,Create inspection_silver Table with Time Series Features
print("Creating inspection_silver table (time series features + as-of join)...")

# Import Tempo for time series operations
from tempo import TSDF

# Read and clean bronze layer data
inspections = spark.table(f"{CATALOG}.{SCHEMA}.inspection_bronze")

raw_sensors = (
    spark.table(f"{CATALOG}.{SCHEMA}.sensor_bronze")
    # Fix negative air pressure values
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

print("  → Calculating exponential moving average on rotation speed...")
print("  → Resampling sensor data to hourly intervals...")
sensors_tsdf = (
    TSDF(
        raw_sensors,
        ts_col="timestamp",
        partition_cols=["device_id", "trip_id", "factory_id", "model_id"]
    )
    .EMA("rotation_speed", window=5)  # Exponential moving average over 5 rows
    .resample(freq="1 hour", func="mean")  # Resample to 1 hour intervals
)

print("  → Performing as-of join (joining most recent sensor data to each inspection)...")
# As-of join: for each inspection, attach the most recent sensor reading that occurred BEFORE the inspection
inspection_silver_df = (
    inspections_tsdf
    .asofJoin(sensors_tsdf, right_prefix="sensor")
    .df  # Convert back to regular Spark DataFrame
    .withColumnRenamed("sensor_trip_id", "trip_id")
    .withColumnRenamed("sensor_model_id", "model_id")
    .withColumnRenamed("sensor_factory_id", "factory_id")
)

silver_count = inspection_silver_df.count()
print(f"  → {silver_count:,} enriched inspection records")

# Write silver table
inspection_silver_df.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.inspection_silver")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.inspection_silver\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Gold Layer Table
# MAGIC
# MAGIC Gold layer provides aggregated business metrics.

# COMMAND ----------

# DBTITLE 1,Create inspection_gold Table
print("Creating inspection_gold table (aggregated metrics)...")

# Aggregate inspection data by device, factory, model, and defect flag
inspection_gold_df = (
    spark.table(f"{CATALOG}.{SCHEMA}.inspection_silver")
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

gold_count = inspection_gold_df.count()
print(f"  → {gold_count:,} aggregated records (by device/factory/model/defect)")

# Write gold table
inspection_gold_df.write.format('delta').mode('overwrite').saveAsTable(f"{CATALOG}.{SCHEMA}.inspection_gold")
print(f"✅ Created table: {CATALOG}.{SCHEMA}.inspection_gold\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup Complete! 🎉
# MAGIC
# MAGIC All tables have been created successfully with a proper star schema design including primary/foreign key relationships.
# MAGIC
# MAGIC ### Data Model
# MAGIC
# MAGIC **Dimension Tables (with PRIMARY KEYs):**
# MAGIC - `dim_factories` - Factory reference data, PK(factory_id)
# MAGIC - `dim_models` - IoT device model reference data, PK(model_id)
# MAGIC - `dim_devices` - Device master data, PK(device_id), FK→factories, FK→models
# MAGIC
# MAGIC **Fact Tables (with FOREIGN KEYs):**
# MAGIC - `sensor_bronze` - IoT sensor readings, FK→devices, FK→factories, FK→models
# MAGIC - `inspection_bronze` - Device inspection records, FK→devices
# MAGIC
# MAGIC ### Dimension Tables
# MAGIC ```sql
# MAGIC -- View factory reference data
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.dim_factories;
# MAGIC
# MAGIC -- View model reference data
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.dim_models ORDER BY model_family, release_year;
# MAGIC
# MAGIC -- View device master data with relationships
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.dim_devices LIMIT 10;
# MAGIC ```
# MAGIC
# MAGIC ### Bronze Tables (Raw Data with FK Relationships)
# MAGIC ```sql
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.sensor_bronze LIMIT 10;
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.inspection_bronze LIMIT 10;
# MAGIC ```
# MAGIC
# MAGIC ### Silver Tables (Enriched & Feature Engineered)
# MAGIC ```sql
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.anomaly_detected LIMIT 10;
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.inspection_silver LIMIT 10;
# MAGIC ```
# MAGIC
# MAGIC ### Gold Table (Business Metrics)
# MAGIC ```sql
# MAGIC SELECT * FROM {CATALOG}.{SCHEMA}.inspection_gold ORDER BY count DESC LIMIT 10;
# MAGIC ```
# MAGIC
# MAGIC ### Sample Queries with Dimensional Joins
# MAGIC
# MAGIC **Defect rate by factory with factory details:**
# MAGIC ```sql
# MAGIC SELECT 
# MAGIC   f.factory_name,
# MAGIC   f.region,
# MAGIC   f.city,
# MAGIC   SUM(CASE WHEN ig.defect = 1 THEN ig.count ELSE 0 END) as defects,
# MAGIC   SUM(ig.count) as total_inspections,
# MAGIC   ROUND(100.0 * SUM(CASE WHEN ig.defect = 1 THEN ig.count ELSE 0 END) / SUM(ig.count), 2) as defect_rate_pct
# MAGIC FROM {CATALOG}.{SCHEMA}.inspection_gold ig
# MAGIC JOIN {CATALOG}.{SCHEMA}.dim_factories f ON ig.factory_id = f.factory_id
# MAGIC GROUP BY f.factory_name, f.region, f.city
# MAGIC ORDER BY defect_rate_pct DESC;
# MAGIC ```
# MAGIC
# MAGIC **Recent anomalies with device and model details:**
# MAGIC ```sql
# MAGIC SELECT 
# MAGIC   a.device_id,
# MAGIC   d.status as device_status,
# MAGIC   f.factory_name,
# MAGIC   m.model_name,
# MAGIC   m.model_category,
# MAGIC   a.timestamp,
# MAGIC   a.temperature,
# MAGIC   a.rotation_speed,
# MAGIC   a.density
# MAGIC FROM {CATALOG}.{SCHEMA}.anomaly_detected a
# MAGIC JOIN {CATALOG}.{SCHEMA}.dim_devices d ON a.device_id = d.device_id
# MAGIC JOIN {CATALOG}.{SCHEMA}.dim_factories f ON a.factory_id = f.factory_id
# MAGIC JOIN {CATALOG}.{SCHEMA}.dim_models m ON a.model_id = m.model_id
# MAGIC ORDER BY a.timestamp DESC
# MAGIC LIMIT 20;
# MAGIC ```
# MAGIC
# MAGIC **Sensor performance by model family:**
# MAGIC ```sql
# MAGIC SELECT 
# MAGIC   m.model_family,
# MAGIC   m.model_category,
# MAGIC   COUNT(DISTINCT s.device_id) as device_count,
# MAGIC   AVG(s.temperature) as avg_temperature,
# MAGIC   AVG(s.rotation_speed) as avg_rotation_speed,
# MAGIC   MAX(s.temperature) as max_temperature
# MAGIC FROM {CATALOG}.{SCHEMA}.sensor_bronze s
# MAGIC JOIN {CATALOG}.{SCHEMA}.dim_models m ON s.model_id = m.model_id
# MAGIC GROUP BY m.model_family, m.model_category
# MAGIC ORDER BY avg_temperature DESC;
# MAGIC ```

# COMMAND ----------

# DBTITLE 1,Generate Synthetic System Tables
print("\nGenerating synthetic system tables for training...")
generate_synthetic_system_tables(spark, CATALOG, SCHEMA)
print("✅ Synthetic system tables created!\n")

# COMMAND ----------

# DBTITLE 1,Summary Statistics
print("="*80)
print("SETUP COMPLETE - Summary".center(80))
print("="*80)
print(f"\n📊 Tables Created in {CATALOG}.{SCHEMA}:")
print(f"\n  Dimension Tables (with PRIMARY KEYs):")
print(f"    • dim_factories: {factory_count} rows - PK(factory_id)")
print(f"    • dim_models: {model_count} rows - PK(model_id)")
print(f"    • dim_devices: {device_count} rows - PK(device_id), FK→factories, FK→models")
print(f"\n  Bronze Layer (with FOREIGN KEYs):")
print(f"    • sensor_bronze: {total_count:,} rows - FK→devices, FK→factories, FK→models")
print(f"    • inspection_bronze: {inspection_count:,} rows - FK→devices")
print(f"\n  Silver Layer:")
print(f"    • anomaly_detected: {anomaly_count:,} rows")
print(f"    • inspection_silver: {silver_count:,} rows")
print(f"\n  Gold Layer:")
print(f"    • inspection_gold: {gold_count:,} rows")
print(f"\n  System Tables (Synthetic for Training):")
print(f"    • system_billing - 30 days of billing data")
print(f"    • query_history - 500 query executions")
print(f"    • user_permissions - User access control")
print(f"    • audit_logs - 300 audit events")
print(f"\n📁 Data Volumes:")
print(f"    • {SENSOR_LANDING}")
print(f"    • {INSPECTION_LANDING}")
print(f"    • {CHECKPOINT_PATH}")
print(f"\n🔑 Data Model:")
print(f"    Star schema with fact tables (sensor_bronze, inspection_bronze)")
print(f"    referencing dimension tables (dim_devices, dim_factories, dim_models)")
print("\n" + "="*80)
print("Next steps: Query the tables or build dashboards on top of this data!".center(80))
print("="*80)
