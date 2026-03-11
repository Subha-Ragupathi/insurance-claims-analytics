from pyspark.sql.functions import col, to_date, when, upper, trim
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Insurance Silver Ingestion") \
    .getOrCreate()

bronze_path = "/Volumes/workspace/default/bronze/"
silver_path = "/Volumes/workspace/default/silver/"

customers_df = spark.read.format("delta").load(bronze_path + "customers")
policies_df = spark.read.format("delta").load(bronze_path + "policies")
claims_df = spark.read.format("delta").load(bronze_path + "claims")
payments_df = spark.read.format("delta").load(bronze_path + "payments")

customers_clean = customers_df.dropDuplicates(["customer_id"]) \
    .withColumn("customer_name", trim(col("customer_name"))) \
    .withColumn("city", upper(trim(col("city")))) \
    .withColumn("state", upper(trim(col("state")))) \
    .withColumn("join_date", to_date(col("join_date")))

policies_clean = policies_df.dropDuplicates(["policy_id"]) \
    .withColumn("policy_type", upper(trim(col("policy_type")))) \
    .withColumn("status", upper(trim(col("status")))) \
    .withColumn("start_date", to_date(col("start_date"))) \
    .withColumn("end_date", to_date(col("end_date")))

claims_clean = claims_df.dropDuplicates(["claim_id"]) \
    .withColumn("claim_type", upper(trim(col("claim_type")))) \
    .withColumn("claim_status", upper(trim(col("claim_status")))) \
    .withColumn("incident_city", upper(trim(col("incident_city")))) \
    .withColumn("claim_date", to_date(col("claim_date"))) \
    .withColumn("fraud_flag", when(col("fraud_flag").isNull(), 0).otherwise(col("fraud_flag")))

payments_clean = payments_df.dropDuplicates(["payment_id"]) \
    .withColumn("payment_status", upper(trim(col("payment_status")))) \
    .withColumn("payment_date", to_date(col("payment_date")))

customers_clean.write.format("delta").mode("overwrite").save(silver_path + "customers")
policies_clean.write.format("delta").mode("overwrite").save(silver_path + "policies")
claims_clean.write.format("delta").mode("overwrite").save(silver_path + "claims")
payments_clean.write.format("delta").mode("overwrite").save(silver_path + "payments")

print("Silver tables created successfully")