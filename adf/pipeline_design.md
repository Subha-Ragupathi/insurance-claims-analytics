# Azure Data Factory Pipeline Design

## Pipeline Name
pl_insurance_claims_analytics

## Activities
1. Ingest Customers CSV
2. Ingest Policies CSV
3. Ingest Claims CSV
4. Ingest Payments CSV
5. Trigger Bronze Notebook
6. Trigger Silver Notebook
7. Trigger Gold Notebook
8. Run Data Quality Checks
9. Publish Curated Data for Reporting

## Trigger
Manual trigger or scheduled daily batch trigger

## Failure Handling
- Retry notebook execution on transient failure
- Log failed activity details
- Stop downstream execution if silver or gold transformation fails
