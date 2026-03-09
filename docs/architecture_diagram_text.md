# Architecture Diagram Content

## Title
Insurance Claims Analytics Platform - Azure Style Data Engineering Architecture

## Flow
Source CSV Files
-> Azure Data Factory / Ingestion Layer
-> ADLS Raw Layer
-> Databricks Bronze Layer
-> Databricks Silver Layer
-> Databricks Gold Layer
-> SQL Analytics Layer
-> Power BI Dashboard

## Source Files
- customers.csv
- policies.csv
- claims.csv
- payments.csv

## Layer Explanation

### Ingestion Layer
Azure Data Factory ingests source files from raw storage.

### Raw Layer
Stores original source CSV files without modification.

### Bronze Layer
Loads raw datasets into Delta format.

### Silver Layer
Cleans and standardizes data:
- remove duplicates
- trim text fields
- standardize categorical values
- convert date columns
- handle nulls

### Gold Layer
Builds business summary tables:
- claims_summary
- fraud_summary
- payment_summary

### Reporting Layer
SQL queries and Power BI consume curated gold datasets for reporting.
