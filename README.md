<img src=https://raw.githubusercontent.com/databricks-industry-solutions/.github/main/profile/solacc_logo.png width="600px">

[![DBR](https://img.shields.io/badge/DBR-14.3ML-red?logo=databricks&style=for-the-badge)](https://docs.databricks.com/release-notes/runtime/14.3lts-ml.html)
[![CLOUD](https://img.shields.io/badge/CLOUD-ALL-blue?logo=googlecloud&style=for-the-badge)](https://databricks.com/try-databricks)

## IoT Time Series Analysis - Setup Script

### Overview

This project provides a simple, self-contained notebook for setting up an IoT time series analysis demo in Databricks. It demonstrates how to:
- Generate synthetic IoT sensor and inspection data
- Create Unity Catalog tables following the medallion architecture (Bronze/Silver/Gold)
- Perform time series analysis using the Tempo library
- Build complete analytics pipelines without infrastructure complexity

**Getting Started:**
Simply import `setup_and_run.py` into your Databricks workspace and click "Run All"!

### What You'll Get

After running the setup notebook, you'll have:

**Bronze Layer Tables (Raw Data)**
- `sensor_bronze`: IoT sensor readings with temperature, pressure, rotation speed, density, delay, airflow rate
- `inspection_bronze`: Defect inspection records

**Silver Layer Tables (Feature Engineering)**
- `anomaly_detected`: Threshold-based anomaly detection on sensor data
- `inspection_silver`: Time series features with exponential moving averages and as-of joins

**Gold Layer Tables (Business Metrics)**
- `inspection_gold`: Aggregated defect rates and metrics by device, factory, and model

**Data Volumes**
- Sample CSV files with ~400,000 sensor readings and ~1,600 inspection records
- Ready for incremental processing or further experimentation

### Use Case: Manufacturing IoT Analytics

The demo simulates IoT sensors on manufacturing equipment (jet engine turbines) that measure:
- **Temperature & Air Pressure**: Environmental conditions
- **Rotation Speed & Airflow Rate**: Operational metrics
- **Density**: Material properties
- **Delay**: Timing metrics

Inspection records flag potential defects, which are enriched with sensor data to build predictive features.

### Prerequisites

- Unity Catalog enabled Databricks workspace
- Databricks Runtime 14.3 ML or later (for Tempo library support)
- Permissions to create schemas, tables, and volumes in Unity Catalog

### Quick Start

1. **Import the notebook**
   - Download or clone this repository
   - Import `setup_and_run.py` into your Databricks workspace

2. **Configure (optional)**
   - Edit the `CATALOG` and `SCHEMA` variables at the top of the notebook
   - Adjust `NUM_ROWS` and `NUM_DEVICES` if you want more or less data

3. **Run All**
   - Attach the notebook to a Unity Catalog-enabled cluster with ML Runtime 14.3+
   - Click "Run All" and wait 3-5 minutes
   - All tables and data will be created automatically

4. **Query the results**
   ```sql
   -- View bronze sensor data
   SELECT * FROM <catalog>.<schema>.sensor_bronze LIMIT 10;
   
   -- Check anomalies detected
   SELECT * FROM <catalog>.<schema>.anomaly_detected 
   ORDER BY timestamp DESC LIMIT 20;
   
   -- Analyze defect rates by factory
   SELECT 
     factory_id,
     SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) as defects,
     SUM(count) as total_inspections,
     ROUND(100.0 * SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) / SUM(count), 2) as defect_rate_pct
   FROM <catalog>.<schema>.inspection_gold
   GROUP BY factory_id
   ORDER BY defect_rate_pct DESC;
   ```

### What's Happening Under the Hood

**Data Generation**
- Synthetic time series data with realistic patterns (seasonality, trends, noise)
- Simulated defects based on physical conditions (high temperature + pressure, high rotation speed, etc.)
- Intentional data quality issues (missing values, negative pressures) to demonstrate handling

**Bronze Layer**
- Raw CSV files loaded from Unity Catalog volumes
- Minimal transformations, preserving original data
- Schema enforcement with type casting

**Silver Layer**
- **Data Quality**: Fix negative air pressure values, drop invalid records
- **Anomaly Detection**: Apply threshold-based rules to flag potential issues
- **Time Series Features**: 
  - Exponential moving averages (EMA) on rotation speed
  - Resampling to hourly intervals
  - As-of joins to prevent data leakage (attach most recent sensor reading BEFORE each inspection)

**Gold Layer**
- Business-level aggregations by device, factory, model, and defect status
- Average sensor metrics for each group
- Ready for dashboards and BI tools

### Key Technologies

**Tempo Library**

Distributed time series operations at scale:
- `TSDF`: Time Series DataFrames for temporal operations
- `.EMA()`: Exponential moving averages
- `.resample()`: Aggregate to different time granularities
- `.asofJoin()`: Join records based on temporal proximity without future data leakage

**Unity Catalog**

Centralized governance for data and AI assets:
- Fine-grained access control
- Data lineage tracking
- Cross-workspace sharing
- Volumes for file storage with governance

**Medallion Architecture**

Organize data transformations in layers:
- **Bronze**: Raw data, minimal processing
- **Silver**: Cleaned, enriched, feature-engineered data
- **Gold**: Business-level aggregations and metrics

### Project Structure

```
iot_time_series_analysis/
├── setup_and_run.py           # Main setup notebook (Run this!)
├── util/
│   ├── data_generator.py       # Synthetic data generation functions
│   └── onboarding_setup.py     # Setup helper functions
├── legacy_notebooks/           # Original DLT pipeline notebooks (reference)
│   ├── 01_data_ingestion.py
│   ├── 02_featurization.py
│   ├── 03_aggregated_metrics.py
│   └── 04_actionable_insights.py
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

### Extending This Demo

**Add More Data**

Run the data generation functions again to append more records:

```python
from util.data_generator import land_more_data
from util.onboarding_setup import dgconfig, new_data_config

# Generate new data with different parameters
new_config = new_data_config(dgconfig, rows=50000, devices=20)
land_more_data(spark, dbutils, config, new_config)

# Re-read and recreate tables to include new data
```

**Customize Features**

Edit the time series feature engineering in the silver layer:
- Change EMA window sizes
- Try different resampling frequencies
- Add new Tempo operations (interpolation, FFT, etc.)

**Build Dashboards**

Create Lakeview dashboards or SQL dashboards on top of the gold layer:
- Defect trends over time
- Factory performance comparison
- Device-level anomaly tracking
- Temperature vs defect correlation

**Add Machine Learning**

Use the silver layer features to train predictive models:
- Binary classification for defect prediction
- Anomaly detection with autoencoders
- Time series forecasting for maintenance scheduling

### Sample Queries

**Find recent anomalies:**
```sql
SELECT device_id, factory_id, timestamp, temperature, rotation_speed, density
FROM <catalog>.<schema>.anomaly_detected
ORDER BY timestamp DESC
LIMIT 20;
```

**Defect rate by model:**
```sql
SELECT 
  model_id,
  SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) as defects,
  SUM(count) as total,
  ROUND(100.0 * SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) / SUM(count), 2) as defect_pct
FROM <catalog>.<schema>.inspection_gold
GROUP BY model_id
ORDER BY defect_pct DESC;
```

**Average temperature for defective vs non-defective:**
```sql
SELECT 
  defect,
  COUNT(*) as inspection_count,
  AVG(average_temperature) as avg_temp,
  AVG(average_rotation_speed) as avg_rotation,
  AVG(average_air_pressure) as avg_pressure
FROM <catalog>.<schema>.inspection_gold
GROUP BY defect;
```

### Troubleshooting

**Issue: "Catalog not found"**
- Verify you have access to the specified catalog
- Try using `catalog = 'main'` or another accessible catalog

**Issue: "Tempo import errors"**
- Ensure you're using ML Runtime (not standard Runtime)
- Verify dbl-tempo>=0.1.30 is installed (the notebook installs it automatically)

**Issue: "Out of memory during data generation"**
- Reduce `NUM_ROWS` and `NUM_DEVICES` parameters
- Use a cluster with more memory

**Issue: "Tables exist but are empty"**
- Check that CSV files were created in the volumes
- Verify no filters or expectations are dropping all records
- Look for errors in the notebook output

### Additional Resources

- [Tempo Library Documentation](https://databrickslabs.github.io/tempo/)
- [Unity Catalog Guide](https://docs.databricks.com/data-governance/unity-catalog/)
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [Time Series Analysis on Databricks](https://www.databricks.com/blog/2021/04/06/fine-grained-time-series-forecasting-at-scale-with-facebook-prophet-and-apache-spark-updated-for-spark-3.html)

### Legacy Notebooks

The `legacy_notebooks/` directory contains the original DLT pipeline approach with separate notebooks for each layer. These are kept for reference but are not needed for the simplified setup.

## Authors
josh.melton@databricks.com

## Project Support

Please note the code in this project is provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs). They are provided AS-IS and we do not make any guarantees of any kind. Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo. They will be reviewed as time permits, but there are no formal SLAs for support.

## License

&copy; 2025 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source].
