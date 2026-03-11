from pyspark.sql.functions import sum, count, avg

silver_path = "/Volumes/workspace/default/silver/"
gold_path = "/Volumes/workspace/default/gold/"

customers = spark.read.format("delta").load(silver_path + "customers")
policies = spark.read.format("delta").load(silver_path + "policies")
claims = spark.read.format("delta").load(silver_path + "claims")
payments = spark.read.format("delta").load(silver_path + "payments")

claims_policy = claims.join(policies, "policy_id", "left") \
    .join(customers, "customer_id", "left")

claims_summary = claims_policy.groupBy("policy_type", "claim_status").agg(
    count("claim_id").alias("total_claims"),
    sum("claim_amount").alias("total_claim_amount"),
    avg("claim_amount").alias("avg_claim_amount")
)

fraud_summary = claims_policy.groupBy("policy_type").agg(
    sum("fraud_flag").alias("fraud_cases"),
    count("claim_id").alias("total_claims")
)

payment_summary = payments.join(claims, "claim_id", "left").groupBy("claim_status").agg(
    sum("paid_amount").alias("total_paid_amount"),
    count("payment_id").alias("payment_count")
)

claims_summary.write.format("delta").mode("overwrite").save(gold_path + "claims_summary")
fraud_summary.write.format("delta").mode("overwrite").save(gold_path + "fraud_summary")
payment_summary.write.format("delta").mode("overwrite").save(gold_path + "payment_summary")

print("Gold tables created successfully")