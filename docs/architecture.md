# Architecture

## High-Level Flow
Raw CSV Files -> Bronze Layer -> Silver Layer -> Gold Layer -> SQL Queries -> Dashboard

## Layer Details

### Raw Layer
Stores input CSV files for customers, policies, claims, and payments.

### Bronze Layer
Ingests raw source files into Delta format without major business transformation.

### Silver Layer
Cleans and standardizes source data:
- trims text columns
- converts date fields
- removes duplicates
- normalizes categorical values

### Gold Layer
Builds analytics-ready summary tables for:
- claim metrics
- fraud metrics
- payment metrics

### Reporting Layer
SQL queries consume gold tables and can be connected to Power BI dashboards.
