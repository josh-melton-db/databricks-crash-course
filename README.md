<img src=https://raw.githubusercontent.com/databricks-industry-solutions/.github/main/profile/solacc_logo.png width="600px">

[![DBR](https://img.shields.io/badge/DBR-15.4ML-red?logo=databricks&style=for-the-badge)](https://docs.databricks.com/release-notes/runtime/15.4lts-ml.html)
[![CLOUD](https://img.shields.io/badge/CLOUD-ALL-blue?logo=googlecloud&style=for-the-badge)](https://databricks.com/try-databricks)

## Databricks Crash Course: IoT Time Series Analysis

### Overview

This crash course teaches modern Databricks development practices through a real-world IoT time series analysis use case. You'll learn how to build production-grade data pipelines using the latest Databricks platform capabilities.

**What you'll learn:**
- **Lakeflow Spark Declarative Pipelines** for simplified, declarative ETL
- **Medallion Architecture** for organizing data transformations (bronze/silver/gold)
- **Time Series Analysis** at scale using the Tempo library
- **Infrastructure as Code** with Databricks Asset Bundles (DAB)
- **Data Quality Management** with pipeline expectations
- **Real-time Monitoring** with Lakeview Dashboards and SQL Alerts

### Use Case: Manufacturing IoT Analytics

The Internet of Things (IoT) generates massive volumes of data - IBM estimates approximately 175 zettabytes annually by 2025. This crash course demonstrates how manufacturing organizations can process and analyze IoT sensor data to:
- Detect equipment anomalies in real-time
- Predict maintenance needs before failures occur
- Monitor quality metrics across factories and devices
- Make data-driven operational decisions

### What's Modern in This Approach

This crash course showcases current Databricks best practices (as of December 2025):

✅ **Lakeflow Spark Declarative Pipelines**: Modern pipeline development using `pyspark.pipelines` module with Python source files (not notebooks)

✅ **Infrastructure as Code**: Complete deployment automation via Databricks Asset Bundles - version control everything

✅ **Latest Dependencies**: Databricks Runtime 15.4 ML with updated SDKs (databricks-sdk >=0.35.0, dbl-tempo >=0.1.30)

✅ **Source File Organization**: Clear separation of layers in dedicated Python files following software engineering practices

✅ **Declarative Data Quality**: Built-in expectations for data validation without custom code

## Reference Architecture
<img src='https://raw.githubusercontent.com/databricks-industry-solutions/iot_time_series_analysis/master/images/reference_arch.png?raw=true' width=800>

## Technical Deep Dive

### Pipeline Architecture

The pipeline follows the medallion architecture pattern with three distinct layers:

**Bronze Layer** (Raw Data Ingestion)
- `sensor_bronze.py`: IoT sensor measurements using Auto Loader for incremental file processing
- `inspection_bronze.py`: Defect inspection reports with data quality constraints

**Silver Layer** (Feature Engineering & Enrichment)
- `anomaly_detected.py`: Physics-based anomaly detection using domain rules
- `inspection_silver.py`: Time series feature engineering with Tempo (EMA, resampling, as-of joins)

**Gold Layer** (Business Aggregations)
- `inspection_gold.py`: Aggregated defect rates and metrics by device, factory, and model

### Key Technologies Explained

**Lakeflow Spark Declarative Pipelines**

The new standard for building data pipelines on Databricks:
- Declarative syntax using `@dp.table()` and `@dp.materialized_view()` decorators
- Automatic dependency resolution and optimization
- Built-in data quality with `@dp.expect()` decorators
- Source file-based development (not notebooks)

**Tempo for Time Series Operations**

Handles complex distributed time series computations:
- **Interpolation**: Fill gaps in irregular time series data
- **EMA (Exponential Moving Average)**: Smoothing and trend detection
- **As-of Joins**: Join records based on temporal proximity without data leakage
- **Resampling**: Aggregate to different time granularities
- **Parallelization**: Efficient processing across millions of time series

**Databricks Asset Bundles (DAB)**

Infrastructure as code for the Databricks platform:
- Version control all resources (pipelines, dashboards, alerts)
- Multi-environment deployment (dev/staging/prod)
- Reproducible infrastructure
- CI/CD integration ready

**Auto Loader**

Incremental file ingestion from cloud storage:
- Processes only new files as they arrive
- Schema inference and evolution
- Rescued data column for schema mismatches
- Checkpoint management for exactly-once processing

## Getting Started

### Prerequisites

- Unity Catalog enabled Databricks workspace
- Databricks CLI installed ([installation guide](https://docs.databricks.com/dev-tools/cli/install.html))
- Python 3.10+ (for local development)
- Access to create catalogs, schemas, and volumes in Unity Catalog
- A SQL Warehouse for dashboard and alerts

### Quick Start

1. **Clone this repository**
   ```bash
   git clone https://github.com/josh-melton-db/databricks-crash-course.git
   cd databricks-crash-course
   ```

2. **Authenticate with Databricks**
   ```bash
   databricks auth login --host https://your-workspace-url.cloud.databricks.com
   ```

3. **Import and run the setup notebook**
   - Import `00_setup.py` to your Databricks workspace
   - Attach to a Unity Catalog-enabled ML Runtime cluster (DBR 15.4 ML recommended)
   - Run the notebook to create schema, volumes, and generate sample data

4. **Get a SQL Warehouse ID**
   ```bash
   databricks warehouses list
   ```
   Copy the warehouse ID for dashboards and alerts.

5. **Deploy with Databricks Asset Bundles**
   ```bash
   # Deploy to development environment
   databricks bundle deploy -t dev --var="warehouse_id=<your-warehouse-id>"
   
   # Run the pipeline
   databricks bundle run iot_anomaly_detection_pipeline -t dev
   ```

6. **Explore the results**
   - Monitor the pipeline: **Workflows** > **Lakeflow Pipelines**
   - View the dashboard: **Dashboards** section
   - Configure alerts: **SQL** > **Alerts**

### Understanding the Code

#### Bronze Layer Example (`src/bronze/sensor_bronze.py`)

```python
from pyspark import pipelines as dp

@dp.table(name="sensor_bronze", comment="Raw sensor data")
@dp.expect("valid pressure", "air_pressure > 0")
def sensor_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaHints", schema_hints)
        .load(sensor_landing)
    )
```

**Key concepts:**
- `@dp.table()`: Creates a streaming table
- `@dp.expect()`: Data quality constraint (flags but doesn't drop)
- `cloudFiles`: Auto Loader format for incremental ingestion

#### Silver Layer Example (`src/silver/inspection_silver.py`)

```python
from tempo import TSDF

@dp.materialized_view(name="inspection_silver")
def inspection_silver():
    sensors_tsdf = (
        TSDF(raw_sensors, ts_col="timestamp", partition_cols=["device_id"])
        .EMA("rotation_speed", window=5)
        .resample(freq="1 hour", func="mean")
    )
    return inspections_tsdf.asofJoin(sensors_tsdf, right_prefix="sensor").df
```

**Key concepts:**
- `TSDF`: Tempo's time series DataFrame
- `.EMA()`: Exponential moving average
- `.asofJoin()`: Temporal join without future data leakage

### Deployment Targets

**Development (`dev`)**: 
- Fast iterations with smaller clusters
- PREVIEW channel for latest features
- Development mode for quick updates

**Production (`prod`)**:
- Production-ready configuration
- CURRENT channel for stability
- Larger clusters for scale

```bash
# Deploy to production
databricks bundle deploy -t prod \
  --var="warehouse_id=<warehouse-id>" \
  --var="catalog=prod_catalog" \
  --var="schema=iot_production"
```

### Testing Incremental Processing

Learn how the pipeline processes only new data:

1. Run `04_actionable_insights.py` notebook to land additional data
2. Re-run the pipeline
3. Check event logs - only new records processed
4. Observe optimized materialized view updates (GROUP_AGGREGATE, PARTITION_OVERWRITE)

This demonstrates how declarative pipelines automatically optimize incremental processing.

## Project Structure

```
iot_time_series_analysis/
├── databricks.yml              # Asset Bundle configuration
├── src/                        # Pipeline source files
│   ├── bronze/                 # Raw data ingestion layer
│   │   ├── sensor_bronze.py
│   │   └── inspection_bronze.py
│   ├── silver/                 # Feature engineering layer
│   │   ├── anomaly_detected.py
│   │   └── inspection_silver.py
│   └── gold/                   # Business aggregation layer
│       └── inspection_gold.py
├── resources/                  # Resource definitions
│   ├── dashboard.yml           # Lakeview dashboard config
│   └── alert.yml               # SQL alert config
├── util/                       # Helper utilities
│   ├── data_generator.py       # Synthetic data generation
│   └── onboarding_setup.py     # Setup helpers
├── config/                     # Dashboard templates
│   └── IOT Anomaly Detection.lvdash.json
├── 00_setup.py                 # Initial setup notebook
└── 04_actionable_insights.py   # Testing incremental loads
```

## Learning Path

### Module 1: Pipeline Basics
- Understand streaming tables vs materialized views
- Learn the medallion architecture pattern
- Write your first declarative pipeline

### Module 2: Data Quality
- Implement expectations for data validation
- Handle schema evolution with Auto Loader
- Use rescued data for error handling

### Module 3: Time Series at Scale
- Work with Tempo for time series operations
- Understand as-of joins and their applications
- Implement exponential moving averages

### Module 4: Infrastructure as Code
- Deploy pipelines with Asset Bundles
- Manage multi-environment configurations
- Version control your infrastructure

### Module 5: Monitoring & Alerting
- Build Lakeview dashboards
- Configure SQL alerts
- Monitor pipeline performance

## Advanced Topics

### Custom Data Sources

Replace synthetic data with your own:
1. Update volume paths in `src/bronze/` files
2. Adjust schema hints for your data structure
3. Modify feature engineering in `src/silver/`

### Adding New Transformations

Extend the pipeline:
1. Create new `.py` files in appropriate layer folders
2. Use `@dp.table()` or `@dp.materialized_view()` decorators
3. Add to `databricks.yml` libraries section
4. Redeploy: `databricks bundle deploy -t dev`

### Production Best Practices

- Use separate environments (dev/staging/prod)
- Implement data validation at each layer
- Monitor pipeline metrics and SLAs
- Set up alerting for failures
- Enable Unity Catalog data lineage

## Troubleshooting

**Pipeline execution fails**
- Check event logs in the pipeline UI
- Verify schema and volumes exist
- Confirm Runtime version is 15.4 ML or later

**No data in tables**
- Ensure CSV files in landing zones
- Review expectations - might be dropping all records
- Check file format matches schema hints

**Tempo errors**
- Verify dbl-tempo>=0.1.30 installed
- Confirm ML Runtime (required for Tempo)
- Review TSDF initialization parameters

## Additional Resources

- [Lakeflow Spark Declarative Pipelines Documentation](https://docs.databricks.com/aws/en/ldp/developer/python-dev)
- [Databricks Asset Bundles Guide](https://docs.databricks.com/dev-tools/bundles/)
- [Tempo Library Documentation](https://databrickslabs.github.io/tempo/)
- [Unity Catalog Best Practices](https://docs.databricks.com/data-governance/unity-catalog/best-practices.html)
- [Medallion Architecture Guide](https://www.databricks.com/glossary/medallion-architecture)

## Authors
josh.melton@databricks.com

## Project Support

Please note the code in this project is provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs). They are provided AS-IS and we do not make any guarantees of any kind. Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo. They will be reviewed as time permits, but there are no formal SLAs for support.

## License

&copy; 2025 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source].
