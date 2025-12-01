# IoT Time Series Analysis - Quick Start Guide

This guide gets you up and running with the IoT Time Series Analysis demo in under 10 minutes.

## What You'll Build

A complete IoT analytics pipeline with:
- **400,000+ sensor readings** from 60 simulated IoT devices
- **Bronze/Silver/Gold tables** in Unity Catalog
- **Time series features** using the Tempo library
- **Anomaly detection** based on physics-based rules
- **Business metrics** aggregated by device, factory, and model

## Prerequisites

✅ Databricks workspace with Unity Catalog enabled  
✅ ML Runtime cluster (DBR 14.3 ML or later)  
✅ Permissions to create schemas, tables, and volumes

## Setup Steps

### 1. Import the Notebook

Download or clone this repository, then import `setup_and_run.py` into your Databricks workspace:

```bash
# Option 1: Use Databricks CLI
databricks workspace import setup_and_run.py /Users/your.email@company.com/iot_setup

# Option 2: Use the UI
# Navigate to Workspace → Import → Upload the file
```

### 2. Configure (Optional)

Open the notebook and edit these parameters if needed:

```python
CATALOG = 'default'  # Change to your catalog
SCHEMA = None        # Leave as None to auto-generate
NUM_ROWS = 400000    # Number of sensor readings
NUM_DEVICES = 60     # Number of IoT devices
```

### 3. Run the Notebook

1. Attach the notebook to a cluster with **ML Runtime 14.3+**
2. Click **Run All**
3. Wait 3-5 minutes for completion

The notebook will:
- ✅ Install required libraries (databricks-sdk, dbl-tempo)
- ✅ Create Unity Catalog schema and volumes
- ✅ Generate synthetic IoT data
- ✅ Create Bronze/Silver/Gold tables
- ✅ Display summary statistics

### 4. Verify Setup

Check that tables were created:

```sql
-- List all tables
SHOW TABLES IN <catalog>.<schema>;

-- Should see:
-- sensor_bronze
-- inspection_bronze
-- anomaly_detected
-- inspection_silver
-- inspection_gold
```

Query the data:

```sql
-- Bronze: Raw sensor data
SELECT * FROM <catalog>.<schema>.sensor_bronze LIMIT 10;

-- Silver: Anomalies detected
SELECT COUNT(*) as anomaly_count 
FROM <catalog>.<schema>.anomaly_detected;

-- Gold: Aggregated metrics
SELECT * FROM <catalog>.<schema>.inspection_gold 
ORDER BY count DESC LIMIT 10;
```

## What Did I Just Create?

### Bronze Layer (Raw Data)

**`sensor_bronze`**: ~400,000 sensor readings
- device_id, trip_id, factory_id, model_id
- timestamp, temperature, air_pressure
- rotation_speed, airflow_rate, density, delay

**`inspection_bronze`**: ~1,600 inspection records
- device_id, timestamp, defect (0 or 1)

### Silver Layer (Feature Engineering)

**`anomaly_detected`**: Threshold-based anomaly detection
- Flags readings with extreme values:
  - High delay + high rotation speed
  - Excessive temperature
  - High density + low air pressure

**`inspection_silver`**: Time series features
- Exponential moving average on rotation speed
- Hourly resampling of sensor data
- As-of join (attach most recent sensor data to each inspection)

### Gold Layer (Business Metrics)

**`inspection_gold`**: Aggregated metrics
- Grouped by: device_id, factory_id, model_id, defect
- Average temperature, density, delay, rotation speed, air pressure
- Inspection counts

## Next Steps

### Explore the Data

**Defect rates by factory:**
```sql
SELECT 
  factory_id,
  SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) as defects,
  SUM(count) as total_inspections,
  ROUND(100.0 * SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) / SUM(count), 2) as defect_rate_pct
FROM <catalog>.<schema>.inspection_gold
GROUP BY factory_id
ORDER BY defect_rate_pct DESC;
```

**Recent anomalies:**
```sql
SELECT device_id, factory_id, model_id, timestamp, temperature, rotation_speed
FROM <catalog>.<schema>.anomaly_detected
ORDER BY timestamp DESC
LIMIT 20;
```

**Temperature distribution:**
```sql
SELECT 
  FLOOR(temperature / 10) * 10 as temp_bucket,
  COUNT(*) as reading_count
FROM <catalog>.<schema>.sensor_bronze
WHERE temperature IS NOT NULL
GROUP BY temp_bucket
ORDER BY temp_bucket;
```

### Build Dashboards

Create visualizations on the gold layer:

1. Navigate to **Dashboards** → **Create Dashboard**
2. Add visualizations:
   - Bar chart: Defect rates by factory
   - Line chart: Temperature trends over time
   - Scatter plot: Temperature vs defect correlation
3. Use queries from the "Explore the Data" section above

### Add More Data

Generate additional data to test incremental processing:

```python
# In a new notebook cell
from util.data_generator import land_more_data
from util.onboarding_setup import dgconfig, new_data_config

# Generate 50,000 more rows for 20 devices
new_config = new_data_config(dgconfig, rows=50000, devices=20)
land_more_data(spark, dbutils, config, new_config)

# Re-run the table creation cells to include new data
```

### Experiment with Time Series Features

Try different Tempo operations in the `inspection_silver` logic:

```python
# Different EMA window
sensors_tsdf.EMA("rotation_speed", window=10)

# Different resampling frequency
sensors_tsdf.resample(freq="30 minutes", func="mean")

# Add interpolation for missing values
sensors_tsdf.interpolate("temperature", method="linear")
```

## Understanding the Code

### Time Series Operations (Tempo)

The notebook uses Tempo for distributed time series analysis:

```python
from tempo import TSDF

# Create Time Series DataFrame
sensors_tsdf = TSDF(
    raw_sensors,
    ts_col="timestamp",
    partition_cols=["device_id", "trip_id", "factory_id", "model_id"]
)

# Apply operations
sensors_tsdf = (
    sensors_tsdf
    .EMA("rotation_speed", window=5)      # Exponential moving average
    .resample(freq="1 hour", func="mean")  # Resample to hourly
)

# As-of join (temporal join without future data)
result = inspections_tsdf.asofJoin(sensors_tsdf, right_prefix="sensor")
```

**Key Concept: As-of Join**
- Attaches the most recent sensor reading that occurred BEFORE each inspection
- Prevents data leakage (don't use future data to predict the past)
- Critical for building valid predictive models

### Medallion Architecture

**Bronze (Raw)**: Ingest as-is, minimal processing
- Preserve original data
- Handle schema evolution
- Flag data quality issues

**Silver (Enriched)**: Clean, transform, enrich
- Fix data quality problems
- Engineer features
- Join related datasets

**Gold (Aggregated)**: Business-level metrics
- Aggregate by key dimensions
- Pre-compute common queries
- Optimize for BI tools

## Troubleshooting

### "Catalog not found" error

**Solution**: Use a different catalog or create one
```sql
CREATE CATALOG my_catalog;
```

Then update the notebook:
```python
CATALOG = 'my_catalog'
```

### "Module tempo not found" error

**Solution**: Ensure you're using ML Runtime, not standard Runtime
- In cluster configuration, select "Machine Learning" runtime
- The notebook installs tempo automatically, but it requires ML dependencies

### "Out of memory" during data generation

**Solution**: Reduce the data volume
```python
NUM_ROWS = 100000   # Smaller dataset
NUM_DEVICES = 20    # Fewer devices
```

### Tables created but empty

**Solution**: Check volumes have data
```python
display(dbutils.fs.ls(f"/Volumes/{CATALOG}/{SCHEMA}/sensor_data"))
```

If empty, re-run the "Generate and Land Data" cells.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Unity Catalog                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Volumes (CSV Files)           Tables (Delta)              │
│  ┌──────────────────┐         ┌────────────────────────┐  │
│  │ sensor_data/     │────────▶│ sensor_bronze         │  │
│  │ inspection_data/ │─┐       │ inspection_bronze     │  │
│  └──────────────────┘ │       └───────────┬────────────┘  │
│                       │                   │               │
│                       │       ┌───────────▼────────────┐  │
│                       └──────▶│ inspection_silver     │  │
│                               │ anomaly_detected      │  │
│                               └───────────┬────────────┘  │
│                                           │               │
│                               ┌───────────▼────────────┐  │
│                               │ inspection_gold       │  │
│                               └────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## What's Next?

### Learn More About:

- **Time Series Analysis**: [Tempo Documentation](https://databrickslabs.github.io/tempo/)
- **Unity Catalog**: [Governance Guide](https://docs.databricks.com/data-governance/unity-catalog/)
- **Medallion Architecture**: [Best Practices](https://www.databricks.com/glossary/medallion-architecture)

### Extend This Demo:

- Build machine learning models on the silver layer features
- Create real-time streaming pipelines
- Integrate with external data sources
- Deploy dashboards for stakeholders

## Questions or Issues?

- Check the main README.md for detailed documentation
- File issues on the GitHub repository
- Contact: josh.melton@databricks.com

---

**That's it!** You now have a complete IoT analytics pipeline in Unity Catalog. Start querying, building dashboards, or extending the demo with your own use cases.
