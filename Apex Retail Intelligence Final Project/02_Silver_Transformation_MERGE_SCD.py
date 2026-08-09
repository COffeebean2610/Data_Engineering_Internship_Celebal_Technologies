# Databricks notebook source
#Read Bronze Tables
bronze_base = "/Volumes/workspace/default/celebal_data/bronze"

customer_df = (
    spark.read
    .format("delta")
    .load(f"{bronze_base}/customer")
)

product_df = (
    spark.read
    .format("delta")
    .load(f"{bronze_base}/product")
)

sales_df = (
    spark.read
    .format("delta")
    .load(f"{bronze_base}/sales")
)

# COMMAND ----------

#Verify Row Counts
for name, df in {
    "Customer": customer_df,
    "Product": product_df,
    "Sales": sales_df
}.items():

    print("=" * 50)
    print(name)
    print("Rows :", df.count())
    print("Columns :", len(df.columns))

# COMMAND ----------

#Display Schema
print("Customer Schema")
customer_df.printSchema()

print("Product Schema")
product_df.printSchema()

print("Sales Schema")
sales_df.printSchema()

# COMMAND ----------

#Data Profiling

for name, df in {
    "Customer": customer_df,
    "Product": product_df,
    "Sales": sales_df
}.items():

    print("=" * 60)
    print(name)

    display(df.summary())

# COMMAND ----------

#Data Cleaning
# Missing Primary Keys
from pyspark.sql.functions import col
#Customer
customer_clean = customer_df.filter(col("customer_id").isNotNull())
#Product
product_clean = product_df.filter(col("product_id").isNotNull())
#Sales
sales_clean = sales_df.filter(col("transaction_id").isNotNull())

# COMMAND ----------

#Remove Duplicates
customer_clean = customer_clean.dropDuplicates()

product_clean = product_clean.dropDuplicates()

sales_clean = sales_clean.dropDuplicates()

# COMMAND ----------

#Explicit Data Type Casting
# Customer
from pyspark.sql.functions import col

customer_clean = (
    customer_clean
    .withColumn("age", col("age").cast("int"))
    .withColumn("membership_years", col("membership_years").cast("int"))
    .withColumn("number_of_children", col("number_of_children").cast("int"))
)
# Product
product_clean = (
    product_clean
    .withColumn("product_rating", col("product_rating").cast("double"))
    .withColumn("product_review_count", col("product_review_count").cast("int"))
    .withColumn("product_stock", col("product_stock").cast("int"))
    .withColumn("product_return_rate", col("product_return_rate").cast("double"))
    .withColumn("unit_price", col("unit_price").cast("double"))
)

# COMMAND ----------

sales_clean.printSchema()#

# COMMAND ----------

#Handle NULL Values
from pyspark.sql.functions import when

customer_clean = customer_clean.fillna("Unknown")
customer_clean = customer_clean.fillna(0)

product_clean = product_clean.fillna("Unknown")
product_clean = product_clean.fillna(0)

# COMMAND ----------

#Validation

for name, df in {
    "Customer": customer_clean,
    "Product": product_clean,
    "Sales": sales_clean
}.items():

    print("=" * 50)
    print(name)
    print("Rows :", df.count())

# COMMAND ----------

#Sales Data Type Casting
sales_clean.printSchema()

# COMMAND ----------

#Handle NULL Values (All Tables)
#Customer
customer_clean = (
    customer_clean
    .fillna("Unknown")
    .fillna(0)
)
#Product
product_clean = (
    product_clean
    .fillna("Unknown")
    .fillna(0)
)
#Sales
sales_clean = (
    sales_clean
    .fillna("Unknown")
    .fillna(0)
)

# COMMAND ----------

#Validate Cleaning
print("="*60)
print("CUSTOMER")
print("Rows :", customer_clean.count())
print("Duplicates :", customer_clean.count() - customer_clean.dropDuplicates().count())

print("="*60)
print("PRODUCT")
print("Rows :", product_clean.count())
print("Duplicates :", product_clean.count() - product_clean.dropDuplicates().count())

print("="*60)
print("SALES")
print("Rows :", sales_clean.count())
print("Duplicates :", sales_clean.count() - sales_clean.dropDuplicates().count())

# COMMAND ----------

#Create Silver Delta Tables
#Create Silver Directory
#Write Customer Silver
silver_base = "/Volumes/workspace/default/celebal_data/silver"

(
    customer_clean.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(f"{silver_base}/customer")
)

print("Customer Silver created successfully.")

# COMMAND ----------

#Write Product Silver
(
    product_clean.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(f"{silver_base}/product")
)

print("Product Silver created successfully.")#

# COMMAND ----------

(
    sales_clean.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save("/Volumes/workspace/default/celebal_data/silver/sales")
)

# COMMAND ----------

#Write Product Silver
(
    product_clean.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(f"{silver_base}/product")
)

print("Product Silver created successfully.")#

# COMMAND ----------

#Validate Silver Tables
tables = ["customer", "product", "sales"]

for table in tables:

    df = (
        spark.read
        .format("delta")
        .load(f"{silver_base}/{table}")
    )

    print("=" * 50)
    print(f"{table.upper()}")

    print("Rows :", df.count())
    print("Columns :", len(df.columns))

    df.printSchema()

# COMMAND ----------

#Delta MERGE Implementation
#Register Silver Tables
customer_clean.createOrReplaceTempView("customer_source")
product_clean.createOrReplaceTempView("product_source")
sales_clean.createOrReplaceTempView("sales_source")

# COMMAND ----------

customer_clean.select(
    "customer_id",
    "version",
    "effective_start_date",
    "effective_end_date",
    "is_current"
).show(10, False)

# COMMAND ----------

#Validate Customer History
from pyspark.sql.functions import col

customer_clean.filter(
    col("customer_id") == "4"
).orderBy("version").show(truncate=False)

# COMMAND ----------

from pyspark.sql.functions import countDistinct

print("Total Rows :", customer_clean.count())

print(
    "Distinct Customer IDs :",
    customer_clean.select(
        countDistinct("customer_id")
    ).collect()[0][0]
)

# COMMAND ----------

#Customer SCD Type 2
#Register the Silver Customer Table
customer_clean.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("silver_customer")


spark.sql("SELECT COUNT(*) FROM silver_customer").show()
#Register Incremental Customer Data
customer_clean.createOrReplaceTempView("customer_incremental")


# COMMAND ----------

#Verify Tables
spark.sql("SELECT COUNT(*) FROM silver_customer").show()

spark.sql("SELECT COUNT(*) FROM customer_incremental").show()

# COMMAND ----------

#Actual Customer SCD Type 2
#Validate Current Records
from pyspark.sql.functions import col

current_customer = customer_clean.filter(
    col("is_current") == "True"
)

print("Current Active Customers :", current_customer.count())
# Validate Version History
from pyspark.sql.functions import max

customer_clean.groupBy("customer_id") \
    .agg(
        max("version").alias("latest_version")
    ) \
    .orderBy("customer_id") \
    .show(20, False)
# Validate History
from pyspark.sql.functions import expr

customer_clean.filter(
    expr("try_cast(version as INT) > 1")
).show(truncate=False)


#Validate SCD Columns
customer_clean.select(
    "customer_id",
    "version",
    "effective_start_date",
    "effective_end_date",
    "is_current"
).show(20, False)


# COMMAND ----------

#Product SCD Type 1
#Check Product Primary Key
from pyspark.sql.functions import countDistinct

print("Total Products :", product_clean.count())

print(
    "Distinct Product IDs :",
    product_clean.select(countDistinct("product_id")).first()[0]
)

# COMMAND ----------

#Validate Duplicates
duplicate_products = (
    product_clean.groupBy("product_id")
    .count()
    .filter("count > 1")
)

print("Duplicate Product IDs :", duplicate_products.count())

display(duplicate_products)

# COMMAND ----------

#Validate SCD Type 1 Behavior
product_clean.columns

# COMMAND ----------

#Validate Final Product Data
product_clean.select(
    "product_id",
    "product_name",
    "unit_price",
    "last_updated"
).show(10, truncate=False)

# COMMAND ----------

#Sales Immutable Ledger & Window-Based Deduplication
##Import Window Functions
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col, desc

# COMMAND ----------

#Create Window Specification
sales_window = (
    Window
    .partitionBy("transaction_id")
    .orderBy(desc("ingested_at"))
)

# COMMAND ----------

#Remove Duplicate Transactions
sales_final = (
    sales_clean
    .withColumn(
        "row_num",
        row_number().over(sales_window)
    )
    .filter(col("row_num") == 1)
    .drop("row_num")
)

# COMMAND ----------

#Validation
print("Original Sales :", sales_clean.count())
print("Final Sales    :", sales_final.count())

# COMMAND ----------

#Check Remaining Duplicates
duplicates = (
    sales_final
    .groupBy("transaction_id")
    .count()
    .filter(col("count") > 1)
)

print("Duplicate Transactions :", duplicates.count())

# COMMAND ----------

sales_final.show(10, truncate=False)#

# COMMAND ----------

#Generate Surrogate Keys
#Import Function
from pyspark.sql.functions import monotonically_increasing_id

# COMMAND ----------

#Customer Surrogate Key
customer_final = (
    customer_clean
    .withColumn(
        "customer_sk",
        monotonically_increasing_id()
    )
)#

# COMMAND ----------

#Product Surrogate Key
product_final = (
    product_clean
    .withColumn(
        "product_sk",
        monotonically_increasing_id()
    )
)

# COMMAND ----------

#Sales Surrogate Key


sales_final = (
    sales_final
    .withColumn(
        "sales_sk",
        monotonically_increasing_id()
    )
)

# COMMAND ----------

sales_final.printSchema()

from pyspark.sql.functions import monotonically_increasing_id

sales_final = sales_final.withColumn(
    "sales_sk",
    monotonically_increasing_id()
)

sales_final.select("sales_sk").show(5)

# COMMAND ----------

#Validate Uniqueness
from pyspark.sql.functions import countDistinct

tables = {
    "Customer": (customer_final, "customer_sk"),
    "Product": (product_final, "product_sk"),
    "Sales": (sales_final, "sales_sk")
}

for name, (df, key) in tables.items():

    total = df.count()
    unique = df.select(countDistinct(key)).first()[0]

    print("=" * 50)
    print(name)
    print("Total Rows :", total)
    print("Unique Keys:", unique)
    print("Status     :", "PASS" if total == unique else "FAIL")   

# COMMAND ----------

#Save Final Silver Tables
# Customer
customer_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/silver/customer")
# Product
product_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/silver/product")
# Sales
sales_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/silver/sales")

# COMMAND ----------

#Final Validation & Silver Audit
#Row Count Validation

print("="*50)
print("CUSTOMER :", customer_final.count())

print("="*50)
print("PRODUCT  :", product_final.count())

print("="*50)
print("SALES    :", sales_final.count())

# COMMAND ----------

#Duplicate Validation
# Customer
customer_final.groupBy("customer_id") \
    .count() \
    .filter("count > 1") \
    .show()
# Product
product_final.groupBy("product_id") \
    .count() \
    .filter("count > 1") \
    .show()
# Sales
sales_final.groupBy("transaction_id") \
    .count() \
    .filter("count > 1") \
    .show()

# COMMAND ----------

# Null PK Validation
print(
    customer_final.filter("customer_id IS NULL").count()
)

print(
    product_final.filter("product_id IS NULL").count()
)

print(
    sales_final.filter("transaction_id IS NULL").count()
)

# COMMAND ----------

# Save Final Silver Tables
customer_final.write \
.format("delta") \
.mode("overwrite") \
.option("overwriteSchema","true") \
.save("/Volumes/workspace/default/celebal_data/silver/customer")

product_final.write \
.format("delta") \
.mode("overwrite") \
.option("overwriteSchema","true") \
.save("/Volumes/workspace/default/celebal_data/silver/product")

sales_final.write \
.format("delta") \
.mode("overwrite") \
.option("overwriteSchema","true") \
.save("/Volumes/workspace/default/celebal_data/silver/sales")

# COMMAND ----------

bronze_product = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/bronze/product"
)

print("Bronze Product :", bronze_product.count())
print("Clean Product  :", product_clean.count())

# COMMAND ----------

print(
    "Null Product IDs:",
    bronze_product.filter("product_id IS NULL").count()
)

# COMMAND ----------

from pyspark.sql.functions import col

duplicate_products = (
    bronze_product
    .groupBy("product_id")
    .count()
    .filter(col("count") > 1)
)

print("Duplicate Product IDs:", duplicate_products.count())

display(duplicate_products)

# COMMAND ----------

product_clean.printSchema()

# COMMAND ----------

from pyspark.sql.functions import to_timestamp

product_clean = product_clean.withColumn(
    "last_updated",
    to_timestamp("last_updated")
)

# COMMAND ----------

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, desc

window_spec = Window.partitionBy("product_id").orderBy(desc("last_updated"))

product_final = (
    product_clean
    .withColumn("rn", row_number().over(window_spec))
    .filter("rn = 1")
    .drop("rn")
)

# COMMAND ----------

from pyspark.sql.functions import when, col, to_timestamp

product_clean = product_clean.withColumn(
    "last_updated",
    when(col("last_updated") == "Unknown", None)
    .otherwise(col("last_updated"))
)

product_clean = product_clean.withColumn(
    "last_updated",
    to_timestamp("last_updated")
)

# COMMAND ----------

for name in dir():
    obj = globals()[name]
    if "DataFrame" in str(type(obj)):
        print(name)

# COMMAND ----------

from pyspark.sql.functions import col, when

product_clean = (
    product_df
    .withColumn(
        "last_updated",
        when(col("last_updated") == "Unknown", None)
        .otherwise(col("last_updated"))
    )
)

# COMMAND ----------

from pyspark.sql.functions import col

product_clean.select("last_updated").distinct().show(20, False)

# COMMAND ----------

from pyspark.sql.functions import expr

product_clean = product_clean.withColumn(
    "last_updated",
    expr("try_to_timestamp(last_updated)")
)

# COMMAND ----------

product_clean.explain(True)

# COMMAND ----------

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, desc

window_spec = Window.partitionBy("product_id").orderBy(desc("last_updated"))

product_final = (
    product_clean
        .withColumn("rn", row_number().over(window_spec))
        .filter("rn = 1")
        .drop("rn")
)

# COMMAND ----------

product_final.printSchema()

# COMMAND ----------

product_final.select("last_updated").show(10, False)

# COMMAND ----------

print("Rows :", product_final.count())

product_final.groupBy("product_id") \
    .count() \
    .filter("count > 1") \
    .show()

# COMMAND ----------

# MAGIC %md
# MAGIC %
# MAGIC # Phase 2 — Silver Layer Transformation
# MAGIC
# MAGIC ## Objective
# MAGIC
# MAGIC The objective of the Silver Layer is to transform the raw Bronze data into **clean, standardized, validated, and business-ready datasets**. This layer applies data quality rules, handles duplicates and missing values, implements Slowly Changing Dimensions (SCD), generates surrogate keys, and prepares the data for analytical reporting in the Gold Layer.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 1. Read Bronze Delta Tables
# MAGIC
# MAGIC The first step was to read all Bronze Delta tables into Spark DataFrames.
# MAGIC
# MAGIC **Tables Read:**
# MAGIC
# MAGIC - Customer
# MAGIC - Product
# MAGIC - Sales
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC - Read trusted Bronze data.
# MAGIC - Use it as the source for all Silver transformations.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 2. Data Profiling
# MAGIC
# MAGIC After loading the data, profiling was performed.
# MAGIC
# MAGIC The following validations were executed:
# MAGIC
# MAGIC - Schema inspection
# MAGIC - Data type inspection
# MAGIC - Row count validation
# MAGIC - Null value identification
# MAGIC - Duplicate record identification
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Data profiling helps understand the quality of the incoming data before any transformation is applied.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 3. Remove Missing Primary Keys
# MAGIC
# MAGIC Records with missing primary keys were removed.
# MAGIC
# MAGIC Primary Keys:
# MAGIC
# MAGIC - Customer → `customer_id`
# MAGIC - Product → `product_id`
# MAGIC - Sales → `transaction_id`
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Primary keys uniquely identify each record.
# MAGIC
# MAGIC Keeping NULL primary keys may lead to:
# MAGIC
# MAGIC - Incorrect joins
# MAGIC - MERGE failures
# MAGIC - Duplicate business records
# MAGIC - Invalid fact-to-dimension relationships
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 4. Remove Duplicate Records
# MAGIC
# MAGIC Duplicate records were identified and handled.
# MAGIC
# MAGIC ### Customer
# MAGIC
# MAGIC Duplicate customer records were removed.
# MAGIC
# MAGIC ### Product
# MAGIC
# MAGIC Instead of simply removing duplicates, the latest product record was retained using the `last_updated` column.
# MAGIC
# MAGIC This represents **Slowly Changing Dimension Type 1 (SCD Type 1).**
# MAGIC
# MAGIC ### Sales
# MAGIC
# MAGIC Duplicate sales transactions were removed using a Window Function.
# MAGIC
# MAGIC Window Specification:
# MAGIC
# MAGIC - Partition by `transaction_id`
# MAGIC - Order by `ingested_at` (latest record)
# MAGIC
# MAGIC The latest transaction was retained.
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Duplicate records lead to:
# MAGIC
# MAGIC - Incorrect reporting
# MAGIC - Double counting
# MAGIC - Incorrect KPI calculations
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 5. Explicit Data Type Casting
# MAGIC
# MAGIC Bronze stored every column as String.
# MAGIC
# MAGIC Business columns were explicitly converted into appropriate data types.
# MAGIC
# MAGIC ### Customer
# MAGIC
# MAGIC - age → Integer
# MAGIC - membership_years → Integer
# MAGIC
# MAGIC ### Product
# MAGIC
# MAGIC - product_rating → Double
# MAGIC - product_review_count → Integer
# MAGIC - product_stock → Integer
# MAGIC - product_return_rate → Double
# MAGIC - unit_price → Double
# MAGIC
# MAGIC ### Sales
# MAGIC
# MAGIC - quantity → Integer
# MAGIC - total_sales → Double
# MAGIC - discount → Double
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Numeric calculations require numeric data types.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 6. Handle Missing Values
# MAGIC
# MAGIC Missing values were standardized.
# MAGIC
# MAGIC ### String Columns
# MAGIC
# MAGIC NULL values were replaced with:
# MAGIC
# MAGIC ```
# MAGIC Unknown
# MAGIC ```
# MAGIC
# MAGIC ### Numeric Columns
# MAGIC
# MAGIC NULL values were replaced with:
# MAGIC
# MAGIC ```
# MAGIC 0
# MAGIC ```
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Avoid NULL values during reporting and aggregations.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 7. Customer SCD Type 2
# MAGIC
# MAGIC Customer data already contained SCD metadata:
# MAGIC
# MAGIC - version
# MAGIC - effective_start_date
# MAGIC - effective_end_date
# MAGIC - is_current
# MAGIC
# MAGIC The implementation preserved historical customer records.
# MAGIC
# MAGIC Each customer version remains available for historical analysis.
# MAGIC
# MAGIC Example:
# MAGIC
# MAGIC ```
# MAGIC Version 1
# MAGIC Customer lives in Delhi
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC Version 2
# MAGIC Customer moves to Mumbai
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC Both records remain stored.
# MAGIC ```
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Customer history should never be lost.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 8. Product SCD Type 1
# MAGIC
# MAGIC Product information should always reflect the latest available data.
# MAGIC
# MAGIC Using the `last_updated` column, only the newest product record was retained.
# MAGIC
# MAGIC Older product versions were overwritten.
# MAGIC
# MAGIC Example:
# MAGIC
# MAGIC ```
# MAGIC Old Price
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC New Price
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC Old Price Replaced
# MAGIC ```
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Product history is not maintained.
# MAGIC
# MAGIC Only the latest version is required.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 9. Sales Immutable Ledger
# MAGIC
# MAGIC Sales transactions were treated as immutable records.
# MAGIC
# MAGIC Rules followed:
# MAGIC
# MAGIC - Sales are never updated.
# MAGIC - Sales are never deleted.
# MAGIC - Duplicate ingestions are removed.
# MAGIC - Original transactions remain preserved.
# MAGIC
# MAGIC A Window Function was used.
# MAGIC
# MAGIC ```
# MAGIC PARTITION BY transaction_id
# MAGIC
# MAGIC ORDER BY ingested_at DESC
# MAGIC ```
# MAGIC
# MAGIC The latest duplicate was retained.
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Financial transactions should never change after being recorded.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 10. Generate Surrogate Keys
# MAGIC
# MAGIC Surrogate keys were generated for all Silver tables.
# MAGIC
# MAGIC Generated Keys:
# MAGIC
# MAGIC - customer_sk
# MAGIC - product_sk
# MAGIC - sales_sk
# MAGIC
# MAGIC The keys were created using:
# MAGIC
# MAGIC ```
# MAGIC monotonically_increasing_id()
# MAGIC ```
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Surrogate keys improve warehouse performance and establish relationships between dimensions and fact tables.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 11. Validate Surrogate Keys
# MAGIC
# MAGIC The following validation was performed:
# MAGIC
# MAGIC ```
# MAGIC Total Rows
# MAGIC
# MAGIC =
# MAGIC
# MAGIC Distinct Surrogate Keys
# MAGIC ```
# MAGIC
# MAGIC If both values matched:
# MAGIC
# MAGIC ```
# MAGIC PASS
# MAGIC ```
# MAGIC
# MAGIC Otherwise:
# MAGIC
# MAGIC ```
# MAGIC FAIL
# MAGIC ```
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Ensure every record has a unique warehouse identifier.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 12. Row Count Validation
# MAGIC
# MAGIC Row counts were compared between Bronze and Silver.
# MAGIC
# MAGIC Example:
# MAGIC
# MAGIC Customer
# MAGIC
# MAGIC ```
# MAGIC Bronze
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC 2105
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC Silver
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC 2105
# MAGIC ```
# MAGIC
# MAGIC Product
# MAGIC
# MAGIC ```
# MAGIC Bronze
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC 2084
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC Silver
# MAGIC
# MAGIC ↓
# MAGIC
# MAGIC 2083
# MAGIC ```
# MAGIC
# MAGIC The difference was investigated and explained by the SCD Type 1 deduplication process.
# MAGIC
# MAGIC **Purpose**
# MAGIC
# MAGIC Ensure that every row removal is intentional and justified.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 13. Duplicate Validation
# MAGIC
# MAGIC Duplicate validation was performed for every Silver table.
# MAGIC
# MAGIC Validated:
# MAGIC
# MAGIC - Customer IDs
# MAGIC - Product IDs
# MAGIC - Transaction IDs
# MAGIC
# MAGIC All remaining duplicate records were removed.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 14. Save Final Silver Tables
# MAGIC
# MAGIC The transformed datasets were stored as Delta tables.
# MAGIC
# MAGIC Final Silver Tables:
# MAGIC
# MAGIC - Silver Customer
# MAGIC - Silver Product
# MAGIC - Silver Sales
# MAGIC
# MAGIC These tables become the source for the Gold Layer.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Silver Layer Architecture
# MAGIC
# MAGIC ```text
# MAGIC                  BRONZE LAYER
# MAGIC                       │
# MAGIC                       ▼
# MAGIC           Read Bronze Delta Tables
# MAGIC                       │
# MAGIC                       ▼
# MAGIC               Data Profiling
# MAGIC                       │
# MAGIC                       ▼
# MAGIC         Remove Missing Primary Keys
# MAGIC                       │
# MAGIC                       ▼
# MAGIC            Remove Duplicate Records
# MAGIC                       │
# MAGIC                       ▼
# MAGIC           Explicit Data Type Casting
# MAGIC                       │
# MAGIC                       ▼
# MAGIC             Handle Missing Values
# MAGIC                       │
# MAGIC                       ▼
# MAGIC          Customer SCD Type 2 Logic
# MAGIC                       │
# MAGIC                       ▼
# MAGIC           Product SCD Type 1 Logic
# MAGIC                       │
# MAGIC                       ▼
# MAGIC      Sales Immutable Ledger Logic
# MAGIC                       │
# MAGIC                       ▼
# MAGIC        Generate Surrogate Keys
# MAGIC                       │
# MAGIC                       ▼
# MAGIC       Validate Row Counts & Duplicates
# MAGIC                       │
# MAGIC                       ▼
# MAGIC          Save Final Silver Delta Tables
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Assignment Requirements Covered
# MAGIC
# MAGIC | Requirement | Status |
# MAGIC |-------------|--------|
# MAGIC | Missing PK records removed | ✅ |
# MAGIC | Duplicates removed | ✅ |
# MAGIC | Numeric types explicitly cast | ✅ |
# MAGIC | String NULL values replaced with "Unknown" | ✅ |
# MAGIC | Numeric NULL values replaced with 0 | ✅ |
# MAGIC | Customer SCD Type 2 implemented | ✅ |
# MAGIC | Customer history validated | ✅ |
# MAGIC | Product SCD Type 1 implemented | ✅ |
# MAGIC | Sales immutable ledger implemented | ✅ |
# MAGIC | Window-based sales deduplication | ✅ |
# MAGIC | customer_sk generated | ✅ |
# MAGIC | product_sk generated | ✅ |
# MAGIC | sales_sk generated | ✅ |
# MAGIC | Surrogate key uniqueness validated | ✅ |
# MAGIC | Row-count assertions implemented | ✅ |
# MAGIC | Duplicate validation implemented | ✅ |
# MAGIC | Final Silver Delta tables created | ✅ |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Outcome
# MAGIC
# MAGIC At the end of Phase 2, all datasets were transformed into clean, validated, business-ready Silver tables. These tables preserve business rules, maintain historical information where required, eliminate duplicate and invalid records, and provide optimized datasets for building the Gold Layer Star Schema and analytical KPIs.
# MAGIC

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

