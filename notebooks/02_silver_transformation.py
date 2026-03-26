# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Data Cleansing and Standardization
# MAGIC Removes duplicates, trims text, uppercases categorical fields,
# MAGIC converts dates, and handles null values.
# MAGIC Supports both full-refresh and incremental (merge/upsert) load modes.

# COMMAND ----------

# MAGIC %run ./00_pipeline_config

# COMMAND ----------

import logging
from pyspark.sql.functions import col, to_date, when, upper, trim
from delta.tables import DeltaTable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SILVER] %(levelname)s: %(message)s")
logger = logging.getLogger("silver_transformation")

# COMMAND ----------

def clean_customers(df):
    """Deduplicate, trim names, uppercase city/state, and parse join_date."""
    return df.dropDuplicates(["customer_id"]) \
        .withColumn("customer_name", trim(col("customer_name"))) \
        .withColumn("city", upper(trim(col("city")))) \
        .withColumn("state", upper(trim(col("state")))) \
        .withColumn("join_date", to_date(col("join_date")))


def clean_policies(df):
    """Deduplicate, uppercase policy_type/status, and parse date columns."""
    return df.dropDuplicates(["policy_id"]) \
        .withColumn("policy_type", upper(trim(col("policy_type")))) \
        .withColumn("status", upper(trim(col("status")))) \
        .withColumn("start_date", to_date(col("start_date"))) \
        .withColumn("end_date", to_date(col("end_date")))


def clean_claims(df):
    """Deduplicate, uppercase text fields, parse claim_date, default fraud_flag nulls to 0."""
    return df.dropDuplicates(["claim_id"]) \
        .withColumn("claim_type", upper(trim(col("claim_type")))) \
        .withColumn("claim_status", upper(trim(col("claim_status")))) \
        .withColumn("incident_city", upper(trim(col("incident_city")))) \
        .withColumn("claim_date", to_date(col("claim_date"))) \
        .withColumn("fraud_flag", when(col("fraud_flag").isNull(), 0).otherwise(col("fraud_flag")))


def clean_payments(df):
    """Deduplicate, uppercase payment_status, and parse payment_date."""
    return df.dropDuplicates(["payment_id"]) \
        .withColumn("payment_status", upper(trim(col("payment_status")))) \
        .withColumn("payment_date", to_date(col("payment_date")))


CLEANERS = {
    "customers": clean_customers,
    "policies": clean_policies,
    "claims": clean_claims,
    "payments": clean_payments,
}

# COMMAND ----------

def write_silver_full(df, silver_path, partition_by):
    """Full overwrite of the silver table."""
    writer = df.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
    if partition_by:
        writer = writer.partitionBy(partition_by)
    writer.save(silver_path)


def write_silver_incremental(df, silver_path, merge_keys, partition_by):
    """Incremental merge — upsert cleaned records into existing silver Delta table."""
    try:
        delta_table = DeltaTable.forPath(spark, silver_path)
        merge_condition = " AND ".join([f"target.{k} = source.{k}" for k in merge_keys])

        delta_table.alias("target") \
            .merge(df.alias("source"), merge_condition) \
            .whenMatchedUpdateAll() \
            .whenNotMatchedInsertAll() \
            .execute()

        logger.info(f"Incremental merge completed using keys: {merge_keys}")

    except Exception:
        logger.info("Silver Delta table not found — performing initial full load")
        write_silver_full(df, silver_path, partition_by)

# COMMAND ----------

def transform_to_silver():
    """Read bronze tables, apply cleaning logic, and write to silver Delta layer."""
    success_count = 0
    for table_name, meta in DATASETS.items():
        try:
            bronze_path = BRONZE_PATH + table_name
            silver_path = SILVER_PATH + table_name

            logger.info(f"Reading bronze table '{table_name}' from {bronze_path}")
            df = spark.read.format("delta").load(bronze_path)
            before_count = df.count()

            clean_fn = CLEANERS[table_name]
            df_clean = clean_fn(df)
            after_count = df_clean.count()

            partition_by = meta.get("partition_by")
            if LOAD_MODE == "incremental":
                write_silver_incremental(df_clean, silver_path, meta["merge_keys"], partition_by)
            else:
                write_silver_full(df_clean, silver_path, partition_by)

            dropped = before_count - after_count
            logger.info(
                f"Silver table '{table_name}' created — {after_count} rows "
                f"({dropped} duplicates removed), mode={LOAD_MODE}, partition_by={partition_by}"
            )
            success_count += 1

        except Exception as e:
            logger.error(f"Failed to transform '{table_name}': {e}")
            raise

    logger.info(f"Silver transformation complete — {success_count}/{len(DATASETS)} tables processed ({LOAD_MODE} mode)")

# COMMAND ----------

transform_to_silver()
