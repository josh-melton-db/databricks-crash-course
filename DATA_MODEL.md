# IoT Time Series Analysis - Data Model

## Overview

This project now implements a **star schema design** with proper primary key and foreign key relationships following Databricks constraints syntax. The data model separates reference data (dimensions) from transactional data (facts) for better data integrity and query performance.

## Architecture

```
┌─────────────────┐
│  dim_factories  │ (Dimension)
│  PK: factory_id │
└────────┬────────┘
         │
         │ FK
         ↓
┌─────────────────┐      ┌──────────────┐
│   dim_models    │ (Dimension)  │ dim_devices  │ (Dimension)
│  PK: model_id   │─────→│ PK: device_id│
└─────────────────┘  FK  │ FK: factory_id│
                         │ FK: model_id  │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ↓ FK                    ↓ FK
         ┌─────────────────┐    ┌──────────────────┐
         │ sensor_bronze   │    │ inspection_bronze│
         │ (Fact Table)    │    │ (Fact Table)     │
         │ FK: device_id   │    │ FK: device_id    │
         │ FK: factory_id  │    └──────────────────┘
         │ FK: model_id    │
         └─────────────────┘
```

## Dimension Tables

### dim_factories
**Purpose:** Reference data for manufacturing facilities  
**Primary Key:** `factory_id`

| Column       | Type   | Description                    |
|--------------|--------|--------------------------------|
| factory_id   | STRING | Factory identifier (PK)        |
| factory_name | STRING | Full factory name              |
| region       | STRING | Geographic region              |
| city         | STRING | City location                  |
| state        | STRING | State/province                 |

**Data:**
- A06: Factory A06, North Region, San Francisco, CA
- D18: Factory D18, East Region, New York, NY
- J15: Factory J15, South Region, Austin, TX
- C04: Factory C04, West Region, Seattle, WA
- T10: Factory T10, Central Region, Chicago, IL

### dim_models
**Purpose:** IoT device model reference data  
**Primary Key:** `model_id`

| Column         | Type   | Description                    |
|----------------|--------|--------------------------------|
| model_id       | STRING | Model identifier (PK)          |
| model_name     | STRING | Full model name                |
| model_family   | STRING | Product family                 |
| model_category | STRING | Category/purpose               |
| release_year   | INT    | Year of release                |

**Model Families:**
- SkyJet (SkyJet134, SkyJet234, SkyJet334) - Commercial
- EcoJet (EcoJet1000, EcoJet2000, EcoJet3000) - Eco-Friendly
- SkyBolt (SkyBolt1, SkyBolt2, SkyBolt250) - Compact
- JetLift, FlyForce, TurboFan, MightyWing, AeroGlider - Various categories

### dim_devices
**Purpose:** Master data for individual IoT devices  
**Primary Key:** `device_id`  
**Foreign Keys:** 
- `factory_id` → `dim_factories(factory_id)`
- `model_id` → `dim_models(model_id)`

| Column            | Type      | Description                     |
|-------------------|-----------|---------------------------------|
| device_id         | INT       | Device identifier (PK)          |
| factory_id        | STRING    | Factory location (FK)           |
| model_id          | STRING    | Device model (FK)               |
| installation_date | DATE      | Installation date               |
| status            | STRING    | Device status (Active/Maintenance) |

## Fact Tables

### sensor_bronze
**Purpose:** Raw IoT sensor readings  
**Foreign Keys:**
- `device_id` → `dim_devices(device_id)`
- `factory_id` → `dim_factories(factory_id)`
- `model_id` → `dim_models(model_id)`

| Column         | Type      | Description                    |
|----------------|-----------|--------------------------------|
| device_id      | INT       | Device identifier (FK)         |
| trip_id        | INT       | Trip/session identifier        |
| factory_id     | STRING    | Factory identifier (FK)        |
| model_id       | STRING    | Model identifier (FK)          |
| timestamp      | TIMESTAMP | Reading timestamp              |
| airflow_rate   | DOUBLE    | Airflow rate                   |
| rotation_speed | DOUBLE    | Rotation speed                 |
| air_pressure   | FLOAT     | Air pressure                   |
| temperature    | FLOAT     | Temperature                    |
| delay          | FLOAT     | Delay metric                   |
| density        | FLOAT     | Density metric                 |

### inspection_bronze
**Purpose:** Device inspection records  
**Foreign Keys:**
- `device_id` → `dim_devices(device_id)`

| Column    | Type      | Description              |
|-----------|-----------|--------------------------|
| defect    | FLOAT     | Defect flag (0 or 1)     |
| timestamp | TIMESTAMP | Inspection timestamp     |
| device_id | INT       | Device identifier (FK)   |

## Databricks Constraint Syntax

All constraints follow the Databricks SQL syntax as documented at:
https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint

### Primary Key Example
```sql
CREATE TABLE dim_factories (
    factory_id STRING NOT NULL,
    factory_name STRING,
    ...
    CONSTRAINT factories_pk PRIMARY KEY (factory_id) NOT ENFORCED
) USING DELTA
```

### Foreign Key Example
```sql
CREATE TABLE dim_devices (
    device_id INT NOT NULL,
    factory_id STRING NOT NULL,
    model_id STRING NOT NULL,
    ...
    CONSTRAINT devices_pk PRIMARY KEY (device_id) NOT ENFORCED,
    CONSTRAINT devices_factory_fk FOREIGN KEY (factory_id) 
        REFERENCES dim_factories(factory_id) NOT ENFORCED,
    CONSTRAINT devices_model_fk FOREIGN KEY (model_id) 
        REFERENCES dim_models(model_id) NOT ENFORCED
) USING DELTA
```

**Key Points:**
- All constraints use `NOT ENFORCED` - Databricks does not enforce PK/FK constraints at runtime
- Constraints are informational and used for query optimization
- Column constraints must be declared as `NOT NULL` separately
- Unity Catalog only (not supported in hive_metastore)

## Table Creation Order

To respect foreign key dependencies, tables must be created in this order:

1. **Dimension Tables** (no dependencies):
   - `dim_factories`
   - `dim_models`

2. **Dimension with Dependencies**:
   - `dim_devices` (references factories and models)

3. **Fact Tables**:
   - `sensor_bronze` (references devices, factories, models)
   - `inspection_bronze` (references devices)

4. **Silver/Gold Layers**:
   - `anomaly_detected`
   - `inspection_silver`
   - `inspection_gold`

## Sample Queries with Joins

### Defect Analysis by Factory
```sql
SELECT 
  f.factory_name,
  f.region,
  SUM(CASE WHEN ig.defect = 1 THEN ig.count ELSE 0 END) as defects,
  SUM(ig.count) as total_inspections,
  ROUND(100.0 * SUM(CASE WHEN ig.defect = 1 THEN ig.count ELSE 0 END) / SUM(ig.count), 2) as defect_rate_pct
FROM inspection_gold ig
JOIN dim_factories f ON ig.factory_id = f.factory_id
GROUP BY f.factory_name, f.region
ORDER BY defect_rate_pct DESC;
```

### Device Performance by Model Family
```sql
SELECT 
  m.model_family,
  m.model_category,
  COUNT(DISTINCT s.device_id) as device_count,
  AVG(s.temperature) as avg_temperature,
  AVG(s.rotation_speed) as avg_rotation_speed
FROM sensor_bronze s
JOIN dim_models m ON s.model_id = m.model_id
GROUP BY m.model_family, m.model_category
ORDER BY avg_temperature DESC;
```

### Device Status and Recent Anomalies
```sql
SELECT 
  d.device_id,
  d.status as device_status,
  d.installation_date,
  f.factory_name,
  m.model_name,
  a.timestamp,
  a.temperature
FROM anomaly_detected a
JOIN dim_devices d ON a.device_id = d.device_id
JOIN dim_factories f ON d.factory_id = f.factory_id
JOIN dim_models m ON d.model_id = m.model_id
WHERE d.status = 'Active'
ORDER BY a.timestamp DESC
LIMIT 20;
```

## Benefits of This Design

1. **Data Integrity**: Foreign keys document relationships between tables
2. **Query Optimization**: Databricks can use constraint metadata to optimize queries
3. **Better Documentation**: Schema is self-documenting with clear relationships
4. **Easier Analysis**: Join paths are explicit and well-defined
5. **Star Schema**: Classic dimensional modeling for analytics workloads
6. **Reusability**: Dimension tables can be shared across multiple fact tables

## Implementation Notes

- Dimension data is generated programmatically in `util/data_generator.py`
- Functions `generate_dimension_tables()` and `generate_device_dimension()` create reference data
- Device assignments (device → factory, device → model) use the same hashing logic as the original IOT data generation to ensure consistency
- All constraints are informational (`NOT ENFORCED`) as per Databricks best practices





