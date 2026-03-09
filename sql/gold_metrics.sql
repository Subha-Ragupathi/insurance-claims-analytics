SELECT
    policy_type,
    claim_status,
    total_claims,
    total_claim_amount,
    avg_claim_amount
FROM delta.`output/gold/claims_summary`
ORDER BY total_claim_amount DESC;
