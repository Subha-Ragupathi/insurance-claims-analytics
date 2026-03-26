# Azure Data Factory Pipeline Design

## Pipeline Name
pl_insurance_claims_analytics

## Activities
1. Ingest Customers CSV
2. Ingest Policies CSV
3. Ingest Claims CSV
4. Ingest Payments CSV
5. Trigger Bronze Notebook (with schema validation)
6. Trigger Silver Notebook (cleaning and standardization)
7. Trigger Gold Notebook (business aggregations)
8. Run Data Quality Checks (all tables)
9. Run Gold SQL Analytics
10. Publish Curated Data for Reporting

## Trigger
Manual trigger or scheduled daily batch trigger

## Failure Handling
- Retry notebook execution on transient failure (max 2 retries)
- Log failed activity details to pipeline monitoring
- Stop downstream execution if bronze schema validation fails
- Stop downstream execution if silver or gold transformation fails
- Alert on data quality check failures via email notification

## Configuration
- Pipeline parameters reference `config/pipeline_config.py` for paths
- Environment-specific overrides via ADF pipeline parameters mapped to `PIPELINE_BASE_VOLUME`
