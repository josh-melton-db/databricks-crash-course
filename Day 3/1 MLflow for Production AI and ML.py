# Databricks notebook source
# MAGIC %md
# MAGIC # MLflow for Production AI and ML
# MAGIC
# MAGIC ## The Scenario
# MAGIC
# MAGIC 🛩️ **Leadership just gave you the order:** Your team has IoT sensor data streaming in from aircraft engines across 5 factories. By the end of the week, you need to deploy a predictive model to identify potential defects before they cause failures. This notebook gets you from raw data to a production-ready model in 30 minutes.
# MAGIC
# MAGIC ## What You'll Learn
# MAGIC
# MAGIC ✅ **Experiment** - Track model training with MLflow autologging  
# MAGIC ✅ **Register** - Version control models in Unity Catalog  
# MAGIC ✅ **Predict** - Load and use models for batch inference  
# MAGIC
# MAGIC **Key Concepts:**
# MAGIC - **MLflow Tracking**: Automatically log parameters, metrics, and models
# MAGIC - **Unity Catalog Model Registry**: Enterprise-grade model versioning and governance
# MAGIC - **Model Aliases**: Tag models as "Champion" or "Challenger" for deployment
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **References:**
# MAGIC - [MLflow Tracking](https://docs.databricks.com/aws/en/mlflow/tracking)
# MAGIC - [Databricks Autologging](https://docs.databricks.com/aws/en/mlflow/databricks-autologging)
# MAGIC - [Unity Catalog Model Registry](https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle/index.html)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Why MLflow?
# MAGIC
# MAGIC Without MLflow, data scientists face challenges like:
# MAGIC - **Lost experiments** - "Which hyperparameters gave us that 95% accuracy?"
# MAGIC - **Model chaos** - "Where's the model we deployed last week?"
# MAGIC - **No reproducibility** - "I can't recreate these results"
# MAGIC
# MAGIC MLflow solves this by providing:
# MAGIC - **Experiment Tracking**: Automatic logging of parameters, metrics, and artifacts
# MAGIC - **Model Registry**: Centralized model versioning with Unity Catalog
# MAGIC - **Deployment**: Seamless path from experiment to production
# MAGIC
# MAGIC **The MLOps Workflow:**
# MAGIC ```
# MAGIC 1. EXPERIMENT → Train models, MLflow tracks everything
# MAGIC 2. REGISTER   → Save best model to Unity Catalog
# MAGIC 3. PREDICT    → Use model for batch or real-time inference
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup: Connect to IoT Data
# MAGIC
# MAGIC We'll use the sensor and inspection data from our aircraft engine monitoring system.

# COMMAND ----------

# Configuration - update with your catalog/schema
catalog = "josh_melton"  # Update to your catalog
schema = "default"       # Update to your schema

# Display available tables
print("Available IoT tables:")
tables = spark.sql(f"SHOW TABLES IN {catalog}.{schema}").filter("tableName LIKE '%sensor%' OR tableName LIKE '%inspection%'")
display(tables)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load and Prepare Training Data
# MAGIC
# MAGIC We'll join sensor readings with inspection results to create a labeled dataset for defect prediction.

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql.window import Window

# Load sensor and inspection data
sensor_df = spark.table(f"{catalog}.{schema}.sensor_bronze")
inspection_df = spark.table(f"{catalog}.{schema}.inspection_bronze")

# Join sensor data with inspection labels
# For each device, take the most recent sensor reading before each inspection
window_spec = Window.partitionBy("device_id").orderBy(F.col("sensor_timestamp").desc())

training_data = (
    sensor_df
    .withColumnRenamed("timestamp", "sensor_timestamp")
    .join(
        inspection_df.withColumnRenamed("timestamp", "inspection_timestamp"),
        ["device_id"]
    )
    .filter(F.col("sensor_timestamp") <= F.col("inspection_timestamp"))
    .withColumn("row_num", F.row_number().over(window_spec))
    .filter(F.col("row_num") == 1)
    .select(
        "device_id",
        "factory_id", 
        "model_id",
        "airflow_rate",
        "rotation_speed",
        "air_pressure",
        "temperature",
        "delay",
        "density",
        F.col("defect").cast("int").alias("defect")
    )
)

print(f"Training dataset size: {training_data.count():,} records")
print(f"Defect rate: {training_data.filter('defect = 1').count() / training_data.count() * 100:.2f}%")

display(training_data.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Convert to Pandas for Sklearn
# MAGIC
# MAGIC For this quick example, we'll use scikit-learn. For larger datasets, consider using Spark MLlib or distributed training.

# COMMAND ----------

import pandas as pd
from sklearn.model_selection import train_test_split

# Convert to Pandas
pdf = training_data.toPandas()

# Prepare features and target
feature_cols = ["airflow_rate", "rotation_speed", "air_pressure", "temperature", "delay", "density"]
X = pdf[feature_cols]
y = pdf["defect"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training set: {len(X_train):,} samples")
print(f"Test set: {len(X_test):,} samples")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1️⃣ EXPERIMENT: Train Model with MLflow Autologging
# MAGIC
# MAGIC **Key Point:** Use `mlflow.autolog()` to automatically track everything! No need to manually log parameters, metrics, or models.
# MAGIC
# MAGIC **What gets auto-logged:**
# MAGIC - Model architecture and parameters
# MAGIC - Training metrics (accuracy, precision, recall, etc.)
# MAGIC - Model artifacts
# MAGIC - Feature importances
# MAGIC - Training dataset signature

# COMMAND ----------

import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Enable autologging - this is the magic! ✨
mlflow.autolog()

# Train model - MLflow automatically tracks everything
with mlflow.start_run(run_name="IoT Defect Prediction - RF") as run:
    # Train Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    rf_model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = rf_model.predict(X_test)
    y_pred_proba = rf_model.predict_proba(X_test)[:, 1]
    
    # Calculate additional metrics (autolog captures most, but we can add custom ones)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"✅ Run ID: {run.info.run_id}")
    print(f"📊 Accuracy: {accuracy:.4f}")
    print(f"🎯 Precision: {precision:.4f}")
    print(f"🔍 Recall: {recall:.4f}")
    print(f"📈 F1 Score: {f1:.4f}")
    print(f"📉 AUC: {auc:.4f}")
    
    run_id = run.info.run_id

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🔍 Explore the Databricks MLflow UI
# MAGIC
# MAGIC **Click the "Experiment" button at the top right of this notebook** to open the MLflow UI. You'll see:
# MAGIC
# MAGIC 1. **Runs table** - All your experiments in one place
# MAGIC 2. **Parameters** - Hyperparameters used (n_estimators, max_depth, etc.)
# MAGIC 3. **Metrics** - Model performance (accuracy, precision, recall, etc.)
# MAGIC 4. **Artifacts** - Saved model files, feature importances, and more
# MAGIC 5. **Charts** - Visualize metric comparisons across runs
# MAGIC
# MAGIC Try clicking on your run to see all the details that were automatically logged!

# COMMAND ----------

# MAGIC %md
# MAGIC ## Train Another Model to Compare
# MAGIC
# MAGIC Let's train a Gradient Boosting model to compare performance.

# COMMAND ----------

from sklearn.ensemble import GradientBoostingClassifier

# Autologging is still enabled from earlier
with mlflow.start_run(run_name="IoT Defect Prediction - GBM") as run:
    # Train Gradient Boosting
    gbm_model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    gbm_model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = gbm_model.predict(X_test)
    y_pred_proba = gbm_model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"✅ Run ID: {run.info.run_id}")
    print(f"📊 Accuracy: {accuracy:.4f}")
    print(f"🎯 Precision: {precision:.4f}")
    print(f"🔍 Recall: {recall:.4f}")
    print(f"📈 F1 Score: {f1:.4f}")
    print(f"📉 AUC: {auc:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC 💡 **Pro Tip:** Go back to the MLflow UI and compare the two runs side-by-side. Which model performs better?

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2️⃣ REGISTER: Save Model to Unity Catalog
# MAGIC
# MAGIC The **Unity Catalog Model Registry** is your enterprise model store. It provides:
# MAGIC - **Versioning**: Every model update creates a new version
# MAGIC - **Lineage**: Track which data and code produced each model
# MAGIC - **Governance**: Control who can access and deploy models
# MAGIC - **Aliases**: Tag models as "Champion", "Challenger", "Staging", etc.

# COMMAND ----------

# Set the registry to Unity Catalog
mlflow.set_registry_uri("databricks-uc")

# Register the best model (using the Random Forest run_id from earlier)
model_name = f"{catalog}.{schema}.iot_defect_predictor"
model_uri = f"runs:/{run_id}/model"

print(f"📦 Registering model: {model_name}")
model_details = mlflow.register_model(model_uri=model_uri, name=model_name)

print(f"✅ Registered model version: {model_details.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Set Model Alias to "Champion"
# MAGIC
# MAGIC Model aliases let you tag specific versions for deployment (e.g., "Champion" for production, "Challenger" for testing).

# COMMAND ----------

from mlflow.tracking import MlflowClient

client = MlflowClient()

# Add model description
client.update_registered_model(
    name=model_name,
    description="Random Forest model to predict defects in aircraft engine IoT sensors. Trained on sensor readings (airflow, rotation speed, temperature, pressure) and inspection results."
)

# Set the "Champion" alias to this version
client.set_registered_model_alias(
    name=model_name,
    alias="Champion",
    version=model_details.version
)

print(f"✅ Model version {model_details.version} tagged as 'Champion'")

# COMMAND ----------

# MAGIC %md
# MAGIC 🎯 **View your model in Unity Catalog:**
# MAGIC 1. Click "Catalog" in the left sidebar
# MAGIC 2. Navigate to your catalog → schema → "iot_defect_predictor"
# MAGIC 3. See model versions, lineage, and metadata

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3️⃣ PREDICT: Load and Use the Model
# MAGIC
# MAGIC Load the "Champion" model and use it for predictions. This is how you'd use the model in production.

# COMMAND ----------

import mlflow.pyfunc

# Load the Champion model by alias
champion_model_uri = f"models:/{model_name}@Champion"
print(f"📥 Loading model from: {champion_model_uri}")

champion_model = mlflow.pyfunc.load_model(champion_model_uri)

print("✅ Model loaded successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Make Batch Predictions
# MAGIC
# MAGIC Use the loaded model to predict defects on new sensor data.

# COMMAND ----------

# Make predictions on test set
predictions = champion_model.predict(X_test)

# Create results DataFrame
results_df = pd.DataFrame({
    "actual_defect": y_test.values,
    "predicted_defect": predictions,
    "airflow_rate": X_test["airflow_rate"].values,
    "rotation_speed": X_test["rotation_speed"].values,
    "temperature": X_test["temperature"].values
})

print("🔮 Predictions:")
display(results_df.head(20))

# Calculate accuracy
accuracy = (results_df["actual_defect"] == results_df["predicted_defect"]).mean()
print(f"\n✅ Prediction Accuracy: {accuracy:.2%}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Mission Accomplished!
# MAGIC
# MAGIC **What you just did:**
# MAGIC 1. ✅ **EXPERIMENT** - Trained models with automatic MLflow tracking
# MAGIC 2. ✅ **REGISTER** - Saved the best model to Unity Catalog
# MAGIC 3. ✅ **PREDICT** - Loaded and used the model for inference
# MAGIC
# MAGIC **You're now ready to:**
# MAGIC - Show leadership you have a working predictive model ✨
# MAGIC - Deploy this model to production (see "Try This Out" below)
# MAGIC - Track model performance over time
# MAGIC - Iterate and improve with new versions

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🚀 Try This Out: Next Steps
# MAGIC
# MAGIC Now that you have the MLOps basics down, here are ways to level up:
# MAGIC
# MAGIC ### 1. Real-Time Model Serving
# MAGIC Deploy your model as a REST API endpoint:
# MAGIC ```python
# MAGIC # Enable Model Serving (UI: Machine Learning → Serving)
# MAGIC # Your model will be available at an API endpoint for real-time predictions
# MAGIC # Example: https://<workspace>.cloud.databricks.com/serving-endpoints/iot-defect-predictor/invocations
# MAGIC ```
# MAGIC
# MAGIC **Use cases:**
# MAGIC - Real-time defect detection as sensor data streams in
# MAGIC - Embed predictions in dashboards or operational tools
# MAGIC - Low-latency (<100ms) predictions
# MAGIC
# MAGIC **Learn more:** [Model Serving Documentation](https://docs.databricks.com/aws/en/machine-learning/model-serving/index.html)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 2. Streaming Predictions with Structured Streaming
# MAGIC Apply your model to streaming sensor data:
# MAGIC ```python
# MAGIC # Load model as UDF
# MAGIC predict_udf = mlflow.pyfunc.spark_udf(spark, model_uri=champion_model_uri)
# MAGIC
# MAGIC # Apply to streaming data
# MAGIC stream_df = spark.readStream.table("sensor_bronze")
# MAGIC predictions = stream_df.withColumn("predicted_defect", predict_udf(*feature_cols))
# MAGIC
# MAGIC # Write to output table
# MAGIC predictions.writeStream.table("sensor_predictions")
# MAGIC ```
# MAGIC
# MAGIC **Use cases:**
# MAGIC - Continuous monitoring of all devices
# MAGIC - Automated alerting when defects are predicted
# MAGIC - Real-time dashboards with predictions
# MAGIC
# MAGIC **Learn more:** [Structured Streaming + MLflow](https://docs.databricks.com/aws/en/structured-streaming/apply-ml-models.html)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 3. Model Monitoring and Drift Detection
# MAGIC Track model performance over time:
# MAGIC ```python
# MAGIC # Log inference data
# MAGIC mlflow.log_table(predictions, artifact_file="predictions.json")
# MAGIC
# MAGIC # Monitor for:
# MAGIC # - Data drift (are input features changing?)
# MAGIC # - Concept drift (is the defect pattern changing?)
# MAGIC # - Performance drift (is accuracy decreasing?)
# MAGIC ```
# MAGIC
# MAGIC **Learn more:** [Lakehouse Monitoring](https://docs.databricks.com/aws/en/lakehouse-monitoring/index.html)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 4. A/B Testing with Multiple Models
# MAGIC Compare "Champion" vs "Challenger" models in production:
# MAGIC ```python
# MAGIC # Tag new model as Challenger
# MAGIC client.set_registered_model_alias(model_name, "Challenger", new_version)
# MAGIC
# MAGIC # Route 90% traffic to Champion, 10% to Challenger
# MAGIC # Measure which performs better in production
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 5. Hyperparameter Tuning with Hyperopt
# MAGIC Automatically find the best parameters:
# MAGIC ```python
# MAGIC from hyperopt import fmin, tpe, hp, Trials
# MAGIC import mlflow
# MAGIC
# MAGIC def objective(params):
# MAGIC     with mlflow.start_run(nested=True):
# MAGIC         mlflow.autolog()
# MAGIC         model = RandomForestClassifier(**params)
# MAGIC         model.fit(X_train, y_train)
# MAGIC         return -accuracy_score(y_test, model.predict(X_test))
# MAGIC
# MAGIC search_space = {
# MAGIC     'n_estimators': hp.choice('n_estimators', [50, 100, 200]),
# MAGIC     'max_depth': hp.choice('max_depth', [5, 10, 15, 20])
# MAGIC }
# MAGIC
# MAGIC best_params = fmin(fn=objective, space=search_space, algo=tpe.suggest, max_evals=10)
# MAGIC ```
# MAGIC
# MAGIC **Learn more:** [Hyperparameter Tuning](https://docs.databricks.com/aws/en/machine-learning/automl-hyperparam-tuning/index.html)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 6. Feature Store for Reusable Features
# MAGIC Create a centralized feature repository:
# MAGIC ```python
# MAGIC from databricks.feature_store import FeatureStoreClient
# MAGIC
# MAGIC fs = FeatureStoreClient()
# MAGIC
# MAGIC # Create feature table
# MAGIC fs.create_table(
# MAGIC     name=f"{catalog}.{schema}.sensor_features",
# MAGIC     primary_keys=["device_id"],
# MAGIC     df=feature_df
# MAGIC )
# MAGIC
# MAGIC # Models automatically log feature dependencies
# MAGIC ```
# MAGIC
# MAGIC **Learn more:** [Feature Store](https://docs.databricks.com/aws/en/machine-learning/feature-store/index.html)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📚 Additional Resources
# MAGIC
# MAGIC - [MLflow Quickstart](https://docs.databricks.com/aws/en/mlflow/quick-start.html)
# MAGIC - [MLflow 3 Migration Guide](https://docs.databricks.com/aws/en/mlflow/mlflow-3-install.html)
# MAGIC - [Unity Catalog Model Registry](https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle/index.html)
# MAGIC - [Databricks Autologging](https://docs.databricks.com/aws/en/mlflow/databricks-autologging.html)
# MAGIC - [Model Deployment Guide](https://docs.databricks.com/aws/en/machine-learning/model-serving/index.html)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2024 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
