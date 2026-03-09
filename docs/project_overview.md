# Project Overview

## Project Name
Insurance Claims Analytics Platform

## Objective
Build an end-to-end Azure-style data engineering pipeline for insurance claims data using raw, bronze, silver, and gold layers.

## Business Problem
Insurance companies need a reliable analytics pipeline to track claims, payments, fraud indicators, and policy-level trends. Raw operational data is often inconsistent and not ready for direct reporting.

## Solution
This project ingests raw CSV files, transforms them using PySpark, stores curated datasets across medallion layers, and prepares analytics-ready outputs for reporting.

## Key Features
- Raw data ingestion using PySpark
- Bronze, silver, and gold data layers
- Data cleansing and standardization
- Fraud and claims summary metrics
- Data quality validation checks
- SQL queries for analytics consumption

## Technology Stack
- Python
- PySpark
- SQL
- Delta Lake
- GitHub
- Azure Data Factory (project design)
- Azure Databricks (project design)
- Power BI (planned dashboard layer)

## Expected Outputs
- Claims summary by policy type and status
- Fraud rate by policy type
- Payment summary by claim status
- Cleaned silver tables for downstream reporting
