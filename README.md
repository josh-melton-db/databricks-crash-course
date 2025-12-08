<img src=https://raw.githubusercontent.com/databricks-industry-solutions/.github/main/profile/solacc_logo.png width="600px">

[![DBR](https://img.shields.io/badge/DBR-14.3ML-red?logo=databricks&style=for-the-badge)](https://docs.databricks.com/release-notes/runtime/14.3lts-ml.html)
[![CLOUD](https://img.shields.io/badge/CLOUD-ALL-blue?logo=googlecloud&style=for-the-badge)](https://databricks.com/try-databricks)

# Databricks Comprehensive Training - 3 Days

## Overview

A hands-on, three-day training program covering the full Databricks Data Intelligence Platform. Using a realistic IoT manufacturing dataset, participants will learn data engineering, analytics, dashboards, AI/ML, and platform operations.

**Dataset:** IoT sensor data from manufacturing equipment with dimensional models for factories, devices, and inspection records.

## Getting Started

1. **Run Setup First**: Import and run [setup/setup_and_run.py](setup/) to create your training environment
2. **Follow Day by Day**: Each session builds on previous ones
3. **Hands-On Learning**: Every session includes a notebook with exercises

## Training Schedule

### Day 1: Data Analytics & Exploration

| Time  | Session | Description | Notebook |
|-------|---------|-------------|----------|
| 8:30  | **Databricks Overview** | Platform navigation, data discovery with search | 1 Databricks Overview |
| 9:30  | **Lakeflow Designer** | Point-and-click query building with AI | 2 Lakeflow Designer |
| 10:30  | **Dashboards & Genie Overview** | Create dashboards and AI chat interfaces | 3 Dashboards and Genie Overview |
| 12:00 | *Lunch* | | |
| 1:00  | **Notebooks & Data Processing** | Python basics and PySpark data analysis | 4 Notebooks |
| 2:00  | **Data Transformation** | Build ETL pipelines with medallion architecture | 5 Data Transformation |
| 3:00  | **Orchestration** | Schedule and automate workflows | 6 Orchestration |

### Day 2: Advanced Analytics & Machine Learning

| Time  | Session | Description | Notebook |
|-------|---------|-------------|----------|
| 8:30  | **Semantic Modeling** | Create reusable metric definitions | 1 Semantic Modeling |
| 10:00 | **Dashboards Deep Dive** | Advanced dashboard parameters and filters | 2 Dashboards Deep Dive |
| 11:00 | **Genie Deep Dive** | Configure AI chat with custom context | 3 Genie Deep Dive |
| 12:00 | *Lunch* | | |
| 1:00  | **AutoML** | No-code machine learning | 4 AutoML |
| 2:00  | **MLflow and MLOps** | Model tracking and lifecycle management | 5 MLflow and MLops |
| 3:00  | **ML and AI Inference** | Batch, streaming, and real-time predictions | 6 ML and AI Inference |

### Day 3: Production & Operations

| Time  | Session | Description | Notebook |
|-------|---------|-------------|----------|
| 8:30  | **CI/CD and DevOps** | Version control and deployment basics | 1 CI_CD and DevOps |
| 10:00 | **Performance Tuning** | SQL and table optimization with liquid clustering | 2 Performance Tuning |
| 11:00 | **Monitor and Govern** | System tables, costs, and governance | 3 Monitor and Govern |

## Project Structure

```
iot_time_series_analysis/
├── README.md                          # This file
├── setup/                             # Run this first!
│   ├── setup_and_run.py               # Creates all training resources
│   ├── util/
│   │   ├── data_generator.py          # IoT data generation
│   │   ├── onboarding_setup.py        # Setup helpers
│   │   └── resource_creation.py       # Resource creation utilities
│   └── scripts/
│       └── test.py                    # Validation scripts
├── Day 1/                             # Data Analytics & Exploration
│   ├── 1 Databricks Overview.ipynb
│   ├── 2 Lakeflow Designer.ipynb
│   ├── 3 Dashboards and Genie Overview.ipynb
│   ├── 4 Notebooks.ipynb
│   ├── 5 Data Transformation.ipynb
│   └── 6 Orchestration.ipynb
├── Day 2/                             # Advanced Analytics & Machine Learning
│   ├── 1 Semantic Modeling.ipynb
│   ├── 2 Dashboards Deep Dive.ipynb
│   ├── 3 Genie Deep Dive.ipynb
│   ├── 4 AutoML.ipynb
│   ├── 5 MLflow and MLops.ipynb
│   └── 6 ML and AI Inference.ipynb
├── Day 3/                             # Production & Operations
│   ├── 1 CI_CD and DevOps.ipynb
│   ├── 2 Performance Tuning.ipynb
│   └── 3 Monitor and Govern.ipynb
├── DATA_MODEL.md                      # Schema documentation
└── SCHEMA_CHANGES.md                  # PK/FK relationships
```

## Setup - Run This First! 🚀

Before starting the training, run the setup to create your environment:

1. Import `setup/setup_and_run.py` into Databricks workspace
2. Attach to ML Runtime 14.3+ cluster with Unity Catalog enabled
3. Configure catalog/schema names (or use defaults)
4. Click "Run All" (takes 3-5 minutes)

### Resources Created

**Dimension Tables (Star Schema)**
- `dim_factories` - 5 manufacturing facilities
- `dim_models` - 14 IoT device models
- `dim_devices` - Device master data with relationships

**Fact Tables**
- `sensor_bronze` - ~400K IoT sensor readings
- `inspection_bronze` - ~1.6K inspection records

**Processed Tables**
- `anomaly_detected` - Detected anomalies (Silver)
- `inspection_silver` - Enriched with time series features (Silver)
- `inspection_gold` - Business aggregations (Gold)

**Unity Catalog Volumes**
- `sensor_data` - Raw sensor CSV files
- `inspection_data` - Raw inspection CSV files
- `checkpoints` - Pipeline checkpoints

## Dataset: IoT Manufacturing

The training uses realistic IoT sensor data from manufacturing equipment (jet engine turbines):

**Sensors Measure:**
- Temperature & Air Pressure
- Rotation Speed & Airflow Rate
- Density & Delay metrics

**Dimensions:**
- 5 Factories across different regions
- 14 Device models across product families
- 60 Active devices

**Use Cases:**
- Defect prediction and anomaly detection
- Factory performance analysis
- Device health monitoring
- Predictive maintenance

## Learning Path

### Progressive Skill Building

**Day 1** focuses on core analytics:
- Discover data with search and Catalog Explorer
- Build queries with UI tools (Lakeflow)
- Create dashboards and AI chat interfaces
- Learn Python basics and process data with notebooks
- Build and orchestrate ETL pipelines

**Day 2** advances to ML and analytics:
- Semantic layers for metric reusability
- Advanced dashboard features with parameters
- Configure AI-powered chat with custom context
- Train and deploy machine learning models
- Full ML lifecycle with MLflow and inference

**Day 3** covers production operations:
- Version control and CI/CD basics
- Performance optimization with liquid clustering
- System monitoring with system tables
- Cost analysis and governance policies

## Prerequisites

- Databricks workspace with Unity Catalog enabled
- Permissions to create catalogs, schemas, tables, and volumes
- Basic SQL and Python knowledge (helpful but not required)
- No prior Databricks experience needed!

## Sample Queries

After setup completes, try these queries:

```sql
-- View manufacturing facilities
SELECT * FROM <catalog>.<schema>.dim_factories;

-- Sensor readings with device details
SELECT 
  s.device_id,
  m.model_name,
  f.factory_name,
  s.timestamp,
  s.temperature,
  s.rotation_speed
FROM <catalog>.<schema>.sensor_bronze s
JOIN <catalog>.<schema>.dim_devices d ON s.device_id = d.device_id
JOIN <catalog>.<schema>.dim_models m ON d.model_id = m.model_id
JOIN <catalog>.<schema>.dim_factories f ON d.factory_id = f.factory_id
ORDER BY s.timestamp DESC
LIMIT 100;

-- Defect rate by factory
SELECT 
  f.factory_name,
  f.region,
  SUM(CASE WHEN ig.defect = 1 THEN ig.count ELSE 0 END) as defects,
  SUM(ig.count) as total_inspections,
  ROUND(100.0 * SUM(CASE WHEN ig.defect = 1 THEN ig.count ELSE 0 END) / SUM(ig.count), 2) as defect_rate_pct
FROM <catalog>.<schema>.inspection_gold ig
JOIN <catalog>.<schema>.dim_factories f ON ig.factory_id = f.factory_id
GROUP BY f.factory_name, f.region
ORDER BY defect_rate_pct DESC;
```

## Key Technologies Covered

- **Unity Catalog**: Data governance and access control
- **Delta Lake**: ACID transactions and time travel
- **Tempo**: Time series analysis at scale
- **MLflow**: ML experiment tracking and model registry
- **Lakeflow**: Visual ETL and workflow design
- **Genie**: AI-powered data chat
- **AutoML**: Automated machine learning
- **Lakeview**: Dashboard and BI
- **Workflows**: Job orchestration
- **Agent Bricks**: GenAI application framework

## Daily Objectives

### Day 1 Objectives
- Navigate Databricks workspace and discover data with search
- Build queries visually with Lakeflow Designer
- Create dashboards and chat with data using Genie
- Learn Python basics and process data with notebooks
- Build ETL pipelines for data transformation
- Orchestrate and schedule automated workflows

### Day 2 Objectives
- Design semantic models with metric definitions
- Build advanced dashboards with parameters and filters
- Configure Genie with custom context and SQL examples
- Train ML models with no-code AutoML
- Track experiments and manage models with MLflow
- Deploy models for batch, streaming, and real-time inference

### Day 3 Objectives
- Implement version control and CI/CD basics
- Optimize queries with liquid clustering and performance tuning
- Monitor system health using system tables
- Analyze and control costs
- Implement governance policies with Unity Catalog
- Troubleshoot common issues

## Support & Resources

- **Instructor Support**: Available during sessions
- **Documentation**: [docs.databricks.com](https://docs.databricks.com)
- **Community**: [community.databricks.com](https://community.databricks.com)
- **Academy**: [academy.databricks.com](https://academy.databricks.com)

## Troubleshooting

**Issue: "Catalog not found"**
- Verify Unity Catalog is enabled
- Check catalog permissions
- Try using `CATALOG = 'main'`

**Issue: "Tempo import errors"**
- Ensure using ML Runtime 14.3+
- Verify dbl-tempo is installed

**Issue: "Setup takes too long"**
- Reduce NUM_ROWS and NUM_DEVICES
- Use larger cluster

## Authors

josh.melton@databricks.com

## License

&copy; 2025 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source].

---

**Ready to begin?** Start with [setup/setup_and_run.py](setup/) to create your training environment! 🚀
