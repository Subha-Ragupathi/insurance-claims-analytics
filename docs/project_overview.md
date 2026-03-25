# Project Overview

## Project Name
Insurance Claims Analytics Platform

## Objective
Build an end-to-end Azure-style data engineering pipeline for insurance claims data using a medallion architecture (raw → bronze → silver → gold) with production-grade practices including incremental loading, partitioning, and comprehensive testing.

## Business Problem
Insurance companies need a reliable analytics pipeline to track claims, payments, fraud indicators, and policy-level trends. Raw operational data is often inconsistent, contains duplicates, and is not ready for direct reporting. Batch pipelines must support both initial full loads and ongoing incremental updates as new data arrives.

## Solution
This project ingests raw CSV files, validates schemas, transforms data using PySpark, stores curated datasets across medallion layers with Delta partitioning, supports incremental merge/upsert for ongoing loads, runs data quality checks, and prepares analytics-ready outputs for reporting.

## Key Features
- Raw data ingestion with schema validation
- Bronze, silver, and gold data layers using partitioned Delta Lake tables
- Incremental merge/upsert using Delta MERGE for ongoing batch loads
- Data cleansing: deduplication, null handling, date parsing, text standardization
- Fraud and claims summary metrics in the gold layer
- Data quality validation across all tables (nulls, duplicates, row counts, referential integrity)
- SQL analytics integrated into the pipeline
- Centralized configuration for environment-portable path, schema, and partition management
- 31 unit tests with pytest covering transformations, aggregations, merge logic, and partitioning
- CI/CD with GitHub Actions (syntax checks + full test suite)

## Technology Stack
- Python, PySpark 3.5.1
- SQL, Delta Lake (partitioned + MERGE)
- Databricks
- GitHub, GitHub Actions
- Azure Data Factory (pipeline design)
- Power BI (planned dashboard layer)
- pytest (31 tests)

## Expected Outputs
- Claims summary by policy type and status (partitioned)
- Fraud rate by policy type
- Payment summary by claim status
- Cleaned and validated silver tables for downstream reporting
