# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer — Raw Data Ingestion
# MAGIC Reads CSV source files, validates column structure, and stores as Delta tables.
# MAGIC Supports both full-refresh and incremental (merge/upsert) load modes.

# COMMAND ----------

# MAGIC %run ./00_pipeline_config

# COMMAND ----------

import logging
from delta.tables import DeltaTable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [BRONZE] %(levelname)s: %(message)s")
logger = logging.getLogger("bronze_ingestion")

# COMMAND ----------

def validate_schema(df, table_name):
    """Validate that the DataFrame contains all expected columns."""
    expected_columns = set(SCHEMAS[table_name].keys())
    actual_columns = set(df.columns)
    missing = expected_columns - actual_columns
    if missing:
        raise ValueError(f"Schema validation failed for '{table_name}': missing columns {missing}")
    extra = actual_columns - expected_columns
    if extra:
        logger.warning(f"Unexpected columns in '{table_name}': {extra}")


def write_full(df, output_path, partition_by):
    """Full overwrite — drop and rewrite the entire table."""
    writer = df.write.format("delta").mode("overwrite")
    if partition_by:
        writer = writer.partitionBy(partition_by)
    writer.save(output_path)


def write_incremental(df, output_path, merge_keys, partition_by):
    """Incremental upsert — merge new/updated records into existing Delta table."""
    try:
        delta_table = DeltaTable.forPath(spark, output_path)
        merge_condition = " AND ".join([f"target.{k} = source.{k}" for k in merge_keys])

        delta_table.alias("target") \
            .merge(df.alias("source"), merge_condition) \
            .whenMatchedUpdateAll() \
            .whenNotMatchedInsertAll() \
            .execute()

        logger.info(f"Incremental merge completed using keys: {merge_keys}")

    except Exception:
        # Table doesn't exist yet — fall back to full write for first load
        logger.info("Delta table not found — performing initial full load")
        write_full(df, output_path, partition_by)

# COMMAND ----------

def ingest_to_bronze():
    """Ingest all raw CSV files into the bronze Delta layer."""
    success_count = 0
    for table_name, meta in DATASETS.items():
        try:
            input_path = RAW_PATH + meta["file"]
            output_path = BRONZE_PATH + table_name
            logger.info(f"Reading {meta['file']} from {RAW_PATH}")

            df = spark.read.option("header", True).option("inferSchema", True).csv(input_path)
            validate_schema(df, table_name)

            row_count = df.count()

            if LOAD_MODE == "incremental":
                write_incremental(df, output_path, meta["merge_keys"], meta.get("partition_by"))
            else:
                write_full(df, output_path, meta.get("partition_by"))

            logger.info(
                f"Bronze table '{table_name}' created — {row_count} rows, "
                f"mode={LOAD_MODE}, partition_by={meta.get('partition_by')}"
            )
            success_count += 1

        except Exception as e:
            logger.error(f"Failed to ingest '{table_name}': {e}")
            raise

    logger.info(f"Bronze ingestion complete — {success_count}/{len(DATASETS)} tables ingested ({LOAD_MODE} mode)")

# COMMAND ----------

ingest_to_bronze()
