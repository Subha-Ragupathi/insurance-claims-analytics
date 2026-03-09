SELECT
    policy_type,
    fraud_cases,
    total_claims,
    ROUND((fraud_cases * 100.0) / total_claims, 2) AS fraud_rate
FROM delta.`output/gold/fraud_summary`
ORDER BY fraud_rate DESC;
