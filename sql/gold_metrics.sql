-- Gold Layer SQL Analytics
-- These queries are executed programmatically by 05_gold_sql_analytics.py
-- They can also be run directly in Databricks SQL against the registered temp views.
-- Path format:
--   Community Edition: /FileStore/insurance_claims/gold/
--   Unity Catalog:     /Volumes/workspace/default/gold/

-- 1. Claims summary by policy type and status (ordered by highest claim amount)
SELECT
    policy_type,
    claim_status,
    total_claims,
    total_claim_amount,
    avg_claim_amount
FROM claims_summary
ORDER BY total_claim_amount DESC;

-- 2. Fraud rate by policy type (ordered by highest fraud rate)
SELECT
    policy_type,
    fraud_cases,
    total_claims,
    ROUND((fraud_cases * 100.0) / total_claims, 2) AS fraud_rate_pct
FROM fraud_summary
ORDER BY fraud_rate_pct DESC;

-- 3. Payment summary by claim status (ordered by highest paid amount)
SELECT
    claim_status,
    total_paid_amount,
    payment_count
FROM payment_summary
ORDER BY total_paid_amount DESC;
