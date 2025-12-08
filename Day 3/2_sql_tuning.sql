-- Databricks notebook source
-- MAGIC %md
-- MAGIC ## Predicate Pushdown

-- COMMAND ----------

-- DBTITLE 1,Substring Filter
SELECT
  *
FROM system.access.audit
WHERE substring(event_time, 1, 10) = '2025-03-20'

-- COMMAND ----------

-- DBTITLE 1,Timestamp Filter
SELECT
  *
FROM system.access.audit
WHERE DATE(event_time) = '2025-03-20'

-- COMMAND ----------

-- DBTITLE 1,Date Filter
SELECT
  *
FROM system.access.audit
WHERE event_date = DATE('2025-03-20')

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Specifying Join Types
-- MAGIC For more detail, try [this blog post](https://oindrila-chakraborty88.medium.com/different-types-of-join-strategies-in-apache-spark-5c0066999d0d)

-- COMMAND ----------

-- DBTITLE 1,Shuffle Hash Join
-- Before: Spark may choose a shuffle join between two tables of very different sizes. We'll make sure it does for the sake of the demo
-- system.query.history (big) ⋈ system.compute.warehouses (small)
SELECT
  /*+ SHUFFLE_HASH(w) */
  *
FROM system.query.history AS q
JOIN system.compute.warehouses AS w
  ON q.compute.warehouse_id = w.warehouse_id

-- COMMAND ----------

-- DBTITLE 1,Broadcast Join
-- After: Force a Broadcast Hash Join on the small table (system.clusters),
-- so only system.clusters is shipped to executors. The big table never moves.
SELECT
  /*+ BROADCAST(w) */
  *
FROM system.query.history AS q
JOIN system.compute.warehouses AS w
  ON q.compute.warehouse_id = w.warehouse_id

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Warehouse Sizing

-- COMMAND ----------

-- DBTITLE 1,XXS Warehouse
-- BEFORE: Self-join on system.access.audit to pair every event by the same user
-- within a 5-minute window over the last 7 days. Run on a SMALL warehouse (e.g., 2X-Small).
SELECT
  a.request_id             AS req_a,
  b.request_id             AS req_b,
  a.user_identity.email    AS user_email,
  ABS(DATEDIFF(SECOND, a.event_time, b.event_time)) AS time_diff_secs
FROM system.access.audit AS a
JOIN system.access.audit AS b
  ON a.user_identity.email = b.user_identity.email
  AND a.request_id < b.request_id
  AND ABS(DATEDIFF(SECOND, a.event_time, b.event_time)) <= 300

-- COMMAND ----------

-- DBTITLE 1,Large Warehouse
-- AFTER: Run same query on a Large warehouse, ~7x speedup
SELECT
  a.request_id             AS req_a,
  b.request_id             AS req_b,
  a.user_identity.email    AS user_email,
  ABS(DATEDIFF(SECOND, a.event_time, b.event_time)) AS time_diff_secs
FROM system.access.audit AS a
JOIN system.access.audit AS b
  ON a.user_identity.email = b.user_identity.email
  AND a.request_id < b.request_id
  AND ABS(DATEDIFF(SECOND, a.event_time, b.event_time)) <= 300

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Materializing Results

-- COMMAND ----------

-- DBTITLE 1,Standard Query
-- Report: daily average query duration for the past 90 days
SELECT 
  end_time,
  AVG(execution_duration_ms) AS avg_duration_ms
FROM system.query.history
WHERE end_time BETWEEN DATEADD(DAY, -90, CURRENT_DATE()) AND CURRENT_DATE()
GROUP BY end_time
ORDER BY end_time;

-- COMMAND ----------

-- DBTITLE 1,Create MV
-- Step 1: Create a table for the 90‐day aggregation
CREATE OR REPLACE TABLE mv_daily_avg_duration_90d
AS
SELECT
  end_time,
  AVG(execution_duration_ms) AS avg_duration_ms
FROM system.query.history
WHERE end_time BETWEEN DATEADD(DAY, -90, CURRENT_DATE()) AND CURRENT_DATE()
GROUP BY end_time;

-- COMMAND ----------

-- DBTITLE 1,MV Query
-- Step 2: Query the MV for fast results
SELECT *
FROM mv_daily_avg_duration_90d
ORDER BY end_time;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Incremental Processing

-- COMMAND ----------

CREATE OR REPLACE MATERIALIZED VIEW iot_mv AS 
SELECT * 
FROM main.onboarding.josh_melton_sensor_bronze 
WHERE model_id='W07-5100-6362'

-- COMMAND ----------

REFRESH MATERIALIZED VIEW iot_mv;

-- COMMAND ----------

INSERT INTO main.onboarding.josh_melton_sensor_bronze 
(SELECT * 
FROM main.onboarding.josh_melton_sensor_bronze 
LIMIT 1)

-- COMMAND ----------

REFRESH MATERIALIZED VIEW iot_mv;

-- COMMAND ----------

SELECT timestamp, message
FROM event_log(TABLE(iot_mv))
WHERE event_type = 'planning_information'
ORDER BY timestamp DESC;
