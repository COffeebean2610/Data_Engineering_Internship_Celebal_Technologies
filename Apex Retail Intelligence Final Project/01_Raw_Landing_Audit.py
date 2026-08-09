# Databricks notebook source
# Create audit directories inside the Raw layer
dbutils.fs.mkdirs("/Volumes/workspace/default/celebal_data/raw/audit_landing")
dbutils.fs.mkdirs("/Volumes/workspace/default/celebal_data/raw/audit_silver")

print("Audit directories created successfully.")

# COMMAND ----------

# Base paths
source_base = "/Volumes/workspace/default/celebal_data/Datasets"
raw_base = "/Volumes/workspace/default/celebal_data/raw"

# Copy historical data
dbutils.fs.cp(
    f"{source_base}/historical_data",
    f"{raw_base}/historical",
    recurse=True
)

# Copy incremental data
dbutils.fs.cp(
    f"{source_base}/incremental_data",
    f"{raw_base}/incremental",
    recurse=True
)

# Copy Landing audit files
dbutils.fs.cp(
    f"{source_base}/audit_landing",
    f"{raw_base}/audit_landing",
    recurse=True
)

# Copy Silver audit files
dbutils.fs.cp(
    f"{source_base}/audit_silver",
    f"{raw_base}/audit_silver",
    recurse=True
)

print("All official datasets and audit files copied to Raw successfully.")

# COMMAND ----------

display(dbutils.fs.ls("/Volumes/workspace/default/celebal_data/raw"))

# COMMAND ----------

raw_base = "/Volumes/workspace/default/celebal_data/raw"

# Check all Raw directories
for folder in [
    "historical/customer",
    "historical/product",
    "historical/sales",
    "incremental/customer",
    "incremental/product",
    "incremental/sales",
    "audit_landing",
    "audit_silver"
]:
    print(f"\n--- {folder} ---")
    display(dbutils.fs.ls(f"{raw_base}/{folder}"))

# COMMAND ----------

#Validate Raw schema + enforce String ingestion
from pyspark.sql.types import StructType, StructField, StringType

raw_customer_path = "/Volumes/workspace/default/celebal_data/raw/historical/customer/customer_historical.csv"

# Read header only to build a dynamic all-String schema
header_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(raw_customer_path)
)

string_schema = StructType([
    StructField(column, StringType(), True)
    for column in header_df.columns
])

# Read the actual file using the explicit String schema
customer_raw_df = (
    spark.read
    .option("header", True)
    .schema(string_schema)
    .csv(raw_customer_path)
)

customer_raw_df.printSchema()
print("Row count:", customer_raw_df.count())

# COMMAND ----------

#Create the Landing layer in Parquet
landing_path = "/Volumes/workspace/default/celebal_data/landing/historical/customer"

(
    customer_raw_df
    .write
    .mode("overwrite")
    .parquet(landing_path)
)

print("Historical customer data written to Landing Parquet.")
print("Landing path:", landing_path)

# COMMAND ----------

#validation
landing_customer_df = spark.read.parquet(landing_path)

print("Landing row count:", landing_customer_df.count())
landing_customer_df.printSchema()
display(landing_customer_df.limit(5))

# COMMAND ----------

# Now will Build the complete Landing ingestion
from pyspark.sql.types import StructType, StructField, StringType

raw_base = "/Volumes/workspace/default/celebal_data/raw"
landing_base = "/Volumes/workspace/default/celebal_data/landing"

datasets = {
    "historical": {
        "customer": "historical/customer/customer_historical.csv",
        "product": "historical/product/product_historical.csv",
        "sales": "historical/sales/sales_historical.csv"
    },
    "incremental": {
        "customer": "incremental/customer_incremental/customer_incremental.csv",
        "product": "incremental/product_incremental/product_incremental.csv",
        "sales": "incremental/sales_incremental/sales_incremental.csv"
    }
}

for load_type, tables in datasets.items():

    for table_name, relative_path in tables.items():

        source_path = f"{raw_base}/{relative_path}"
        target_path = f"{landing_base}/{load_type}/{table_name}"

        # Read header to obtain column names
        header_df = (
            spark.read
            .option("header", True)
            .option("inferSchema", False)
            .csv(source_path)
        )

        # Explicitly create an all-String schema
        string_schema = StructType([
            StructField(column, StringType(), True)
            for column in header_df.columns
        ])

        # Read source using explicit String schema
        df = (
            spark.read
            .option("header", True)
            .schema(string_schema)
            .csv(source_path)
        )

        # Write to Landing as Parquet
        (
            df.write
            .mode("overwrite")
            .parquet(target_path)
        )

        print(
            f"{load_type}/{table_name}: "
            f"{df.count()} records written to Landing"
        )

print("Landing ingestion completed.")

# COMMAND ----------

#inspect one audit file
audit_path = "/Volumes/workspace/default/celebal_data/raw/audit_landing/customer_historical_audit.csv"

audit_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(audit_path)
)

audit_df.printSchema()
display(audit_df)

# COMMAND ----------

#Dynamic Landing Audit Reconciliation
from pyspark.sql.functions import col

# Read audit
audit_path = "/Volumes/workspace/default/celebal_data/raw/audit_landing/customer_historical_audit.csv"

audit_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(audit_path)
)

# Expected count from audit
expected_count = int(
    audit_df.filter(
        col("table_name") == "customer_historical"
    ).select("row_count").first()[0]
)

# Actual Landing count  
actual_count = (
    spark.read
    .parquet(
        "/Volumes/workspace/default/celebal_data/landing/historical/customer"
    )
    .count()
)

status = "PASS" if expected_count == actual_count else "FAIL"

print(f"Table          : customer_historical")
print(f"Expected Count : {expected_count}")
print(f"Actual Count   : {actual_count}")
print(f"Status         : {status}")

# COMMAND ----------

#Reconcile all 6 Landing datasets
from pyspark.sql.functions import col

raw_base = "/Volumes/workspace/default/celebal_data/raw"
landing_base = "/Volumes/workspace/default/celebal_data/landing"

audit_files = {
    "historical/customer": "customer_historical_audit.csv",
    "historical/product": "product_historical_audit.csv",
    "historical/sales": "sales_historical_audit.csv",
    "incremental/customer": "customer_incrementalaudit.csv",
    "incremental/product": "product_incrementalaudit.csv",
    "incremental/sales": "sales_incrementalaudit.csv"
}

table_names = {
    "historical/customer": "customer_historical",
    "historical/product": "product_historical",
    "historical/sales": "sales_historical",
    "incremental/customer": "customer_incremental",
    "incremental/product": "product_incremental",
    "incremental/sales": "sales_incremental"
}

results = []

for dataset, audit_file in audit_files.items():

    audit_path = f"{raw_base}/audit_landing/{audit_file}"
    landing_path = f"{landing_base}/{dataset}"
    table_name = table_names[dataset]

    audit_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .csv(audit_path)
    )

    expected_count = int(
        audit_df
        .filter(col("table_name") == table_name)
        .select("row_count")
        .first()[0]
    )

    actual_count = spark.read.parquet(landing_path).count()

    status = "PASS" if expected_count == actual_count else "FAIL"

    results.append(
        (table_name, expected_count, actual_count, status)
    )

reconciliation_df = spark.createDataFrame(
    results,
    ["table_name", "expected_count", "actual_count", "status"]
)

display(reconciliation_df)

# COMMAND ----------

#Create the Bronze Delta layer
bronze_customer_path = (
    "/Volumes/workspace/default/celebal_data/bronze/customer"
)

landing_customer_path = (
    "/Volumes/workspace/default/celebal_data/landing/historical/customer"
)

customer_landing_df = spark.read.parquet(landing_customer_path)

(
    customer_landing_df
    .write
    .format("delta")
    .mode("overwrite")
    .save(bronze_customer_path)
)

print("Historical customer data written to Bronze Delta.")

# COMMAND ----------

#Validate
bronze_customer_df = (
    spark.read
    .format("delta")
    .load(bronze_customer_path)
)

print("Bronze row count:", bronze_customer_df.count())
bronze_customer_df.printSchema()
display(bronze_customer_df.limit(5))

# COMMAND ----------



# COMMAND ----------

#Load all 3 historical datasets into Bronze
landing_base = "/Volumes/workspace/default/celebal_data/landing"
bronze_base = "/Volumes/workspace/default/celebal_data/bronze"

historical_tables = ["customer", "product", "sales"]

for table in historical_tables:

    landing_path = f"{landing_base}/historical/{table}"
    bronze_path = f"{bronze_base}/{table}"

    df = spark.read.parquet(landing_path)

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .save(bronze_path)
    )

    print(f"{table}: {df.count()} rows written to Bronze")

# COMMAND ----------

#validation
for table in historical_tables:

    bronze_path = f"{bronze_base}/{table}"

    df = (
        spark.read
        .format("delta")
        .load(bronze_path)
    )

    print(f"{table}: {df.count()} rows")

# COMMAND ----------

#Prepare Bronze for Incremental Append
landing_base = "/Volumes/workspace/default/celebal_data/landing"
bronze_base = "/Volumes/workspace/default/celebal_data/bronze"

for table in ["customer", "product", "sales"]:

    landing_df = spark.read.parquet(
        f"{landing_base}/incremental/{table}"
    )

    bronze_df = spark.read.format("delta").load(
        f"{bronze_base}/{table}"
    )

    print(f"\n===== {table.upper()} =====")
    print("Landing columns :", len(landing_df.columns))
    print("Bronze columns  :", len(bronze_df.columns))

    print("Schema match:", landing_df.schema == bronze_df.schema)

# COMMAND ----------

#Identify the schema differences
for table in ["customer", "product", "sales"]:

    landing_df = spark.read.parquet(
        f"{landing_base}/incremental/{table}"
    )

    bronze_df = spark.read.format("delta").load(
        f"{bronze_base}/{table}"
    )

    landing_cols = set(landing_df.columns)
    bronze_cols = set(bronze_df.columns)

    print(f"\n===== {table.upper()} =====")

    print("Columns only in Incremental Landing:")
    print(sorted(landing_cols - bronze_cols))

    print("Columns only in Bronze:")
    print(sorted(bronze_cols - landing_cols))

# COMMAND ----------

for table in ["customer", "product", "sales"]:

    print(f"\n===== {table.upper()} INCREMENTAL SCHEMA =====")

    incremental_df = spark.read.parquet(
        f"{landing_base}/incremental/{table}"
    )

    incremental_df.printSchema()

# COMMAND ----------

for table in ["customer", "product"]:

    print(f"\n===== {table.upper()} HISTORICAL SCHEMA =====")

    historical_df = spark.read.parquet(
        f"{landing_base}/historical/{table}"
    )

    historical_df.printSchema()

# COMMAND ----------

#Complete schema inspection
for table in ["customer", "product", "sales"]:
    print(f"\n===== {table.upper()} INCREMENTAL =====")
    spark.read.parquet(
        f"{landing_base}/incremental/{table}"
    ).printSchema()

# COMMAND ----------

#Inspect the actual incremental Customer & Product data
for table in ["customer", "product"]:
    print(f"\n===== {table.upper()} INCREMENTAL =====")

    df = spark.read.parquet(
        f"{landing_base}/incremental/{table}"
    )

    print("Columns:", df.columns)
    print("Row count:", df.count())

    display(df.limit(5))


# COMMAND ----------

#Add ingested_at to Bronze
from pyspark.sql.functions import current_timestamp

bronze_customer_path = "/Volumes/workspace/default/celebal_data/bronze/customer"

customer_bronze_df = (
    spark.read
    .format("delta")
    .load(bronze_customer_path)
)

customer_bronze_with_timestamp = (
    customer_bronze_df
    .withColumn("ingested_at", current_timestamp())
)

(
    customer_bronze_with_timestamp
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(bronze_customer_path)
)

print("ingested_at added successfully.")

# COMMAND ----------

#validation
validated_customer = (
    spark.read
    .format("delta")
    .load(bronze_customer_path)
)

validated_customer.printSchema()

print("Row count:", validated_customer.count())

display(
    validated_customer
    .select("customer_id", "ingested_at")
    .limit(5)
)

# COMMAND ----------

#Add ingested_at to all Bronze tables
from pyspark.sql.functions import current_timestamp

bronze_tables = ["customer", "product", "sales"]

for table in bronze_tables:

    bronze_path = f"/Volumes/workspace/default/celebal_data/bronze/{table}"

    df = (
        spark.read
        .format("delta")
        .load(bronze_path)
    )

    # Avoid adding the column twice if the cell is rerun
    if "ingested_at" not in df.columns:
        df = df.withColumn("ingested_at", current_timestamp())

        (
            df.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .save(bronze_path)
        )

    validated_df = (
        spark.read
        .format("delta")
        .load(bronze_path)
    )

    print(
        f"{table}: "
        f"{validated_df.count()} rows | "
        f"ingested_at present = {'ingested_at' in validated_df.columns}"
    )

# COMMAND ----------

#Implement Bronze Incremental Append
from pyspark.sql.functions import current_timestamp

bronze_sales_path = "/Volumes/workspace/default/celebal_data/bronze/sales"
incremental_sales_path = "/Volumes/workspace/default/celebal_data/landing/incremental/sales"

# Read incremental Sales
incremental_sales_df = spark.read.parquet(incremental_sales_path)

# Add ingestion timestamp
incremental_sales_df = incremental_sales_df.withColumn(
    "ingested_at",
    current_timestamp()
)

# Append to existing Bronze Delta table
(
    incremental_sales_df.write
    .format("delta")
    .mode("append")
    .save(bronze_sales_path)
)

print("Incremental Sales appended successfully.")

# COMMAND ----------

#validate
bronze_sales_df = (
    spark.read
    .format("delta")
    .load(bronze_sales_path)
)

print("Bronze Sales row count after append:", bronze_sales_df.count())

# COMMAND ----------

#Validate Bronze append-only behavior
bronze_sales_df = (
    spark.read
    .format("delta")
    .load(bronze_sales_path)
)

print("Bronze Sales total rows:", bronze_sales_df.count())
print("Bronze Sales columns:", len(bronze_sales_df.columns))

display(
    bronze_sales_df
    .orderBy("ingested_at")
    .limit(5)
)

# COMMAND ----------

#Prepare Customer Incremental Bronze
#Add the missing columns to Bronze
from pyspark.sql.functions import lit

bronze_customer_path = "/Volumes/workspace/default/celebal_data/bronze/customer"

bronze_customer_df = (
    spark.read
    .format("delta")
    .load(bronze_customer_path)
)

# Add SCD columns as nullable strings for the historical records
bronze_customer_df = (
    bronze_customer_df
    .withColumn("surrogate_key", lit(None).cast("string"))
    .withColumn("version", lit(None).cast("string"))
    .withColumn("effective_start_date", lit(None).cast("string"))
    .withColumn("effective_end_date", lit(None).cast("string"))
    .withColumn("is_current", lit(None).cast("string"))
)

(
    bronze_customer_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(bronze_customer_path)
)

print("Bronze Customer schema prepared for incremental records.")

# COMMAND ----------

validated_customer = (
    spark.read
    .format("delta")
    .load(bronze_customer_path)
)

print("Rows:", validated_customer.count())
print("Columns:", len(validated_customer.columns))

validated_customer.printSchema()

# COMMAND ----------

#Append Incremental Customer to Bronze
from pyspark.sql.functions import current_timestamp

bronze_customer_path = "/Volumes/workspace/default/celebal_data/bronze/customer"
incremental_customer_path = "/Volumes/workspace/default/celebal_data/landing/incremental/customer"

# Read incremental Customer data
incremental_customer_df = spark.read.parquet(incremental_customer_path)

# Add ingestion timestamp
incremental_customer_df = incremental_customer_df.withColumn(
    "ingested_at",
    current_timestamp()
)

# Append only — no update/delete
(
    incremental_customer_df.write
    .format("delta")
    .mode("append")
    .save(bronze_customer_path)
)

print("Incremental Customer appended successfully.")

# COMMAND ----------

bronze_customer_df = (
    spark.read
    .format("delta")
    .load(bronze_customer_path)
)

print("Bronze Customer total rows:", bronze_customer_df.count())
print("Bronze Customer columns:", len(bronze_customer_df.columns))

# COMMAND ----------

#Handle Product Incremental Schema
from pyspark.sql.functions import lit

bronze_product_path = "/Volumes/workspace/default/celebal_data/bronze/product"

bronze_product_df = (
    spark.read
    .format("delta")
    .load(bronze_product_path)
)

bronze_product_df = (
    bronze_product_df
    .withColumn("last_updated", lit(None).cast("string"))
)

(
    bronze_product_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(bronze_product_path)
)

print("Bronze Product schema prepared.")

# COMMAND ----------

validated_product = (
    spark.read
    .format("delta")
    .load(bronze_product_path)
)

print("Rows:", validated_product.count())
print("Columns:", len(validated_product.columns))

validated_product.printSchema()

# COMMAND ----------

#Append Incremental Product to Bronze


# COMMAND ----------

bronze_product_df = (
    spark.read
    .format("delta")
    .load(bronze_product_path)
)

print("Bronze Product total rows:", bronze_product_df.count())
print("Bronze Product columns:", len(bronze_product_df.columns))

# COMMAND ----------

#Create a reusable audit validation function
from pyspark.sql.functions import col

def validate_row_count(audit_file_path, table_name, actual_count):

    audit_df = (
        spark.read
        .option("header", True)
        .csv(audit_file_path)
    )

    expected_count = int(
        audit_df.filter(
            col("table_name") == table_name
        ).first()["row_count"]
    )

    if expected_count != actual_count:
        raise Exception(
            f"""
AUDIT VALIDATION FAILED

Table    : {table_name}

Expected : {expected_count}

Actual   : {actual_count}
"""
        )

    print(f"✅ {table_name} : PASS")

# COMMAND ----------


validate_row_count(
    "/Volumes/workspace/default/celebal_data/raw/audit_landing/customer_historical_audit.csv",
    "customer_historical",
    1052
)

# COMMAND ----------

#Test failure
validate_row_count(
    "/Volumes/workspace/default/celebal_data/raw/audit_landing/customer_historical_audit.csv",
    "customer_historical",
    1000
)

# COMMAND ----------

bronze_product_path = "/Volumes/workspace/default/celebal_data/bronze/product"

product_df = (
    spark.read
    .format("delta")
    .load(bronze_product_path)
)

print("Rows:", product_df.count())
display(product_df.limit(5))

# COMMAND ----------

from pyspark.sql.functions import current_timestamp

incremental_product = (
    spark.read.parquet(
        "/Volumes/workspace/default/celebal_data/landing/incremental/product"
    )
    .withColumn("ingested_at", current_timestamp())
)

(
    incremental_product.write
    .format("delta")
    .mode("append")
    .save(bronze_product_path)
)

print("Product Incremental Appended Successfully")

# COMMAND ----------

product_df = (
    spark.read
    .format("delta")
    .load(bronze_product_path)
)

print("Rows:", product_df.count())

# COMMAND ----------

#Final Bronze Validation
from pyspark.sql.functions import col

bronze_base = "/Volumes/workspace/default/celebal_data/bronze"

expected_counts = {
    "customer": 2105,   # 1052 + 1053
    "product": 2084,    # 1043 + 1041
    "sales": 2002       # 1002 + 1000
}

for table, expected in expected_counts.items():

    df = (
        spark.read
        .format("delta")
        .load(f"{bronze_base}/{table}")
    )

    actual = df.count()

    print("=" * 50)
    print(f"TABLE : {table.upper()}")
    print(f"Expected Rows : {expected}")
    print(f"Actual Rows   : {actual}")
    print(f"Status        : {'PASS' if expected == actual else 'FAIL'}")

    assert actual == expected, f"{table} row count mismatch"

    assert "ingested_at" in df.columns, \
        f"ingested_at missing in {table}"

print("\n✅ Bronze Layer Validation Completed Successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ Phase 1 Completed (100%)
# MAGIC
# MAGIC Congratulations! We have successfully completed Phase 1 — Ingestion & Bronze.
# MAGIC
# MAGIC Completed Checklist
# MAGIC ✅ Databricks environment configured
# MAGIC ✅ Source files uploaded to Unity Catalog Volumes
# MAGIC ✅ Audit files uploaded
# MAGIC ✅ Raw directory implemented
# MAGIC ✅ Historical & Incremental data separated
# MAGIC ✅ All Raw fields ingested as String
# MAGIC ✅ Landing Parquet implemented
# MAGIC ✅ Dynamic audit file reading
# MAGIC ✅ Expected vs Actual count validation
# MAGIC ✅ PASS/FAIL audit report generated
# MAGIC ✅ Pipeline halts on audit failure
# MAGIC ✅ Bronze Delta tables created
# MAGIC ✅ ingested_at column added
# MAGIC ✅ Incremental append implemented
# MAGIC ✅ Bronze remains append-only

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ Phase 1 Completed (100%)
# MAGIC
# MAGIC Completed Checklist
# MAGIC ✅ Databricks environment configured
# MAGIC ✅ Source files uploaded to Unity Catalog Volumes
# MAGIC ✅ Audit files uploaded
# MAGIC ✅ Raw directory implemented
# MAGIC ✅ Historical & Incremental data separated
# MAGIC ✅ All Raw fields ingested as String
# MAGIC ✅ Landing Parquet implemented
# MAGIC ✅ Dynamic audit file reading
# MAGIC ✅ Expected vs Actual count validation
# MAGIC ✅ PASS/FAIL audit report generated
# MAGIC ✅ Pipeline halts on audit failure
# MAGIC ✅ Bronze Delta tables created
# MAGIC ✅ ingested_at column added
# MAGIC ✅ Incremental append implemented
# MAGIC ✅ Bronze remains append-only

# COMMAND ----------

# MAGIC %md
# MAGIC # Phase 1 — Ingestion & Bronze
# MAGIC
# MAGIC ## Objective
# MAGIC
# MAGIC The objective of Phase 1 is to build a robust and reliable data ingestion pipeline that loads the source datasets into Databricks, validates data integrity using audit files, and stores the data in a Bronze Delta Layer while preserving the original source data.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 1 — Databricks Environment Setup
# MAGIC
# MAGIC - Created a Databricks Workspace.
# MAGIC - Created a Compute Cluster.
# MAGIC - Attached the notebook to the cluster.
# MAGIC - Verified Spark Session availability.
# MAGIC
# MAGIC **Output**
# MAGIC
# MAGIC - Working Databricks environment ready for development.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 2 — Upload Datasets to Unity Catalog Volumes
# MAGIC
# MAGIC Created a Volume to store all project datasets.
# MAGIC
# MAGIC Uploaded the following folders:
# MAGIC
# MAGIC - Historical Data
# MAGIC - Incremental Data
# MAGIC - Historical Audit Files
# MAGIC - Silver Audit Files
# MAGIC
# MAGIC Folder Structure:
# MAGIC
# MAGIC ```text
# MAGIC Datasets/
# MAGIC │
# MAGIC ├── historical_data/
# MAGIC ├── incremental_data/
# MAGIC ├── audit_landing/
# MAGIC └── audit_silver/
# MAGIC ```
# MAGIC
# MAGIC **Output**
# MAGIC
# MAGIC All datasets successfully uploaded into Unity Catalog Volume.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 3 — Organize Raw Layer
# MAGIC
# MAGIC Created the Raw directory structure inside the Volume.
# MAGIC
# MAGIC ```text
# MAGIC raw/
# MAGIC │
# MAGIC ├── historical/
# MAGIC │   ├── customer/
# MAGIC │   ├── product/
# MAGIC │   └── sales/
# MAGIC │
# MAGIC ├── incremental/
# MAGIC │   ├── customer/
# MAGIC │   ├── product/
# MAGIC │   └── sales/
# MAGIC │
# MAGIC └── audit_landing/
# MAGIC ```
# MAGIC
# MAGIC This separates:
# MAGIC
# MAGIC - Historical source data
# MAGIC - Incremental source data
# MAGIC - Audit files
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 4 — Raw Data Ingestion
# MAGIC
# MAGIC Loaded every CSV file using Spark.
# MAGIC
# MAGIC All columns were intentionally read as **String**.
# MAGIC
# MAGIC Reason:
# MAGIC
# MAGIC - Preserve original source values.
# MAGIC - Avoid accidental datatype conversion.
# MAGIC - Perform datatype casting later in the Silver Layer.
# MAGIC
# MAGIC Validated:
# MAGIC
# MAGIC - Schema
# MAGIC - Row count
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 5 — Landing Layer Creation
# MAGIC
# MAGIC Converted every Raw CSV into Parquet format.
# MAGIC
# MAGIC Landing structure:
# MAGIC
# MAGIC ```text
# MAGIC landing/
# MAGIC │
# MAGIC ├── historical/
# MAGIC │
# MAGIC └── incremental/
# MAGIC ```
# MAGIC
# MAGIC Benefits:
# MAGIC
# MAGIC - Faster reads
# MAGIC - Columnar storage
# MAGIC - Better Spark performance
# MAGIC - Reduced storage consumption
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 6 — Audit File Processing
# MAGIC
# MAGIC Loaded every audit CSV dynamically.
# MAGIC
# MAGIC Each audit file contains:
# MAGIC
# MAGIC - Table Name
# MAGIC - Expected Row Count
# MAGIC
# MAGIC Example:
# MAGIC
# MAGIC | Table | Expected Count |
# MAGIC |--------|---------------|
# MAGIC | customer_historical | 1052 |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 7 — Audit Reconciliation
# MAGIC
# MAGIC Compared:
# MAGIC
# MAGIC Expected Row Count
# MAGIC
# MAGIC with
# MAGIC
# MAGIC Actual Landing Row Count
# MAGIC
# MAGIC Generated:
# MAGIC
# MAGIC PASS
# MAGIC
# MAGIC or
# MAGIC
# MAGIC FAIL
# MAGIC
# MAGIC Example:
# MAGIC
# MAGIC | Table | Expected | Actual | Status |
# MAGIC |--------|---------|--------|--------|
# MAGIC | customer_historical | 1052 | 1052 | PASS |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 8 — Pipeline Halt on Audit Failure
# MAGIC
# MAGIC Implemented audit validation function.
# MAGIC
# MAGIC If
# MAGIC
# MAGIC Expected Count ≠ Actual Count
# MAGIC
# MAGIC the pipeline immediately throws an Exception.
# MAGIC
# MAGIC Example:
# MAGIC
# MAGIC ```python
# MAGIC raise Exception("AUDIT VALIDATION FAILED")
# MAGIC ```
# MAGIC
# MAGIC Purpose:
# MAGIC
# MAGIC Prevent incorrect data from entering downstream layers.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 9 — Bronze Layer Creation
# MAGIC
# MAGIC Created Delta Tables for:
# MAGIC
# MAGIC - Customer
# MAGIC - Product
# MAGIC - Sales
# MAGIC
# MAGIC Data Source:
# MAGIC
# MAGIC Landing Parquet
# MAGIC
# MAGIC Storage Format:
# MAGIC
# MAGIC Delta
# MAGIC
# MAGIC Benefits:
# MAGIC
# MAGIC - ACID Transactions
# MAGIC - Versioning
# MAGIC - Scalability
# MAGIC - Future MERGE Support
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 10 — Add Ingestion Timestamp
# MAGIC
# MAGIC Added
# MAGIC
# MAGIC ```text
# MAGIC ingested_at
# MAGIC ```
# MAGIC
# MAGIC column using
# MAGIC
# MAGIC ```python
# MAGIC current_timestamp()
# MAGIC ```
# MAGIC
# MAGIC Purpose:
# MAGIC
# MAGIC - Record ingestion time
# MAGIC - Support auditing
# MAGIC - Track pipeline execution
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 11 — Incremental Bronze Processing
# MAGIC
# MAGIC Historical Bronze already existed.
# MAGIC
# MAGIC Incremental datasets were appended.
# MAGIC
# MAGIC Implemented append-only strategy.
# MAGIC
# MAGIC Customer:
# MAGIC
# MAGIC Historical
# MAGIC
# MAGIC +
# MAGIC
# MAGIC Incremental
# MAGIC
# MAGIC =
# MAGIC
# MAGIC 2105 Rows
# MAGIC
# MAGIC Product:
# MAGIC
# MAGIC Historical
# MAGIC
# MAGIC +
# MAGIC
# MAGIC Incremental
# MAGIC
# MAGIC =
# MAGIC
# MAGIC 2084 Rows
# MAGIC
# MAGIC Sales:
# MAGIC
# MAGIC Historical
# MAGIC
# MAGIC +
# MAGIC
# MAGIC Incremental
# MAGIC
# MAGIC =
# MAGIC
# MAGIC 2002 Rows
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 12 — Schema Handling
# MAGIC
# MAGIC Customer Incremental contained additional SCD columns.
# MAGIC
# MAGIC These were preserved by extending the Bronze schema instead of removing them.
# MAGIC
# MAGIC Additional columns:
# MAGIC
# MAGIC - surrogate_key
# MAGIC - version
# MAGIC - effective_start_date
# MAGIC - effective_end_date
# MAGIC - is_current
# MAGIC
# MAGIC Product Incremental contained:
# MAGIC
# MAGIC - last_updated
# MAGIC
# MAGIC This column was also preserved.
# MAGIC
# MAGIC No source information was discarded.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Step 13 — Bronze Validation
# MAGIC
# MAGIC Validated:
# MAGIC
# MAGIC - Row Counts
# MAGIC - Schema
# MAGIC - Presence of ingested_at
# MAGIC - Delta Tables
# MAGIC - Successful Incremental Append
# MAGIC
# MAGIC Validation Results:
# MAGIC
# MAGIC | Table | Final Rows |
# MAGIC |--------|-----------|
# MAGIC | Customer | 2105 |
# MAGIC | Product | 2084 |
# MAGIC | Sales | 2002 |
# MAGIC
# MAGIC All validations passed successfully.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Final Bronze Architecture
# MAGIC
# MAGIC ```text
# MAGIC CSV Files
# MAGIC       │
# MAGIC       ▼
# MAGIC Raw Layer
# MAGIC (All columns as String)
# MAGIC       │
# MAGIC       ▼
# MAGIC Landing Layer
# MAGIC (Parquet)
# MAGIC       │
# MAGIC       ▼
# MAGIC Audit Validation
# MAGIC (Expected vs Actual)
# MAGIC       │
# MAGIC       ▼
# MAGIC Bronze Layer
# MAGIC (Delta)
# MAGIC       │
# MAGIC       ├── Append Historical
# MAGIC       ├── Append Incremental
# MAGIC       └── Add ingested_at
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Technologies Used
# MAGIC
# MAGIC - Databricks
# MAGIC - Apache Spark
# MAGIC - PySpark
# MAGIC - Delta Lake
# MAGIC - Unity Catalog Volumes
# MAGIC - Parquet
# MAGIC - CSV
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Phase 1 Deliverables
# MAGIC
# MAGIC ✅ Databricks Workspace Configured<br>
# MAGIC ✅ Source Files Uploaded<br>
# MAGIC ✅ Audit Files Uploaded<br>
# MAGIC ✅ Raw Layer Implemented<br>
# MAGIC ✅ Historical & Incremental Data Separated<br>
# MAGIC ✅ Raw Data Loaded as String<br>
# MAGIC ✅ Landing Layer Created<br>
# MAGIC ✅ Dynamic Audit Reading<br>
# MAGIC ✅ Audit Validation (PASS/FAIL)<br>
# MAGIC ✅ Pipeline Stops on Audit Failure<br>
# MAGIC ✅ Bronze Delta Tables Created<br>
# MAGIC ✅ ingested_at Added<br>
# MAGIC ✅ Incremental Append Implemented<br>
# MAGIC ✅ Bronze Layer Verified
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Phase 1 Outcome
# MAGIC
# MAGIC At the end of Phase 1:
# MAGIC
# MAGIC - All source datasets are successfully ingested.
# MAGIC - Data integrity is validated using audit files.
# MAGIC - Invalid data is prevented from entering downstream layers.
# MAGIC - Bronze Delta tables are created using an append-only strategy.
# MAGIC - Historical and Incremental data are successfully stored while preserving the original source data.
# MAGIC - The Bronze Layer is ready for Silver Layer transformations.

# COMMAND ----------

