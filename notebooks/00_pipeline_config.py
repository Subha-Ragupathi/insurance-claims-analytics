# Databricks notebook source
# MAGIC %md
# MAGIC # Pipeline Configuration
# MAGIC Centralized configuration for the Insurance Claims Analytics pipeline.
# MAGIC Run this notebook first using `%run ./00_pipeline_config` from other notebooks.

# COMMAND ----------

import os

# Environment: "databricks_community", "databricks_uc", or "local"
ENVIRONMENT = os.getenv("PIPELINE_ENV", "databricks_community")

# Base path — defaults to Unity Catalog Volume
# Create a volume in Catalog before running: Catalog → default → default → Volumes → Create Volume
BASE_PATH = os.getenv("PIPELINE_BASE_PATH", "/Volumes/workspace/default")

# Layer paths
RAW_PATH = f"{BASE_PATH}/raw/"
BRONZE_PATH = f"{BASE_PATH}/bronze/"
SILVER_PATH = f"{BASE_PATH}/silver/"
GOLD_PATH = f"{BASE_PATH}/gold/"

# Pipeline mode: "full" (overwrite) or "incremental" (merge/upsert)
LOAD_MODE = os.getenv("PIPELINE_LOAD_MODE", "full")

# Source datasets — primary keys, partition columns, and merge keys
DATASETS = {
    "customers": {
        "file": "customers.csv",
        "primary_key": "customer_id",
        "partition_by": None,
        "merge_keys": ["customer_id"],
    },
    "policies": {
        "file": "policies.csv",
        "primary_key": "policy_id",
        "partition_by": "policy_type",
        "merge_keys": ["policy_id"],
    },
    "claims": {
        "file": "claims.csv",
        "primary_key": "claim_id",
        "partition_by": "claim_status",
        "merge_keys": ["claim_id"],
    },
    "payments": {
        "file": "payments.csv",
        "primary_key": "payment_id",
        "partition_by": "payment_status",
        "merge_keys": ["payment_id"],
    },
}

# Expected schemas for validation
SCHEMAS = {
    "customers": {
        "customer_id": "string", "customer_name": "string", "age": "int",
        "gender": "string", "city": "string", "state": "string", "join_date": "string",
    },
    "policies": {
        "policy_id": "string", "customer_id": "string", "policy_type": "string",
        "premium_amount": "double", "start_date": "string", "end_date": "string", "status": "string",
    },
    "claims": {
        "claim_id": "string", "policy_id": "string", "claim_date": "string",
        "claim_type": "string", "claim_amount": "double", "claim_status": "string",
        "incident_city": "string", "fraud_flag": "int",
    },
    "payments": {
        "payment_id": "string", "claim_id": "string", "payment_date": "string",
        "paid_amount": "double", "payment_status": "string",
    },
}

# Gold layer partitioning
GOLD_PARTITIONS = {
    "claims_summary": "policy_type",
    "fraud_summary": None,
    "payment_summary": None,
}

# COMMAND ----------

print(f"Pipeline config loaded — ENV={ENVIRONMENT}, BASE_PATH={BASE_PATH}, MODE={LOAD_MODE}")
