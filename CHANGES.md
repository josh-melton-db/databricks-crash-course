# Project Simplification - Changes Summary

## Overview

This project has been simplified from a Databricks Asset Bundles (DAB) deployment with Delta Live Tables to a single, self-contained notebook that creates all tables directly. This makes setup much easier - just "Run All" in a Databricks notebook!

## What Changed

### ✅ Added

- **`setup_and_run.py`**: New all-in-one notebook that:
  - Generates synthetic IoT data
  - Creates Unity Catalog schema and volumes
  - Creates all Bronze/Silver/Gold tables directly
  - No infrastructure deployment needed

### ❌ Removed

- **`databricks.yml`**: DAB configuration file (no longer needed)
- **`00_setup.py`**: Old setup notebook that referenced DAB deployment
- **`resources/`**: Dashboard and alert deployment configs
- **`config/`**: Dashboard JSON templates
- **`src/`**: DLT pipeline source files (bronze/silver/gold layers)
  - These used streaming DLT decorators (`@dp.table`, `@dp.materialized_view`)
  - Logic has been converted to regular Spark operations in the new notebook

### 📝 Updated

- **`README.md`**: Simplified to focus on notebook-based setup
- **`RUNME.md`**: Quick start guide for the new approach

### 🔄 Kept Unchanged

- **`util/`**: Data generation and setup utilities (still used by new notebook)
- **`legacy_notebooks/`**: Original DLT notebooks kept for reference
- **`requirements.txt`**: Python dependencies (unchanged)
- All documentation files (LICENSE, CONTRIBUTING, etc.)

## Migration Guide

### Old Approach (DAB + DLT)

```bash
# 1. Run setup notebook to create schema/volumes
# 2. Deploy with Asset Bundles
databricks bundle deploy -t dev --var="warehouse_id=xyz"
# 3. Run the DLT pipeline
databricks bundle run iot_anomaly_detection_pipeline -t dev
# 4. View dashboard in UI
```

### New Approach (Notebook Only)

```bash
# 1. Import setup_and_run.py to Databricks
# 2. Click "Run All"
# Done! Query the tables.
```

## Technical Changes

### Data Pipeline Conversion

**Old (DLT Streaming)**:
```python
from pyspark import pipelines as dp

@dp.table(name="sensor_bronze")
def sensor_bronze():
    return spark.readStream.format("cloudFiles").load(...)
```

**New (Batch)**:
```python
sensor_bronze_df = (
    spark.read
    .format("csv")
    .option("header", "true")
    .load(SENSOR_LANDING)
    .select(...)
)
sensor_bronze_df.write.format('delta').mode('overwrite').saveAsTable(...)
```

### Silver Layer Time Series

**Old (DLT Materialized View)**:
```python
@dp.materialized_view(name="inspection_silver")
def inspection_silver():
    sensors_tsdf = TSDF(...).EMA(...).resample(...)
    return inspections_tsdf.asofJoin(sensors_tsdf).df
```

**New (Direct DataFrame Operations)**:
```python
sensors_tsdf = TSDF(...).EMA("rotation_speed", window=5).resample(freq="1 hour", func="mean")
inspection_silver_df = inspections_tsdf.asofJoin(sensors_tsdf, right_prefix="sensor").df
inspection_silver_df.write.format('delta').mode('overwrite').saveAsTable(...)
```

## Why This Change?

### Benefits of New Approach

✅ **Simpler setup**: No CLI tools or deployment steps  
✅ **Faster learning**: All code in one place, easy to understand  
✅ **Self-contained**: No external dependencies or configurations  
✅ **Easier debugging**: Direct notebook execution, clear error messages  
✅ **Better for demos**: "Run All" and you're done

### Trade-offs

⚠️ **No incremental processing**: Tables are recreated each time (batch mode)  
⚠️ **No automatic scheduling**: DLT pipelines can run continuously  
⚠️ **No built-in monitoring**: DLT has built-in event logs and metrics  
⚠️ **No data quality tracking**: DLT expectations provide quality metrics  
⚠️ **Manual updates**: Need to re-run notebook to add more data

### When to Use Each Approach

**Use the new notebook approach if:**
- Learning Databricks and Unity Catalog
- Building demos or prototypes
- Want quick setup without infrastructure
- Working with static/batch datasets

**Consider DLT/DAB approach (legacy) if:**
- Building production pipelines
- Need continuous/streaming processing
- Want automatic incremental updates
- Require data quality monitoring
- Managing multiple environments (dev/staging/prod)

## Project Structure After Changes

```
iot_time_series_analysis/
├── setup_and_run.py           # 🆕 Main notebook - Run this!
├── README.md                   # ✏️ Updated
├── RUNME.md                    # ✏️ Updated  
├── CHANGES.md                  # 🆕 This file
├── requirements.txt            # ✓ Unchanged
├── util/                       # ✓ Unchanged (data generation)
│   ├── data_generator.py
│   └── onboarding_setup.py
├── legacy_notebooks/           # ✓ Reference only
│   ├── 01_data_ingestion.py
│   ├── 02_featurization.py
│   ├── 03_aggregated_metrics.py
│   └── 04_actionable_insights.py
└── images/                     # ✓ Unchanged
    └── reference_arch.png
```

## What You Get

Running `setup_and_run.py` creates:

### Unity Catalog Objects

**Schema**: `<catalog>.<schema>`  
**Volumes**: 
- `sensor_data` (CSV files with sensor readings)
- `inspection_data` (CSV files with inspection records)
- `checkpoints` (temporary storage)

**Tables**:
- `sensor_bronze` (~400k rows of sensor data)
- `inspection_bronze` (~1.6k inspection records)
- `anomaly_detected` (threshold-based anomalies)
- `inspection_silver` (time series features + as-of joins)
- `inspection_gold` (aggregated business metrics)

### Sample Data

- **60 IoT devices** across 5 factories
- **14 different equipment models**
- **1 year of data** (2023-01-01 to 2023-12-31)
- **Sensor metrics**: temperature, air pressure, rotation speed, airflow rate, density, delay
- **Realistic patterns**: seasonality, trends, noise, correlations
- **Simulated defects**: based on physical conditions

## Questions?

See README.md for detailed documentation or RUNME.md for a quick start guide.

For questions or issues, contact: josh.melton@databricks.com

