# Day 1: Data Analytics & Exploration

## Overview

Master the fundamentals of Databricks through hands-on exercises. Progress from UI-based tools to code-based analysis, building dashboards and ML models along the way.

## Prerequisites

✅ Complete [setup](../setup/) to create training environment with IoT manufacturing data

## Schedule

| Time | Session | Topics |
|------|---------|--------|
| 8:30 | Databricks Introduction | Platform overview, workspace navigation, Unity Catalog basics |
| 9:30 | Lakeflow Designer | Visual query building, AI-powered SQL generation |
| 10:30 | Dashboards & Genie Overview | Dashboard creation, AI chat with data |
| 12:00 | *Lunch Break* | |
| 1:00 | AutoML | No-code ML model training and evaluation |
| 2:00 | Notebooks & Data Exploration | Python/SQL coding, AI Assistant |
| 3:00 | Data Transformation | Building ETL pipelines |

## Session Details

### 1. Databricks Introduction (8:30-9:30)

**Learning Objectives:**
- Navigate the Databricks workspace
- Understand the three-level namespace (catalog.schema.table)
- Explore Unity Catalog tables and volumes
- Run your first SQL queries

**Notebook:** `01_databricks_introduction.py`

**Topics Covered:**
- Workspace layout (Data, Workspace, Compute, Workflows)
- Unity Catalog data explorer
- SQL Editor basics
- Running queries on IoT data
- Understanding star schema (dimensions + facts)

**Hands-On:**
- Query dimension tables (factories, models, devices)
- Explore sensor and inspection data
- Join fact tables with dimensions
- Calculate basic metrics

---

### 2. Lakeflow Designer (9:30-10:30)

**Learning Objectives:**
- Use visual query builder
- Generate SQL with AI assistance
- Save queries as datasets
- Understand query optimization

**Notebook:** `02_lakeflow_designer.py`

**Topics Covered:**
- Lakeflow Designer interface (preview feature)
- Drag-and-drop query building
- AI-powered query suggestions
- Creating reusable datasets
- Previewing results

**Hands-On:**
- Build query joining sensors with device/factory info
- Use AI to generate aggregation queries
- Create dataset: "Device Performance Metrics"
- Save for use in dashboard session

---

### 3. Dashboards and Genie Overview (10:30-12:00)

**Learning Objectives:**
- Create interactive dashboards
- Use saved queries as datasets
- Chat with data using Genie
- Share insights with stakeholders

**Notebook:** `03_dashboards_genie_overview.py`

**Topics Covered:**
- Lakeview dashboard creation
- Visualization types (charts, tables, maps)
- Dashboard parameters and filters
- Genie AI chat interface
- Natural language data queries

**Hands-On:**
- Create dashboard using Lakeflow Designer datasets
- Add charts: defect rate by factory, temperature trends
- Ask Genie: "Which factory has the highest defect rate?"
- Share dashboard with team

---

### 4. AutoML (1:00-2:00)

**Learning Objectives:**
- Train ML models without code
- Evaluate model performance
- Understand feature importance
- Register models in Unity Catalog

**Notebook:** `04_automl.py`

**Topics Covered:**
- AutoML UI walkthrough
- Selecting target variable (defect prediction)
- Choosing features from sensor data
- Model training and evaluation
- Feature importance analysis
- Model registration

**Hands-On:**
- Train defect prediction model on inspection_silver
- Compare multiple algorithms
- Review feature importance
- Register best model to Unity Catalog

---

### 5. Notebooks, Data Exploration, and Assistant (2:00-3:00)

**Learning Objectives:**
- Write Python and SQL in notebooks
- Use AI Assistant for code generation
- Perform exploratory data analysis
- Create visualizations

**Notebook:** `05_notebooks_data_exploration.py`

**Topics Covered:**
- Notebook interface and cells
- Python and SQL magic commands
- AI Assistant for code completion
- Pandas and PySpark for data analysis
- Built-in visualizations
- DataFrame operations

**Hands-On:**
- Load sensor data with PySpark
- Calculate statistics (mean, std, percentiles)
- Use AI Assistant to generate analysis code
- Create correlation matrices
- Identify outliers and anomalies

---

### 6. Data Transformation (3:00-4:00)

**Learning Objectives:**
- Build ETL pipelines
- Transform raw data to curated datasets
- Apply data quality rules
- Schedule pipeline execution

**Notebook:** `06_data_transformation.py`

**Topics Covered:**
- Medallion architecture (Bronze → Silver → Gold)
- Data quality checks and cleansing
- Feature engineering
- Incremental processing
- Pipeline patterns
- Delta Lake operations

**Hands-On:**
- Build Bronze → Silver transformation
- Apply data quality rules (remove nulls, fix negatives)
- Calculate derived features
- Create Gold aggregation table
- Test incremental updates

---

## Day 1 Outcomes

By the end of Day 1, you will have:

✅ Navigated Databricks workspace confidently  
✅ Built queries visually with Lakeflow Designer  
✅ Created an interactive dashboard  
✅ Chatted with data using Genie  
✅ Trained an ML model with AutoML  
✅ Written Python/SQL code with AI assistance  
✅ Built a data transformation pipeline  

## Datasets Used

- `dim_factories`, `dim_models`, `dim_devices` - Reference data
- `sensor_bronze` - Raw IoT sensor readings
- `inspection_bronze` - Inspection records
- `inspection_silver` - Cleaned with features
- `inspection_gold` - Business aggregations

## Key Takeaways

1. **UI-First, Then Code**: Databricks supports both visual and code-based workflows
2. **AI Everywhere**: AI Assistant helps at every step
3. **Unity Catalog**: Centralized governance for all data assets
4. **Delta Lake**: Powers all tables with ACID guarantees
5. **Medallion Pattern**: Organize data transformations in layers

## Homework (Optional)

1. Create additional dashboard visualizations
2. Ask Genie 10 different questions about the data
3. Train AutoML model predicting temperature anomalies
4. Explore sensor data for additional patterns
5. Build transformation for a new business metric

## Next Steps

Proceed to [Day 2](../Day%202/) for advanced analytics, semantic modeling, and automation!

## Additional Resources

- [Databricks Workspace Guide](https://docs.databricks.com/workspace/index.html)
- [Lakeview Dashboards](https://docs.databricks.com/dashboards/lakeview.html)
- [AutoML Documentation](https://docs.databricks.com/machine-learning/automl/index.html)
- [Notebooks Guide](https://docs.databricks.com/notebooks/index.html)
- [Delta Lake Guide](https://docs.databricks.com/delta/index.html)
