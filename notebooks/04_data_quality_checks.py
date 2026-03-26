# Databricks notebook source
# MAGIC %md
# MAGIC # Data Quality Checks
# MAGIC Validates all silver-layer tables for null values, duplicate primary keys, and row-count thresholds.

# COMMAND ----------

# MAGIC %run ./00_pipeline_config

# COMMAND ----------

import logging
from pyspark.sql.functions import col, count, when

logging.basicConfig(level=logging.INFO, format="%(asctime)s [DQ] %(levelname)s: %(message)s")
logger = logging.getLogger("data_quality")

# COMMAND ----------

def check_nulls(df, table_name):
    """Report null counts per column. Returns True if no nulls found."""
    null_counts = df.select([
        count(when(col(c).isNull(), c)).alias(c) for c in df.columns
    ]).collect()[0]

    has_nulls = False
    for column in df.columns:
        null_count = null_counts[column]
        if null_count > 0:
            logger.warning(f"[{table_name}] Column '{column}' has {null_count} null(s)")
            has_nulls = True

    if not has_nulls:
        logger.info(f"[{table_name}] No null values detected")
    return not has_nulls


def check_duplicates(df, table_name, primary_key):
    """Check for duplicate primary keys. Returns True if no duplicates found."""
    duplicates = df.groupBy(primary_key).count().filter(col("count") > 1)
    dup_count = duplicates.count()

    if dup_count > 0:
        logger.warning(f"[{table_name}] Found {dup_count} duplicate '{primary_key}' values")
        duplicates.show(truncate=False)
        return False

    logger.info(f"[{table_name}] No duplicate '{primary_key}' values")
    return True


def check_row_count(df, table_name, min_rows=1):
    """Verify table has at least min_rows rows. Returns True if threshold met."""
    row_count = df.count()
    if row_count < min_rows:
        logger.warning(f"[{table_name}] Row count ({row_count}) is below minimum threshold ({min_rows})")
        return False

    logger.info(f"[{table_name}] Row count: {row_count}")
    return True

# COMMAND ----------

def run_quality_checks():
    """Execute all data quality checks across all silver tables."""
    all_passed = True
    total_checks = 0
    passed_checks = 0

    for table_name, meta in DATASETS.items():
        try:
            logger.info(f"--- Running quality checks on '{table_name}' ---")
            df = spark.read.format("delta").load(SILVER_PATH + table_name)

            checks = [
                check_row_count(df, table_name),
                check_nulls(df, table_name),
                check_duplicates(df, table_name, meta["primary_key"]),
            ]

            total_checks += len(checks)
            passed_checks += sum(checks)
            if not all(checks):
                all_passed = False

        except Exception as e:
            logger.error(f"Quality check failed for '{table_name}': {e}")
            all_passed = False
            raise

    logger.info(f"Data quality summary: {passed_checks}/{total_checks} checks passed across {len(DATASETS)} tables")

    if all_passed:
        logger.info("All data quality checks PASSED")
    else:
        logger.warning("Some data quality checks FAILED — review warnings above")

    return all_passed

# COMMAND ----------

run_quality_checks()
