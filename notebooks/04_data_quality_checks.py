from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

spark = SparkSession.builder \
    .appName("Data Quality Checks") \
    .getOrCreate()

silver_path = "output/silver/"
claims = spark.read.format("delta").load(silver_path + "claims")

null_check = claims.select([
    count(when(col(c).isNull(), c)).alias(c) for c in claims.columns
])

duplicate_check = claims.groupBy("claim_id").count().filter(col("count") > 1)

print("Null counts:")
null_check.show()

print("Duplicate claim IDs:")
duplicate_check.show()
