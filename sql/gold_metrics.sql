SELECT
    policy_type,
    claim_status,
    total_claims,
    total_claim_amount,
    avg_claim_amount
FROM delta.`/Volumes/workspace/default/gold/claims_summary`
ORDER BY total_claim_amount DESC;

SELECT
    policy_type,
    fraud_cases,
    total_claims,
    ROUND((fraud_cases * 100.0) / total_claims, 2) AS fraud_rate
FROM delta.`/Volumes/workspace/default/gold/fraud_summary`
ORDER BY fraud_rate DESC;

SELECT
    claim_status,
    total_paid_amount,
    payment_count
FROM delta.`/Volumes/workspace/default/gold/payment_summary`
ORDER BY total_paid_amount DESC;
