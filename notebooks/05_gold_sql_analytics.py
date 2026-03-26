# Databricks notebook source
# MAGIC %md
# MAGIC # Gold SQL Analytics
# MAGIC Runs analytical queries against gold-layer Delta tables.
# MAGIC Produces key business metrics for claims, fraud, and payments.

# COMMAND ----------

# MAGIC %run ./00_pipeline_config

# COMMAND ----------

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SQL] %(levelname)s: %(message)s")
logger = logging.getLogger("gold_sql_analytics")

# COMMAND ----------

def run_gold_analytics():
    """Register gold tables as temp views and run analytical SQL queries."""
    try:
        # Register gold Delta tables as temporary SQL views
        tables = ["claims_summary", "fraud_summary", "payment_summary"]
        for table in tables:
            spark.read.format("delta").load(GOLD_PATH + table).createOrReplaceTempView(table)
            logger.info(f"Registered temp view: {table}")

        # 1. Claims by policy type and status
        logger.info("--- Claims Summary by Policy Type ---")
        claims_sql = spark.sql("""
            SELECT policy_type, claim_status, total_claims,
                   total_claim_amount, avg_claim_amount
            FROM claims_summary
            ORDER BY total_claim_amount DESC
        """)
        claims_sql.show(truncate=False)

        # 2. Fraud rate by policy type
        logger.info("--- Fraud Rate by Policy Type ---")
        fraud_sql = spark.sql("""
            SELECT policy_type, fraud_cases, total_claims,
                   ROUND((fraud_cases * 100.0) / total_claims, 2) AS fraud_rate_pct
            FROM fraud_summary
            ORDER BY fraud_rate_pct DESC
        """)
        fraud_sql.show(truncate=False)

        # 3. Payment summary by claim status
        logger.info("--- Payment Summary by Claim Status ---")
        payment_sql = spark.sql("""
            SELECT claim_status, total_paid_amount, payment_count
            FROM payment_summary
            ORDER BY total_paid_amount DESC
        """)
        payment_sql.show(truncate=False)

        logger.info("Gold SQL analytics complete")

    except Exception as e:
        logger.error(f"SQL analytics failed: {e}")
        raise

# COMMAND ----------

run_gold_analytics()
