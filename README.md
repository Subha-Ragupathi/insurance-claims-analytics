# Insurance Claims Analytics Platform

## Overview
This project demonstrates an end-to-end Azure-style data engineering pipeline for insurance claims analytics using PySpark, SQL, and Delta Lake concepts.

## Business Problem
Insurance organizations generate claims, policy, customer, and payment data from multiple operational systems. This raw data is not immediately ready for analytics because it may contain duplicates, inconsistent formats, and limited business-level aggregations.

## Solution
This project builds a medallion-style pipeline that:
- ingests raw CSV data
- stores raw records in a bronze layer
- cleans and standardizes data in a silver layer
- builds aggregated business metrics in a gold layer
- exposes SQL queries for downstream reporting

## Tech Stack
- Python
- PySpark
- SQL
- Delta Lake
- GitHub
- Azure Data Factory (design concept)
- Azure Databricks (design concept)
- Power BI (planned reporting layer)

## Architecture
Raw CSV Files -> Bronze Layer -> Silver Layer -> Gold Layer -> SQL Queries -> Dashboard
![Architecture Diagram](docs/architecture.png)

## Repository Structure
- data/raw -> source CSV files
- notebooks -> PySpark ingestion and transformation scripts
- sql -> analytics queries
- docs -> project overview and architecture notes

## Data Files
This project uses the following raw input datasets:
- customers.csv
- policies.csv
- claims.csv
- payments.csv

## Processing Layers

### Bronze Layer
Reads raw CSV input files and stores them in Delta format.

### Silver Layer
Applies cleansing and transformation rules:
- duplicate removal
- trimming text fields
- uppercasing categorical values
- date conversions
- null handling

### Gold Layer
Builds analytics-ready summary tables for:
- claims summary
- fraud summary
- payment summary

## Data Quality Checks
The project includes validation logic to identify:
- null values
- duplicate claim IDs

## Sample Business Outputs
- total claims by policy type
- claim amount trends
- fraud rate by policy type
- payment summary by claim status

## Future Enhancements
- Add Power BI dashboard screenshots
- Add architecture diagram
- Replace sample data with larger public datasets
- Add GitHub Actions CI/CD workflow
- Deploy on Azure Databricks

## Project Status
In progress
