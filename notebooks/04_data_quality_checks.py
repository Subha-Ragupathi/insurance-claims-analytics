from pyspark.sql.functions import col, count, when

silver_path = "/Volumes/workspace/default/silver/"
claims = spark.read.format("delta").load(silver_path + "claims")

null_check = claims.select([
    count(when(col(c).isNull(), c)).alias(c) for c in claims.columns
])

duplicate_check = claims.groupBy("claim_id").count().filter(col("count") > 1)

print("Null counts:")
null_check.show()

print("Duplicate claim IDs:")
duplicate_check.show()