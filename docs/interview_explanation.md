# Interview Explanation

## How to Explain This Project
This project is an end-to-end insurance claims analytics pipeline designed using medallion architecture principles.

I started with raw CSV datasets for customers, policies, claims, and payments. The bronze layer ingests source data into Delta-style storage. The silver layer cleans and standardizes the data by removing duplicates, converting date fields, trimming text values, and handling nulls. The gold layer creates aggregated business metrics such as claims summary, fraud summary, and payment summary.

The project demonstrates core data engineering concepts including data ingestion, transformation, data quality validation, layered architecture, SQL-based reporting, and analytics-ready data modeling.

## Key Skills Demonstrated
- PySpark data processing
- SQL analytics
- Data cleansing and standardization
- Medallion architecture
- Batch pipeline design
- GitHub-based project organization
