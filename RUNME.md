# Databricks Crash Course: Getting Started Guide

This guide walks you through the complete setup and deployment of the IoT Time Series Analysis crash course using modern Databricks practices.

## What You'll Learn

By the end of this crash course, you'll understand:
- How to build declarative data pipelines with Python
- Infrastructure as code using Databricks Asset Bundles
- Time series analysis at scale with Tempo
- Data quality management with expectations
- Real-time monitoring with dashboards and alerts

## Prerequisites

Before you begin, ensure you have:

1. **Databricks Workspace Access**
   - Unity Catalog enabled workspace
   - Permissions to create catalogs, schemas, volumes, and pipelines
   - Access to a SQL Warehouse

2. **Local Development Environment**
   - Databricks CLI installed ([installation guide](https://docs.databricks.com/dev-tools/cli/install.html))
   - Git (to clone the repository)
   - Python 3.10+ (optional, for local development)

3. **Cluster Requirements**
   - Unity Catalog enabled ML Runtime cluster (DBR 15.4 ML recommended)
   - For the setup notebook only - pipelines run on Databricks serverless compute

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/josh-melton-db/databricks-crash-course.git
cd databricks-crash-course
```

### Step 2: Authenticate with Databricks

```bash
databricks auth login --host https://your-workspace-url.cloud.databricks.com
```

Follow the prompts to complete authentication. Your credentials will be saved for future commands.

### Step 3: Run the Setup Notebook

The setup notebook creates Unity Catalog resources and generates sample IoT data.

1. **Import the notebook to your workspace**
   ```bash
   databricks workspace import 00_setup.py /Users/your.email@company.com/iot_crash_course_setup -f PYTHON
   ```

2. **Open the notebook in Databricks UI**
   - Navigate to your workspace
   - Find the `iot_crash_course_setup` notebook
   - Attach it to a Unity Catalog-enabled cluster with ML Runtime 15.4

3. **Run the notebook**
   - Execute all cells in order
   - Note the catalog and schema names (you'll need these)
   - Wait for data generation (~1-2 minutes for ~400,000 rows)

**What the setup creates:**
- Unity Catalog schema
- Three volumes (sensor_bronze, inspection_bronze, iot_checkpoints)
- Sample IoT sensor and inspection data in CSV format

### Step 4: Get SQL Warehouse ID

You need a SQL Warehouse ID for dashboard and alert resources.

```bash
databricks warehouses list
```

Example output:
```
ID                                    Name              State
abc123def456ghi789                    Serverless SQL    RUNNING
```

Copy the ID (e.g., `abc123def456ghi789`).

### Step 5: Deploy with Asset Bundles

Deploy all resources (pipeline, dashboard, alert) with a single command:

```bash
databricks bundle deploy -t dev --var="warehouse_id=abc123def456ghi789"
```

**What this deploys:**
- **Declarative Pipeline**: All bronze/silver/gold tables with dependencies
- **Lakeview Dashboard**: Visualizations for defect rates and trends
- **SQL Alert**: Automated notifications for anomalies

**Optional customization:**

```bash
databricks bundle deploy -t dev \
  --var="warehouse_id=abc123def456ghi789" \
  --var="catalog=my_catalog" \
  --var="schema=my_custom_schema"
```

### Step 6: Run the Pipeline

Execute the pipeline to process your data:

```bash
databricks bundle run iot_anomaly_detection_pipeline -t dev
```

**Alternative: Run from UI**
1. Navigate to **Workflows** > **Lakeflow Pipelines**
2. Find `iot_anomaly_detection_<your-username>`
3. Click **Start**

**Pipeline execution:**
- **Bronze Layer**: Ingests raw CSV files using Auto Loader
- **Silver Layer**: Engineers time series features, detects anomalies
- **Gold Layer**: Aggregates metrics by device, factory, and model

Watch the execution graph in real-time to see data flowing through the pipeline!

### Step 7: Explore Results

**View the Dashboard**

1. Navigate to **Dashboards** 
2. Find `IoT Anomaly Detection - <your-username>`
3. Explore visualizations:
   - Defect rates by factory (bar chart)
   - Weekly inspection trends (stacked bars)
   - Temperature vs. defects (scatter plot)
   - Density vs. defects (scatter plot)

**Configure the Alert**

1. Navigate to **SQL** > **Alerts**
2. Find `IoT Anomaly Detection Alert - <your-username>`
3. Review the query (counts defects in last 10 minutes)
4. Click **Edit** to configure:
   - Add email recipients
   - Adjust threshold if needed
   - Set notification frequency
5. Click **Unmute** to activate

**Query the Tables**

Open a SQL editor and explore:

```sql
-- Bronze: Raw sensor data
SELECT * FROM <catalog>.<schema>.sensor_bronze LIMIT 10;

-- Silver: Anomalies detected
SELECT 
  device_id,
  timestamp,
  temperature,
  air_pressure,
  rotation_speed,
  delay
FROM <catalog>.<schema>.anomaly_detected 
WHERE timestamp > current_timestamp() - INTERVAL 1 DAY;

-- Gold: Defect rates by factory
SELECT 
  factory_id,
  SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) AS defect_count,
  SUM(count) AS total_count,
  ROUND(100.0 * SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) / SUM(count), 2) AS defect_rate_pct
FROM <catalog>.<schema>.inspection_gold
GROUP BY factory_id
ORDER BY defect_rate_pct DESC;
```

### Step 8: Test Incremental Processing

Learn how declarative pipelines handle incremental data:

1. **Import the insights notebook**
   ```bash
   databricks workspace import 04_actionable_insights.py /Users/your.email@company.com/iot_incremental_test -f PYTHON
   ```

2. **Run the notebook**
   - This lands ~10,000 additional rows in the volumes
   - No changes to existing data

3. **Re-run the pipeline**
   ```bash
   databricks bundle run iot_anomaly_detection_pipeline -t dev
   ```

4. **Observe the magic** ✨
   - Open the pipeline event logs
   - Notice **only new files** are processed by Auto Loader
   - Materialized views use optimized strategies:
     - `GROUP_AGGREGATE`: Only recompute changed groups
     - `PARTITION_OVERWRITE`: Only update affected partitions
   - Much faster than full reprocessing!

5. **Refresh the dashboard**
   - Metrics update with new data
   - Charts show additional data points

**Key learning:** Declarative pipelines automatically optimize for incremental processing. You don't write merge logic - the platform handles it!

## Understanding What You Built

### Pipeline Architecture

**Bronze Layer** (`src/bronze/`)
```python
@dp.table(name="sensor_bronze")
@dp.expect("valid pressure", "air_pressure > 0")
def sensor_bronze():
    return spark.readStream.format("cloudFiles").load(...)
```
- Streaming tables for continuous ingestion
- Auto Loader handles schema evolution
- Expectations flag data quality issues

**Silver Layer** (`src/silver/`)
```python
@dp.materialized_view(name="inspection_silver")
def inspection_silver():
    sensors_tsdf = TSDF(...).EMA("rotation_speed", window=5)
    return inspections_tsdf.asofJoin(sensors_tsdf).df
```
- Materialized views for complex transformations
- Tempo for time series operations
- As-of joins prevent data leakage

**Gold Layer** (`src/gold/`)
```python
@dp.materialized_view(name="inspection_gold")
def inspection_gold():
    return silver.groupBy(...).agg(...)
```
- Business-level aggregations
- Optimized incremental updates
- Ready for BI tools and dashboards

### Key Concepts

**Declarative vs Imperative**
- **Declarative**: Describe *what* you want (pipeline figures out *how*)
- **Imperative**: Explicitly code every step

**Streaming Tables vs Materialized Views**
- **Streaming Table**: Continuous processing, append-only semantics
- **Materialized View**: Batch processing, full CRUD operations

**Auto Loader Benefits**
- Processes only new files
- Handles schema changes gracefully
- Exactly-once processing guarantees

**Tempo for Time Series**
- Distributed processing of time series operations
- Built for PySpark scale
- Handles irregular timestamps and missing data

## Production Deployment

Ready to deploy to production?

### Step 1: Review Configuration

Edit `databricks.yml` prod target:
- Adjust cluster sizes for expected load
- Set notification recipients
- Configure catalog/schema for production

### Step 2: Deploy to Production

```bash
databricks bundle deploy -t prod \
  --var="warehouse_id=<prod-warehouse-id>" \
  --var="catalog=prod_catalog" \
  --var="schema=iot_production"
```

### Step 3: Validate

1. Run the pipeline in prod environment
2. Verify data quality in event logs
3. Test dashboard access for stakeholders
4. Confirm alert notifications work

### Step 4: Set Up Continuous Execution (Optional)

For real-time processing:
1. Open the pipeline in Databricks UI
2. Click **Settings**
3. Change **Pipeline Mode** to **Continuous**
4. Save and restart

Or schedule periodic execution:
```bash
# Configure in databricks.yml or create a separate job
databricks jobs create --json '{
  "name": "IoT Pipeline Scheduled",
  "schedule": {"quartz_cron_expression": "0 0 * * * ?", "timezone_id": "UTC"},
  "tasks": [{"pipeline_task": {"pipeline_id": "..."}}]
}'
```

## Configuration and Customization

### Environment Variables

Create `.env` file for easier configuration:

```bash
# Databricks workspace
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=<your-token>

# Deployment variables
warehouse_id=abc123def456
catalog=default
schema=iot_anomaly_detection_myname
```

Deploy without inline variables:
```bash
databricks bundle deploy -t dev
```

### Customizing the Pipeline

**Modify anomaly detection rules:**

Edit `src/silver/anomaly_detected.py`:
```python
bronze.where(
    ((col("delay") > 200) & (col("rotation_speed") > 900)) |  # Your thresholds
    (col("temperature") > 110) |
    ((col("density") > 5.0) & (col("air_pressure") < 800))
)
```

**Change time series features:**

Edit `src/silver/inspection_silver.py`:
```python
.EMA("rotation_speed", window=10)  # Different window size
.resample(freq="30 minutes", func="mean")  # Different granularity
```

**Add new tables:**

1. Create `src/silver/new_feature.py`:
```python
from pyspark import pipelines as dp

@dp.materialized_view(name="new_feature")
def new_feature():
    return spark.read.table("sensor_bronze").groupBy(...).agg(...)
```

2. Add to `databricks.yml`:
```yaml
libraries:
  - file:
      path: ./src/silver/new_feature.py
```

3. Redeploy:
```bash
databricks bundle deploy -t dev
```

### Using Your Own Data

Replace synthetic data with real IoT data:

1. **Update source paths** in `src/bronze/*.py`:
```python
sensor_landing = f"/Volumes/{catalog}/{schema}/my_real_sensors"
```

2. **Adjust schema hints**:
```python
schema_hints = "device_id string, timestamp timestamp, temperature float, ..."
```

3. **Modify feature engineering** in silver layer to match your use case

4. **Update business logic** in gold layer for your KPIs

## Troubleshooting

### Common Issues

**❌ Pipeline fails: "Schema not found"**

✅ **Solution:**
```bash
# Verify setup notebook ran successfully
databricks sql execute --warehouse-id <id> "SHOW SCHEMAS IN <catalog>"

# Check catalog/schema match in databricks.yml
grep -A 2 "catalog:" databricks.yml
```

**❌ Error: "Warehouse not found" during deployment**

✅ **Solution:**
```bash
# List available warehouses
databricks warehouses list

# Use a valid ID
databricks bundle deploy -t dev --var="warehouse_id=<correct-id>"
```

**❌ Pipeline runs but tables are empty**

✅ **Solution:**
1. Check data exists in volumes:
```bash
databricks fs ls /Volumes/<catalog>/<schema>/sensor_bronze/
```
2. Review event logs for dropped records
3. Check if expectations are too strict

**❌ Tempo errors in silver layer**

✅ **Solution:**
- Verify using ML Runtime (not standard Runtime)
- Check dbl-tempo>=0.1.30 in cluster libraries
- Review TSDF initialization - ensure timestamp column exists

**❌ Dashboard shows no data**

✅ **Solution:**
1. Verify pipeline completed successfully
2. Run query manually to test:
```sql
SELECT COUNT(*) FROM <catalog>.<schema>.inspection_gold;
```
3. Check table name replacements in dashboard JSON
4. Refresh the dashboard

### Validation Commands

**Check bundle configuration:**
```bash
databricks bundle validate -t dev
```

**List deployed resources:**
```bash
databricks bundle resources -t dev
```

**View pipeline status:**
```bash
databricks pipelines get <pipeline-id>
```

### Clean Up and Redeploy

If you need to start fresh:

```bash
# Destroy all bundle resources
databricks bundle destroy -t dev

# Optionally drop schema (loses all data!)
databricks sql execute --warehouse-id <id> "DROP SCHEMA <catalog>.<schema> CASCADE"

# Redeploy from scratch
databricks bundle deploy -t dev --var="warehouse_id=<id>"
```

## Next Steps in Your Learning

### Extend This Project

- **Add ML models**: Build predictive maintenance models using engineered features
- **Implement streaming**: Switch to continuous mode for real-time processing
- **Add more visualizations**: Enhance the dashboard with custom charts
- **Integrate external data**: Join with weather, maintenance logs, or production schedules

### Learn More Databricks Concepts

- **Unity Catalog**: Fine-grained access control and data governance
- **Photon**: Accelerated query engine for faster processing
- **Databricks SQL**: BI and analytics on your lakehouse
- **MLflow**: Experiment tracking and model deployment
- **Workflows**: Orchestrate complex data and ML pipelines

### Explore Advanced Topics

- **CDC (Change Data Capture)**: Track changes in source systems
- **SCD (Slowly Changing Dimensions)**: Handle historical data
- **Data Mesh**: Implement domain-oriented data architecture
- **Cost Optimization**: Monitor and optimize compute spend

## Additional Resources

### Official Documentation
- [Lakeflow Spark Declarative Pipelines](https://docs.databricks.com/aws/en/ldp/developer/python-dev)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/)
- [Tempo Library](https://databrickslabs.github.io/tempo/)
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/)

### Learning Resources
- [Databricks Academy](https://academy.databricks.com/)
- [Medallion Architecture Guide](https://www.databricks.com/glossary/medallion-architecture)
- [Data Engineering Best Practices](https://www.databricks.com/discover/data-engineering-best-practices)

### Community
- [Databricks Community Forums](https://community.databricks.com/)
- [GitHub Discussions](https://github.com/josh-melton-db/databricks-crash-course/discussions)

---

**Questions or Issues?**

File an issue: [databricks-crash-course/issues](https://github.com/josh-melton-db/databricks-crash-course/issues)

**Want to Contribute?**

Pull requests welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
