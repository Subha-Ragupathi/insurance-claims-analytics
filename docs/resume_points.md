# Resume Points

- Built an end-to-end insurance claims analytics pipeline using medallion architecture with PySpark, Delta Lake, SQL, and Databricks, processing customer, policy, claims, and payment data across bronze, silver, and gold layers.
- Implemented Delta MERGE (upsert) logic for incremental data loads, reducing reprocessing overhead by merging only new and updated records on primary keys.
- Designed and applied partitioning strategy across all layers — partitioned by low-cardinality columns (policy_type, claim_status, payment_status) to optimize query performance while avoiding small-file problems.
- Built schema validation at ingestion to catch column mismatches before data enters the pipeline, preventing silent failures in downstream transformations.
- Implemented data cleansing including duplicate removal, date standardization, null handling, and text normalization across all source tables in the silver layer.
- Developed gold-layer summary tables for claim trends, fraud rate analysis, and payment tracking with partitioned outputs for downstream BI consumption.
- Built comprehensive data quality framework validating nulls, duplicate primary keys, referential integrity, and row-count thresholds across all silver tables.
- Created centralized configuration module managing paths, schemas, partition columns, merge keys, and load modes — enabling environment portability via environment variables.
- Wrote 31 unit tests with pytest covering schema validation, transformation correctness, aggregation logic, merge/upsert behavior, partition cardinality, and referential integrity.
- Set up CI/CD pipeline with GitHub Actions for automated syntax validation and full test suite execution on every commit.
- Integrated SQL analytics stage that registers gold Delta tables as Spark SQL views for downstream reporting and dashboard connectivity.
