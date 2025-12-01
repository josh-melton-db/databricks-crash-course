# Databricks notebook source
# MAGIC %md
# MAGIC ### 0. Setup
# MAGIC 
# MAGIC This notebook prepares your environment for the IoT Time Series Analysis solution accelerator. It will:
# MAGIC - Create the required Unity Catalog schema and volumes
# MAGIC - Generate and land initial sample IoT sensor and inspection data
# MAGIC - Provide instructions for deploying the DLT pipeline using Databricks Asset Bundles
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Unity Catalog enabled workspace
# MAGIC - Machine Learning Runtime cluster (DBR 14.3 ML or later recommended)
# MAGIC - Databricks CLI installed locally for DAB deployment
# MAGIC
# MAGIC **After running this notebook:**
# MAGIC 1. From your local terminal, navigate to the project directory
# MAGIC 2. Run `databricks bundle deploy -t dev` to deploy the DLT pipeline, dashboard, and alert
# MAGIC 3. Run the deployed DLT pipeline from the Databricks UI
# MAGIC 4. View the dashboard and configure the alert

# COMMAND ----------

# DBTITLE 1,Install Dependencies
# MAGIC %pip install databricks-sdk>=0.35.0 dbl-tempo>=0.1.30 -q
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Import Required Modules
from util.onboarding_setup import set_config_for_bundle, reset_tables, dgconfig
from util.data_generator import land_more_data

# COMMAND ----------

# DBTITLE 1,Configure and Reset Environment
# Set your catalog and schema (or use defaults)
# Modify these parameters to use a different catalog/schema
config = set_config_for_bundle(
    dbutils,
    catalog='default',  # Change this to use a different catalog
    schema=None  # Leave as None to auto-generate schema name, or specify a custom schema
)

print(f"Configuration:")
print(f"  Catalog: {config['catalog']}")
print(f"  Schema: {config['schema']}")
print(f"  Sensor landing zone: {config['sensor_landing']}")
print(f"  Inspection landing zone: {config['inspection_landing']}")

# Reset schema and create volumes
# WARNING: This will drop and recreate the schema, deleting all existing data
reset_tables(spark, config, dbutils)

# COMMAND ----------

# DBTITLE 1,Generate and Land Initial Data
print('Generating initial IoT data...')
print(f"This will create approximately {dgconfig['shared']['num_rows']:,} rows of sensor data")
print(f"for {dgconfig['shared']['num_devices']} devices")

land_more_data(spark, dbutils, config, dgconfig)

print('\nInitial data generation complete!')
print(f"Sensor data landed in: {config['sensor_landing']}")
print(f"Inspection data landed in: {config['inspection_landing']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC ### 1. Deploy the Pipeline with Databricks Asset Bundles
# MAGIC
# MAGIC From your local terminal, navigate to the project directory and run:
# MAGIC
# MAGIC ```bash
# MAGIC # Authenticate with Databricks (if not already authenticated)
# MAGIC databricks auth login --host <your-workspace-url>
# MAGIC
# MAGIC # Deploy the bundle (pipeline, dashboard, and alert)
# MAGIC databricks bundle deploy -t dev
# MAGIC ```
# MAGIC
# MAGIC You'll need to provide a SQL Warehouse ID for the dashboard and alert. You can find warehouse IDs by running:
# MAGIC ```bash
# MAGIC databricks warehouses list
# MAGIC ```
# MAGIC
# MAGIC Then deploy with the warehouse ID:
# MAGIC ```bash
# MAGIC databricks bundle deploy -t dev --var="warehouse_id=<your-warehouse-id>"
# MAGIC ```
# MAGIC
# MAGIC ### 2. Run the DLT Pipeline
# MAGIC
# MAGIC After deployment, start the pipeline:
# MAGIC ```bash
# MAGIC databricks bundle run iot_anomaly_detection_pipeline -t dev
# MAGIC ```
# MAGIC
# MAGIC Or navigate to the Databricks UI:
# MAGIC - Go to **Workflows** > **Delta Live Tables**
# MAGIC - Find your pipeline (named `iot_anomaly_detection_<your-username>`)
# MAGIC - Click **Start** to run the pipeline
# MAGIC
# MAGIC ### 3. View Results
# MAGIC
# MAGIC - **Dashboard**: Navigate to **Dashboards** and find `IoT Anomaly Detection - <your-username>`
# MAGIC - **Alert**: Navigate to **SQL** > **Alerts** to configure notification recipients
# MAGIC - **Tables**: Query the tables in your schema to explore the data
# MAGIC
# MAGIC ### 4. Land More Data (Optional)
# MAGIC
# MAGIC To test incremental processing, run notebook **04_actionable_insights** to land additional data,
# MAGIC then re-run your DLT pipeline to process only the new records.
# MAGIC
# MAGIC ### Configuration
# MAGIC
# MAGIC Your configuration has been saved and will be used by the DLT pipeline via DAB variables.
# MAGIC The pipeline will automatically use:
# MAGIC - Catalog: `{config['catalog']}`
# MAGIC - Schema: `{config['schema']}`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Troubleshooting
# MAGIC
# MAGIC **Issue: "Schema not found" during pipeline run**
# MAGIC - Ensure you ran this setup notebook first
# MAGIC - Verify the catalog and schema names match in your DAB configuration
# MAGIC
# MAGIC **Issue: "Warehouse not found" during dashboard deployment**
# MAGIC - Provide a valid warehouse_id when deploying: `--var="warehouse_id=<id>"`
# MAGIC - Or create a `.env` file with `warehouse_id=<your-id>`
# MAGIC
# MAGIC **Issue: Pipeline fails with Tempo errors**
# MAGIC - Ensure you're using a cluster with dbl-tempo>=0.1.30 installed
# MAGIC - The pipeline configuration includes this dependency automatically
# MAGIC
# MAGIC **Issue: No data in tables after pipeline runs**
# MAGIC - Check that CSV files exist in the landing zones (volumes)
# MAGIC - Review DLT event logs for any data quality issues
# MAGIC - Verify expectations aren't dropping all records

# COMMAND ----------


