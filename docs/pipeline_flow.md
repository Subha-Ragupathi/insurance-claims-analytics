# Pipeline Flow

## End-to-End Execution Steps
1. Azure Data Factory ingests raw source files into the raw layer.
2. Bronze ingestion notebook loads raw CSV files into Delta bronze tables.
3. Silver transformation notebook cleans, standardizes, and validates data.
4. Gold aggregation notebook creates analytics-ready summary tables.
5. SQL queries are used to analyze gold tables.
6. Power BI dashboard consumes curated gold outputs for reporting.
