#!/usr/bin/env python3
"""
Script to remove data preparation section from AutoML notebook
"""
import json
import sys

def main():
    notebook_path = "/Users/josh.melton/Desktop/iot_time_series_analysis/Day 1/4 AutoML.ipynb"
    
    # Read the notebook
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    # Cell 0: Update intro
    nb['cells'][0]['source'] = [
        "# AutoML: Automated Machine Learning for Defect Prediction\n",
        "\n",
        "**Databricks AutoML** automatically builds machine learning models with minimal code. It tries multiple algorithms, tunes hyperparameters, and provides a leaderboard of the best models.\n",
        "\n",
        "## What You'll Learn\n",
        "\n",
        "✅ Run classification experiments to predict defects using the UI\n",
        "✅ Review model performance and metrics  \n",
        "✅ Deploy the best model for predictions  \n",
        "✅ Understand feature importance  \n",
        "✅ Use the Python API for programmatic workflows\n",
        "\n",
        "---\n",
        "\n",
        "## Use Case: Predicting Device Defects\n",
        "\n",
        "Your team needs to predict whether aircraft devices will have defects based on sensor readings. Leadership wants this model built quickly to help with:\n",
        "- **Preventive maintenance**: Identify devices at risk before failure\n",
        "- **Quality control**: Catch issues early in production\n",
        "- **Cost reduction**: Minimize downtime and repairs\n",
        "\n",
        "We'll use the `inspection_silver` table you created earlier with Lakeflow to train our model!\n",
        "\n",
        "---\n",
        "\n",
        "## Table of Contents\n",
        "\n",
        "1. [Understanding AutoML](#understanding)\n",
        "2. [Running Classification Experiment](#classification)\n",
        "3. [Reviewing Results](#results)\n",
        "4. [Using the Model](#using-model)\n",
        "5. [Try This Out: Regression Example](#regression)\n",
        "\n",
        "---\n",
        "\n",
        "**References:**\n",
        "- [AutoML Overview](https://docs.databricks.com/aws/en/machine-learning/automl/)\n",
        "- [Classification](https://docs.databricks.com/aws/en/machine-learning/automl/classification)\n",
        "- [Regression](https://docs.databricks.com/aws/en/machine-learning/automl/regression)\n"
    ]
    
    # Remove cells 5-12 (data preparation section and duplicate section) by clearing them
    for i in range(5, 13):
        nb['cells'][i]['source'] = []
    
    # Cell 3: Replace with new section 2
    nb['cells'][3]['source'] = [
        "## 2. Running Classification with AutoML <a id=\"classification\"></a>\n",
        "\n",
        "We'll use the `inspection_silver` table you created in the Lakeflow Designer notebook. This table has sensor features and a `defect` column that we'll predict.\n",
        "\n",
        "### Option 1: Using the UI (Recommended)\n",
        "\n",
        "1. Click **Machine Learning** in the left sidebar\n",
        "2. Click **AutoML** (or **Experiments** → **Create AutoML Experiment**)\n",
        "3. Configure the experiment:\n",
        "   - **Problem type**: Classification\n",
        "   - **Dataset**: Select your catalog → `db_crash_course` schema → `inspection_silver` table\n",
        "   - **Target column**: `defect`\n",
        "   - **Evaluation metric**: F1 Score (good for imbalanced classes)\n",
        "   - **Training framework**: LightGBM, XGBoost, sklearn (select all)\n",
        "   - **Advanced settings** → **Exclude columns**: Add `device_id` (IDs shouldn't be features)\n",
        "   - **Timeout**: 15-20 minutes\n",
        "4. Click **Start AutoML**\n",
        "\n",
        "AutoML will:\n",
        "- Automatically split your data into train/validation/test\n",
        "- Try multiple algorithms (Random Forest, XGBoost, LightGBM)\n",
        "- Tune hyperparameters for each\n",
        "- Generate a leaderboard and notebooks for each model\n",
        "\n",
        "☕ **Grab a coffee!** This will take 15-20 minutes. While it runs, you can move on to the next notebook and come back to review results.\n",
        "\n",
        "---\n",
        "\n",
        "### Option 2: Using Python API\n",
        "\n",
        "For folks who want programmatic control, you can also run AutoML via Python:\n"
    ]
    
    # Cell 4: Update Python API code
    nb['cells'][4] = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from databricks import automl\n",
            "\n",
            "# Run AutoML classification programmatically\n",
            "training_table = f\"{CATALOG}.{SCHEMA}.inspection_silver\"\n",
            "\n",
            "summary = automl.classify(\n",
            "    dataset=training_table,\n",
            "    target_col=\"defect\",\n",
            "    primary_metric=\"f1\",\n",
            "    timeout_minutes=20,\n",
            "    exclude_cols=[\"device_id\"],  # Exclude ID columns from features\n",
            "    experiment_name=f\"/Users/{spark.sql('SELECT current_user()').collect()[0][0]}/automl_defect_prediction\"\n",
            ")\n",
            "\n",
            "print(f\"✅ AutoML Complete!\")\n",
            "print(f\"Best trial F1 Score: {summary.best_trial.metrics['val_f1_score']:.4f}\")\n",
            "print(f\"Best trial Run ID: {summary.best_trial.mlflow_run_id}\")\n"
        ]
    }
    
    # Update section numbering for cells 13 and 16
    nb['cells'][13]['source'][0] = "## 3. Reviewing Results <a id=\"results\"></a>\n"
    nb['cells'][16]['source'][0] = "## 4. Using the Model for Predictions <a id=\"using-model\"></a>\n"
    
    # Update cell 22 (regression instructions)
    nb['cells'][22]['source'] = [
        "**Using the UI:**\n",
        "1. Create a new AutoML experiment\n",
        "2. Select **Regression** as problem type\n",
        "3. Choose your catalog → `db_crash_course` → `sensor_bronze` table\n",
        "4. Target column: `temperature`\n",
        "5. Metric: RMSE (Root Mean Squared Error)\n",
        "6. Exclude columns: `device_id`, `timestamp`\n",
        "7. Timeout: 15 minutes\n",
        "8. Start AutoML\n",
        "\n",
        "**Using Python API:**\n"
    ]
    
    # Update cell 23 (regression Python code)
    nb['cells'][23]['source'] = [
        "# Run AutoML for regression\n",
        "training_table = f\"{CATALOG}.{SCHEMA}.sensor_bronze\"\n",
        "\n",
        "summary_regression = automl.regress(\n",
        "    dataset=training_table,\n",
        "    target_col=\"temperature\",\n",
        "    primary_metric=\"rmse\",\n",
        "    timeout_minutes=15,\n",
        "    exclude_cols=[\"device_id\", \"timestamp\"],  # Exclude IDs and timestamps\n",
        "    experiment_name=f\"/Users/{spark.sql('SELECT current_user()').collect()[0][0]}/automl_temperature_prediction\"\n",
        ")\n",
        "\n",
        "print(f\"✅ Regression AutoML Complete!\")\n",
        "print(f\"Best trial RMSE: {summary_regression.best_trial.metrics['val_rmse']:.4f}\")\n",
        "print(f\"Best trial R²: {summary_regression.best_trial.metrics.get('val_r2_score', 'N/A')}\")\n"
    ]
    
    # Update cell 25 (summary)
    nb['cells'][25]['source'] = [
        "## Summary\n",
        "\n",
        "In this notebook, you learned:\n",
        "\n",
        "✅ **What is AutoML** - Automated machine learning workflow  \n",
        "✅ **Run classification** - Predict defects using the UI or Python API  \n",
        "✅ **Review results** - Understand metrics and feature importance  \n",
        "✅ **Deploy models** - Register and use models for predictions  \n",
        "✅ **Try regression** - Predict continuous values like temperature  \n",
        "\n",
        "### Key Takeaways:\n",
        "\n",
        "1. **AutoML automates** data preprocessing, feature engineering, model selection, and hyperparameter tuning\n",
        "2. **The UI approach** is fastest for getting started - just point it at your table\n",
        "3. **AutoML handles the details** - splitting data, trying algorithms, tuning parameters\n",
        "4. **F1 Score** is best for imbalanced classification problems (more non-defects than defects)\n",
        "5. **Feature importance** shows which sensor readings matter most for predictions\n",
        "6. **Model registration** makes models available for production use via MLflow\n",
        "\n",
        "### What AutoML Did For You:\n",
        "\n",
        "**Behind the scenes, AutoML:**\n",
        "- Split your data into train/validation/test sets\n",
        "- Handled missing values and data types\n",
        "- Tried multiple algorithms (Random Forest, XGBoost, LightGBM)\n",
        "- Tuned hyperparameters for each algorithm\n",
        "- Evaluated models with appropriate metrics\n",
        "- Generated notebooks showing all the code\n",
        "- Registered the best model to MLflow\n",
        "\n",
        "### Quick Wins for Your Team:\n",
        "\n",
        "Now you can tell leadership you've:\n",
        "- ✅ Built a defect prediction model (15 minutes of work!)\n",
        "- ✅ Identified which sensor readings predict failures\n",
        "- ✅ Registered a production-ready model\n",
        "- ✅ Generated notebooks with all the ML code\n",
        "\n",
        "### Next Steps:\n",
        "\n",
        "1. **Review the AutoML notebooks** - See what features mattered most\n",
        "2. **Register your best model** - Make it available for production\n",
        "3. **Build a dashboard** - Visualize predictions (next notebook!)\n",
        "4. **Set up Genie** - Let people ask questions about predictions\n",
        "5. **Create alerts** - Notify when high-risk devices are detected\n",
        "\n",
        "---\n",
        "\n",
        "**Additional Resources:**\n",
        "- [AutoML Documentation](https://docs.databricks.com/aws/en/machine-learning/automl/)\n",
        "- [MLflow Model Registry](https://docs.databricks.com/aws/en/mlflow/model-registry)\n",
        "- [Model Serving](https://docs.databricks.com/aws/en/machine-learning/model-serving/)\n"
    ]
    
    # Write the updated notebook
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print("✅ Notebook updated successfully!")
    print(f"   - Removed data preparation section (cells 3-10)")
    print(f"   - Updated section numbering")
    print(f"   - Updated regression example to use sensor_bronze directly")
    print(f"   - Updated summary section")

if __name__ == "__main__":
    main()

