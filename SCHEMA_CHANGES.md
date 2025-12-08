# Schema Changes - Primary Key / Foreign Key Implementation

## Summary

This document describes the changes made to implement a proper star schema with primary key and foreign key relationships using Databricks constraint syntax.

## Files Modified

### 1. `/util/data_generator.py`
**Added three new functions:**

- `generate_dimension_tables(spark)` - Creates `dim_factories` and `dim_models` reference data
- `generate_device_dimension(spark, num_devices)` - Creates `dim_devices` with FK relationships
- These functions mirror the data generation logic from the original IOT data to ensure consistency

**Key Features:**
- Factory data: 5 factories (A06, D18, J15, C04, T10) with location details
- Model data: 14 models across 7 product families with categories and release years
- Device data: Uses same hashing logic as IOT generation to assign factories/models

### 2. `/setup_and_run.py`
**Major changes:**

#### Added Dimension Table Creation (NEW)
- **dim_factories** - 5 rows with PRIMARY KEY on `factory_id`
- **dim_models** - 14 rows with PRIMARY KEY on `model_id`  
- **dim_devices** - N rows (based on NUM_DEVICES) with:
  - PRIMARY KEY on `device_id`
  - FOREIGN KEY to `dim_factories(factory_id)`
  - FOREIGN KEY to `dim_models(model_id)`

#### Updated Bronze Table Creation
- **sensor_bronze** - Added 3 FOREIGN KEYs:
  - FK to `dim_devices(device_id)`
  - FK to `dim_factories(factory_id)`
  - FK to `dim_models(model_id)`

- **inspection_bronze** - Added 1 FOREIGN KEY:
  - FK to `dim_devices(device_id)`

#### Table Creation Order
Tables are now created in dependency order:
1. dim_factories (no dependencies)
2. dim_models (no dependencies)
3. dim_devices (depends on factories, models)
4. sensor_bronze (depends on devices, factories, models)
5. inspection_bronze (depends on devices)
6. Silver/Gold layers (unchanged)

#### Enhanced Documentation
- Updated markdown cells with new data model information
- Added sample queries demonstrating dimensional joins
- Updated summary statistics to show all tables and relationships

## Databricks Constraint Syntax Used

All constraints follow the official Databricks syntax:

```sql
-- Primary Key
CONSTRAINT constraint_name PRIMARY KEY (column) NOT ENFORCED

-- Foreign Key
CONSTRAINT constraint_name 
  FOREIGN KEY (column) 
  REFERENCES parent_table(parent_column) 
  NOT ENFORCED
```

**Important:** 
- `NOT ENFORCED` is required - Databricks does not enforce referential integrity at runtime
- Constraints are informational and used for query optimization
- Only works with Unity Catalog (not hive_metastore)

## Star Schema Design

```
        Dimensions (Reference Data)
        ┌────────────────────┐
        │  dim_factories (5) │
        └──────────┬─────────┘
                   │
        ┌──────────┴─────────┐
        │                    │
┌───────▼─────────┐   ┌─────▼──────────┐
│ dim_models (14) │   │ dim_devices (N)│
└─────────────────┘   └────────┬───────┘
                               │
                ┌──────────────┴───────────────┐
                │                              │
        ┌───────▼────────────┐      ┌─────────▼──────────┐
        │ sensor_bronze      │      │ inspection_bronze  │
        │ (400K+ rows)       │      │ (~1.6K rows)       │
        └────────────────────┘      └────────────────────┘
                    Facts (Transactional Data)
```

## Benefits

1. **Data Integrity** - Explicit relationships between tables
2. **Query Optimization** - Databricks can leverage constraints for query planning
3. **Self-Documenting** - Schema clearly shows data relationships
4. **Analytics-Ready** - Star schema is ideal for BI and reporting
5. **Maintainability** - Clear separation of dimensions and facts

## Testing Queries

### Verify Primary Keys
```sql
-- Check factories
SELECT * FROM dim_factories ORDER BY factory_id;

-- Check models  
SELECT * FROM dim_models ORDER BY model_family, model_name;

-- Check devices
SELECT * FROM dim_devices LIMIT 10;
```

### Verify Foreign Key Relationships
```sql
-- Devices should only reference existing factories
SELECT DISTINCT d.factory_id 
FROM dim_devices d
LEFT JOIN dim_factories f ON d.factory_id = f.factory_id
WHERE f.factory_id IS NULL;
-- Should return 0 rows

-- Sensor data should only reference existing devices
SELECT DISTINCT s.device_id
FROM sensor_bronze s
LEFT JOIN dim_devices d ON s.device_id = d.device_id
WHERE d.device_id IS NULL;
-- Should return 0 rows
```

### Sample Analytical Query
```sql
-- Defect rate by factory with full details
SELECT 
  f.factory_name,
  f.region,
  f.city,
  COUNT(DISTINCT d.device_id) as device_count,
  SUM(CASE WHEN ib.defect = 1 THEN 1 ELSE 0 END) as total_defects,
  COUNT(*) as total_inspections,
  ROUND(100.0 * SUM(CASE WHEN ib.defect = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as defect_rate_pct
FROM inspection_bronze ib
JOIN dim_devices d ON ib.device_id = d.device_id
JOIN dim_factories f ON d.factory_id = f.factory_id
GROUP BY f.factory_name, f.region, f.city
ORDER BY defect_rate_pct DESC;
```

## Migration Notes

- **No breaking changes** to existing data generation logic
- IoT sensor data generation remains unchanged
- All dimension data is automatically created from the same reference lists
- Device-to-factory and device-to-model mappings use identical hashing logic

## Next Steps

1. Run the updated `setup_and_run.py` notebook
2. Verify all tables are created with proper constraints
3. Use `DESCRIBE EXTENDED table_name` to view constraint metadata
4. Build dashboards and reports leveraging the dimensional model
5. Consider adding more dimension tables (e.g., dim_date, dim_sensor_types)

## References

- [Databricks Constraint Syntax Documentation](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint)
- See `DATA_MODEL.md` for detailed schema documentation







