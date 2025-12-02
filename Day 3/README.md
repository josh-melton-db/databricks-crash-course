# Day 3: Production & Operations

## Overview

Take your Databricks skills to production! Learn ML model management, performance optimization, monitoring, cost management, and governance for enterprise-scale deployments.

## Prerequisites

✅ Complete [Day 1](../Day%201/) and [Day 2](../Day%202/) sessions  
✅ [Setup](../setup/) environment with all resources created

## Schedule

| Time | Session | Topics |
|------|---------|--------|
| 8:30 | MLflow & Production AI/ML | Model tracking, registry, deployment, serving |
| 10:00 | Performance Tuning | Query optimization, caching, Z-Ordering |
| 11:00 | Monitoring, Costs & Governance | System monitoring, cost control, access policies |

## Session Details

### 13. MLflow and Production AI/ML (8:30-10:00)

**Learning Objectives:**
- Track experiments with MLflow
- Register models in Unity Catalog
- Deploy models for batch and real-time inference
- Monitor model performance
- Implement A/B testing

**Notebook:** `13_mlflow_production.py`

**Topics Covered:**
- MLflow tracking (experiments, runs, metrics)
- Model registry in Unity Catalog
- Model versioning and aliases
- Batch inference patterns
- Model serving endpoints
- Feature engineering with Unity Catalog
- Model monitoring and drift detection
- A/B testing and champion/challenger

**Hands-On:**
- Train defect prediction model and log with MLflow
- Register model in Unity Catalog
- Create model versions (v1, v2)
- Set "Champion" alias on best model
- Deploy model serving endpoint
- Run batch inference on sensor data
- Monitor prediction distribution
- Implement A/B test between model versions

**MLflow Tracking Example:**
```python
import mlflow
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run(run_name="defect_predictor_v1"):
    # Train model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    
    # Log parameters
    mlflow.log_params({"n_estimators": 100, "max_depth": 10})
    
    # Log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
```

**Model Registry:**
```python
# Register to Unity Catalog
mlflow.set_registry_uri("databricks-uc")
model_uri = f"runs:/{run_id}/model"

mlflow.register_model(
    model_uri,
    f"{catalog}.{schema}.defect_predictor"
)

# Set alias for production
client = mlflow.MlflowClient()
client.set_registered_model_alias(
    name=f"{catalog}.{schema}.defect_predictor",
    alias="Champion",
    version=1
)
```

**Model Serving:**
- Create serving endpoint
- Choose compute size
- Enable auto-scaling
- Test with sample data
- Monitor latency and throughput

**Model Monitoring:**
- Track prediction distribution
- Monitor feature drift
- Alert on anomalies
- Schedule retraining triggers

---

### 14. Performance Tuning (10:00-11:00)

**Learning Objectives:**
- Identify performance bottlenecks
- Optimize Spark queries
- Use caching effectively
- Implement Z-Ordering and Liquid Clustering
- Right-size clusters

**Notebook:** `14_performance_tuning.py`

**Topics Covered:**
- Query profiling and Spark UI
- Common performance anti-patterns
- Partitioning strategies
- Z-Ordering for query optimization
- Liquid Clustering (adaptive partitioning)
- Caching and materialized views
- Photon acceleration
- Cluster configuration
- Auto-scaling settings

**Hands-On:**
- Profile slow query on sensor_bronze
- Identify shuffle-heavy operations
- Apply Z-Ordering on device_id and timestamp
- Create materialized view for common aggregation
- Enable Photon on cluster
- Compare before/after performance
- Right-size cluster for workload
- Implement adaptive query execution

**Z-Ordering Example:**
```sql
-- Optimize table for common query patterns
OPTIMIZE {catalog}.{schema}.sensor_bronze
ZORDER BY (device_id, date(timestamp));

-- Verify file consolidation
DESCRIBE DETAIL {catalog}.{schema}.sensor_bronze;
```

**Liquid Clustering:**
```sql
-- Create table with liquid clustering
CREATE TABLE {catalog}.{schema}.sensor_clustered (
  device_id INT,
  timestamp TIMESTAMP,
  temperature FLOAT,
  rotation_speed DOUBLE
)
USING DELTA
CLUSTER BY (device_id, date(timestamp));
```

**Materialized Views:**
```sql
-- Pre-compute expensive aggregation
CREATE MATERIALIZED VIEW {catalog}.{schema}.hourly_device_metrics AS
SELECT 
  device_id,
  date_trunc('hour', timestamp) as hour,
  AVG(temperature) as avg_temp,
  AVG(rotation_speed) as avg_rotation,
  COUNT(*) as reading_count
FROM {catalog}.{schema}.sensor_bronze
GROUP BY device_id, date_trunc('hour', timestamp);

-- Use in queries (automatically used by optimizer)
SELECT * FROM {catalog}.{schema}.hourly_device_metrics
WHERE hour >= current_date() - INTERVAL 7 DAYS;
```

**Performance Checklist:**
- [ ] Z-Order fact tables on common predicates
- [ ] Partition large tables by date
- [ ] Cache frequently accessed data
- [ ] Enable Photon for SQL workloads
- [ ] Use materialized views for complex aggregations
- [ ] Right-size clusters (don't over-provision)
- [ ] Enable auto-scaling for variable workloads
- [ ] Use Delta cache on read-heavy clusters

---

### 15. Monitoring, Costs, and Governance (11:00-12:30)

**Learning Objectives:**
- Monitor system health and usage
- Analyze and optimize costs
- Implement data governance policies
- Set up audit logging
- Manage access controls

**Notebook:** `15_monitoring_governance.py`

**Topics Covered:**
- System Tables for monitoring
- Cost analysis and optimization
- Unity Catalog governance features
- Access control and permissions
- Data lineage tracking
- Audit logging
- Compliance and security
- Disaster recovery

**System Monitoring:**

**1. Query History Analysis:**
```sql
-- Analyze query performance over last 7 days
SELECT 
  query_text,
  statement_type,
  user_name,
  execution_status,
  total_duration_ms,
  read_bytes,
  rows_produced
FROM system.query.history
WHERE statement_timestamp >= current_date() - INTERVAL 7 DAYS
  AND total_duration_ms > 10000  -- queries > 10 seconds
ORDER BY total_duration_ms DESC
LIMIT 50;
```

**2. Cluster Usage:**
```sql
-- Monitor cluster utilization
SELECT 
  cluster_id,
  cluster_name,
  owner_user_name,
  state,
  autoscale,
  cluster_memory_mb,
  cluster_cores,
  start_time,
  terminated_time,
  total_uptime_in_state_ms
FROM system.compute.clusters
WHERE start_time >= current_date() - INTERVAL 7 DAYS
ORDER BY total_uptime_in_state_ms DESC;
```

**3. Billing Analysis:**
```sql
-- Analyze costs by workspace/user
SELECT 
  workspace_id,
  sku_name,
  usage_metadata.job_id,
  usage_unit,
  SUM(usage_quantity) as total_usage,
  billing_origin_product
FROM system.billing.usage
WHERE usage_date >= current_date() - INTERVAL 30 DAYS
GROUP BY workspace_id, sku_name, usage_metadata.job_id, usage_unit, billing_origin_product
ORDER BY total_usage DESC
LIMIT 100;
```

**Cost Optimization Strategies:**
- Use spot instances for fault-tolerant workloads
- Auto-terminate idle clusters
- Right-size cluster configurations
- Use Photon for better price/performance
- Optimize queries to reduce data scanned
- Use Delta caching strategically
- Archive old data to cheaper storage
- Schedule non-urgent jobs for off-peak hours

**Governance Features:**

**1. Access Controls:**
```sql
-- Grant permissions on schema
GRANT USE SCHEMA ON SCHEMA {catalog}.{schema} TO `analysts`;
GRANT SELECT ON SCHEMA {catalog}.{schema} TO `analysts`;

-- Grant permissions on specific table
GRANT SELECT ON TABLE {catalog}.{schema}.sensor_bronze TO `data_scientists`;
GRANT MODIFY ON TABLE {catalog}.{schema}.sensor_bronze TO `data_engineers`;

-- Row-level security
CREATE FUNCTION {catalog}.{schema}.region_filter(user_region STRING)
RETURN current_user() IN (SELECT email FROM {catalog}.{schema}.user_regions WHERE region = user_region);

ALTER TABLE {catalog}.{schema}.sensor_bronze 
SET ROW FILTER region_filter ON (factory_region);
```

**2. Data Lineage:**
```sql
-- View table lineage
DESCRIBE HISTORY {catalog}.{schema}.inspection_gold;

-- Track data lineage through Unity Catalog UI
-- Shows: source tables → transformations → downstream usage
```

**3. Audit Logging:**
```sql
-- Review audit logs
SELECT 
  event_time,
  user_identity.email,
  service_name,
  action_name,
  request_params,
  response.status_code
FROM system.access.audit
WHERE action_name IN ('createTable', 'deleteTable', 'grant', 'revoke')
  AND event_date >= current_date() - INTERVAL 7 DAYS
ORDER BY event_time DESC;
```

**Governance Best Practices:**
- Implement least-privilege access
- Use groups instead of individual user grants
- Tag sensitive data (PII, PHI)
- Enable audit logging
- Regular access reviews
- Data classification policies
- Retention and archival policies
- Disaster recovery plan

**Hands-On Exercises:**

1. **Monitor Query Performance:**
   - Identify top 10 slowest queries
   - Find users running expensive queries
   - Analyze query patterns

2. **Cost Analysis:**
   - Calculate costs by team/project
   - Identify optimization opportunities
   - Set up cost alerts

3. **Implement Governance:**
   - Create data classification scheme
   - Set up role-based access
   - Enable row-level security
   - Review audit logs

4. **Disaster Recovery Test:**
   - Document recovery procedures
   - Test table restore from history
   - Validate backup strategy

---

## Day 3 Outcomes

By the end of Day 3, you will have:

✅ Deployed ML models to production with MLflow  
✅ Optimized queries with Z-Ordering and clustering  
✅ Monitored system health and costs  
✅ Implemented governance and access controls  
✅ Created audit trails and lineage  
✅ Established production-ready operations  

## Production Readiness Checklist

### Performance
- [ ] All fact tables Z-Ordered or clustered
- [ ] Materialized views for complex queries
- [ ] Photon enabled on production clusters
- [ ] Caching strategy documented
- [ ] Auto-scaling configured

### ML Operations
- [ ] Models registered in Unity Catalog
- [ ] Serving endpoints configured
- [ ] Model monitoring enabled
- [ ] Retraining pipeline automated
- [ ] A/B testing framework ready

### Monitoring & Observability
- [ ] System tables queried regularly
- [ ] Performance dashboards created
- [ ] Cost analysis automated
- [ ] Alerts configured
- [ ] SLAs defined

### Governance & Security
- [ ] Access controls reviewed
- [ ] Row-level security implemented
- [ ] Audit logging enabled
- [ ] Data classification complete
- [ ] Compliance requirements met

### Operations
- [ ] CI/CD pipelines functional
- [ ] Disaster recovery tested
- [ ] Runbooks documented
- [ ] On-call procedures defined
- [ ] Backup strategy validated

## Key Takeaways

1. **MLflow** provides end-to-end ML lifecycle management
2. **Performance optimization** requires profiling and targeted improvements
3. **System tables** provide comprehensive monitoring capabilities
4. **Cost optimization** is an ongoing process
5. **Governance** protects data and ensures compliance
6. **Production operations** require automation and monitoring

## Final Project (Optional)

Build a complete end-to-end solution:

1. **Data Pipeline**: Ingest → Transform → Aggregate
2. **ML Model**: Train → Register → Deploy → Monitor
3. **Dashboard**: Visualize KPIs and predictions
4. **Automation**: Schedule all workflows
5. **Governance**: Implement access controls
6. **Monitoring**: Track performance and costs

## Congratulations! 🎉

You've completed the comprehensive Databricks training! You now have skills across:

- Data engineering and transformation
- Analytics and visualization
- ML model development and deployment
- Platform operations and governance

## Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Unity Catalog ML](https://docs.databricks.com/machine-learning/manage-model-lifecycle/index.html)
- [Performance Tuning Guide](https://docs.databricks.com/optimizations/index.html)
- [System Tables](https://docs.databricks.com/administration-guide/system-tables/index.html)
- [Unity Catalog Governance](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Best Practices](https://docs.databricks.com/lakehouse-architecture/index.html)

## What's Next?

- Apply learnings to your organization's use cases
- Obtain Databricks certifications
- Join the Databricks Community
- Attend Databricks conferences and webinars
- Explore advanced topics (Streaming, Delta Live Tables, etc.)

**Thank you for participating!** 🚀
