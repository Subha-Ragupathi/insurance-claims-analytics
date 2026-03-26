# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer — Business-Ready Aggregations
# MAGIC Joins silver tables and produces claims_summary, fraud_summary, and payment_summary.
# MAGIC Gold tables are always fully recomputed from silver (no incremental merge on aggregations).
# MAGIC Partitioned by policy_type where applicable for optimized downstream queries.

# COMMAND ----------

# MAGIC %run ./00_pipeline_config

# COMMAND ----------

import logging
from pyspark.sql.functions import sum, count, avg, round as spark_round

logging.basicConfig(level=logging.INFO, format="%(asctime)s [GOLD] %(levelname)s: %(message)s")
logger = logging.getLogger("gold_aggregation")

# COMMAND ----------

def build_claims_summary(claims_policy):
    """Total claims, total amount, and average amount grouped by policy type and claim status."""
    return claims_policy.groupBy("policy_type", "claim_status").agg(
        count("claim_id").alias("total_claims"),
        spark_round(sum("claim_amount"), 2).alias("total_claim_amount"),
        spark_round(avg("claim_amount"), 2).alias("avg_claim_amount"),
    )


def build_fraud_summary(claims_policy):
    """Fraud cases and fraud rate grouped by policy type."""
    df = claims_policy.groupBy("policy_type").agg(
        sum("fraud_flag").alias("fraud_cases"),
        count("claim_id").alias("total_claims"),
    )
    return df.withColumn(
        "fraud_rate_pct",
        spark_round((df["fraud_cases"] * 100.0) / df["total_claims"], 2),
    )


def build_payment_summary(payments, claims):
    """Total paid amount and payment count grouped by claim status."""
    return payments.join(claims, "claim_id", "left").groupBy("claim_status").agg(
        spark_round(sum("paid_amount"), 2).alias("total_paid_amount"),
        count("payment_id").alias("payment_count"),
    )


def write_gold_table(df, table_name):
    """Write a gold summary table with optional partitioning."""
    output_path = GOLD_PATH + table_name
    partition_col = GOLD_PARTITIONS.get(table_name)

    writer = df.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
    if partition_col:
        writer = writer.partitionBy(partition_col)
    writer.save(output_path)

    row_count = df.count()
    logger.info(f"Gold table '{table_name}' created — {row_count} rows, partition_by={partition_col}")

# COMMAND ----------

def aggregate_to_gold():
    """Read silver tables, build gold aggregations, and write to gold Delta layer."""
    try:
        logger.info("Reading silver tables")
        customers = spark.read.format("delta").load(SILVER_PATH + "customers")
        policies = spark.read.format("delta").load(SILVER_PATH + "policies")
        claims = spark.read.format("delta").load(SILVER_PATH + "claims")
        payments = spark.read.format("delta").load(SILVER_PATH + "payments")

        # Join claims with policies and customers for enriched analytics
        claims_policy = claims.join(policies, "policy_id", "left") \
            .join(customers, "customer_id", "left")
        logger.info(f"Enriched claims dataset: {claims_policy.count()} rows")

        # Build and write each gold summary
        write_gold_table(build_claims_summary(claims_policy), "claims_summary")
        write_gold_table(build_fraud_summary(claims_policy), "fraud_summary")
        write_gold_table(build_payment_summary(payments, claims), "payment_summary")

        logger.info("Gold aggregation complete — all summary tables created")

    except Exception as e:
        logger.error(f"Gold aggregation failed: {e}")
        raise

# COMMAND ----------

aggregate_to_gold()
