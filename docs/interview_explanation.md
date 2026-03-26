# Interview Explanation

## How to Explain This Project
This project is an end-to-end insurance claims analytics pipeline designed using medallion architecture principles on Databricks.

I started with raw CSV datasets — 30 customers, 35 policies, 45 claims, and 45 payments. The **bronze layer** ingests source data into Delta format after validating that the file schema matches the expected column structure. It supports both full-refresh and incremental merge modes using Delta MERGE — on subsequent runs, only new or changed records are upserted rather than rewriting the entire table.

The **silver layer** cleans and standardizes the data by removing duplicates on primary keys, converting date fields, trimming and uppercasing text values, and handling null values like defaulting missing fraud flags to zero. Silver tables are **partitioned** — for example, claims are partitioned by `claim_status` and policies by `policy_type` — to optimize query performance for downstream consumers.

The **gold layer** creates aggregated business metrics — claims summary by policy type (partitioned for fast BI queries), fraud rate analysis, and payment breakdowns by claim status. Gold aggregations are always fully recomputed from silver because aggregations are idempotent and incremental merge on summaries would introduce complexity without benefit.

The pipeline includes **data quality checks** that run against all four silver tables, validating for nulls, duplicate primary keys, and minimum row counts. There is also a **SQL analytics stage** that registers gold tables as Spark SQL views and runs business queries.

I built **centralized configuration** so that all paths, schemas, partition columns, and merge keys are defined in one place, making the pipeline portable across environments using environment variables. The project includes **31 unit tests** with pytest covering schema validation, transformation logic, aggregation correctness, merge/upsert behavior, partition cardinality, and referential integrity. A **GitHub Actions CI/CD pipeline** validates syntax and runs the full test suite on every push.

## Key Skills Demonstrated
- PySpark data processing and Delta Lake storage
- Medallion architecture design (bronze → silver → gold)
- **Delta MERGE for incremental/upsert loads** — choosing merge vs overwrite based on layer semantics
- **Partitioning strategy** — partitioning by low-cardinality columns to optimize queries without small-file problems
- Schema validation and data quality engineering
- SQL analytics on aggregated datasets
- Centralized configuration management with environment variables
- Unit testing with pytest (31 tests across 7 test classes)
- CI/CD pipeline with GitHub Actions
- Error handling and structured logging
- GitHub-based project organization and documentation

## Common Interview Questions and Answers

**Q: Why did you choose to partition by claim_status and not claim_date?**
A: claim_status has only 3 values (Approved, Pending, Rejected), making it ideal for partitioning. Partitioning by claim_date would create too many small files — one partition per day — which hurts read performance. For time-based filtering, I'd use Z-ordering on claim_date instead.

**Q: Why doesn't the gold layer use incremental merge?**
A: Gold tables are aggregations. If a single claim changes status from Pending to Approved, both the old and new group-level rows need recalculation. Fully recomputing from silver is simpler, more reliable, and fast enough for batch workloads.

**Q: How would you handle late-arriving data?**
A: The incremental merge mode handles this naturally — late records are upserted via Delta MERGE using the primary key. For the gold layer, the full recomputation picks up any changes automatically.

**Q: What would you do differently at scale (millions of rows)?**
A: I'd add Z-ordering on frequently filtered columns, enable auto-compaction to handle small files, use broadcast joins for small dimension tables, and consider liquid clustering in newer Delta versions.
