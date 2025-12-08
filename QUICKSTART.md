# IoT Time Series Analysis - 5 Minute Setup

## One-Sentence Summary
Import `setup_and_run.py` into Databricks, attach to an ML cluster, and click "Run All" - that's it!

---

## Step 1: Import the Notebook

Upload `setup_and_run.py` to your Databricks workspace:

**Option A: Via UI**
1. Open your Databricks workspace
2. Right-click on your user folder → Import
3. Upload `setup_and_run.py`

**Option B: Via CLI**
```bash
databricks workspace import setup_and_run.py /Users/your.email@company.com/iot_setup
```

---

## Step 2: Run the Notebook

1. Open the imported notebook
2. Attach to a cluster with **ML Runtime 14.3+**
3. Click **Run All**
4. Wait 3-5 minutes ☕

---

## Step 3: Query Your Data

Open a SQL editor or new notebook:

```sql
-- List your tables
SHOW TABLES IN <catalog>.<schema>;

-- Query bronze layer (raw sensor data)
SELECT * FROM <catalog>.<schema>.sensor_bronze LIMIT 10;

-- Query silver layer (anomalies)
SELECT device_id, factory_id, timestamp, temperature, rotation_speed
FROM <catalog>.<schema>.anomaly_detected
ORDER BY timestamp DESC
LIMIT 20;

-- Query gold layer (business metrics)
SELECT 
  factory_id,
  SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) as defects,
  SUM(count) as total_inspections,
  ROUND(100.0 * SUM(CASE WHEN defect = 1 THEN count ELSE 0 END) / SUM(count), 2) as defect_rate_pct
FROM <catalog>.<schema>.inspection_gold
GROUP BY factory_id
ORDER BY defect_rate_pct DESC;
```

---

## What You Just Created

✅ **5 Unity Catalog Tables**
- `sensor_bronze` (400k sensor readings)
- `inspection_bronze` (1.6k inspections)
- `anomaly_detected` (threshold-based alerts)
- `inspection_silver` (time series features)
- `inspection_gold` (aggregated metrics)

✅ **3 Unity Catalog Volumes**
- `sensor_data` (CSV files)
- `inspection_data` (CSV files)
- `checkpoints` (temp storage)

✅ **Real-World Features**
- Exponential moving averages (EMA)
- As-of joins (temporal joins without data leakage)
- Hourly resampling
- Anomaly detection rules

---

## Common Configurations

### Change Catalog
Edit the notebook at the top:
```python
CATALOG = 'my_catalog'  # Change from 'default'
```

### Reduce Data Volume
Edit the notebook at the top:
```python
NUM_ROWS = 100000  # Smaller dataset (default: 400000)
NUM_DEVICES = 20   # Fewer devices (default: 60)
```

### Custom Schema Name
Edit the notebook at the top:
```python
SCHEMA = 'my_custom_schema'  # Instead of auto-generated
```

---

## Troubleshooting

**Error: "Catalog not found"**
→ Change `CATALOG = 'main'` or create the catalog first

**Error: "Module tempo not found"**
→ Use ML Runtime, not standard Runtime

**Error: "Out of memory"**
→ Reduce `NUM_ROWS` to 100000 or use larger cluster

**Tables empty after creation**
→ Check the notebook output for errors, ensure all cells completed

---

## Next Steps

📊 **Build Dashboards**: Create visualizations in Lakeview or SQL Dashboards

🤖 **Add ML Models**: Train predictive models on the silver layer features

📈 **Add More Data**: Re-run data generation cells with different parameters

🔍 **Explore Patterns**: Analyze temperature trends, defect correlations, factory performance

---

## Need More Details?

- **Quick Start**: See `RUNME.md`
- **Full Documentation**: See `README.md`
- **What Changed**: See `CHANGES.md`
- **Legacy Approach**: Check `legacy_notebooks/` directory

---

**That's it!** You have a complete IoT time series pipeline with Bronze/Silver/Gold tables in Unity Catalog. 

Questions? → josh.melton@databricks.com









