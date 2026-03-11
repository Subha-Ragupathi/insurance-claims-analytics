from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Insurance Bronze Ingestion") \
    .getOrCreate()

base_input_path = "dbfs:/data/raw/"
base_output_path = "dbfs:/output/bronze/"

datasets = {
    "customers": "customers.csv",
    "policies": "policies.csv",
    "claims": "claims.csv",
    "payments": "payments.csv"
}

for table_name, file_name in datasets.items():
    df = spark.read.option("header", True).option("inferSchema", True).csv(base_input_path + file_name)

    df.write.format("delta").mode("overwrite").save(base_output_path + table_name)

    print(f"Bronze table created for {table_name}")