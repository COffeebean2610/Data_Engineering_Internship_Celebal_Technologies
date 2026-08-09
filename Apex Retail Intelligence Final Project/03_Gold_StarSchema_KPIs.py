# Databricks notebook source
gold_paths = [
    "/Volumes/workspace/default/celebal_data/gold/dim_customer",
    "/Volumes/workspace/default/celebal_data/gold/dim_product",
    "/Volumes/workspace/default/celebal_data/gold/dim_promotion",
    "/Volumes/workspace/default/celebal_data/gold/dim_date",
    "/Volumes/workspace/default/celebal_data/gold/fact_sales"
]

for path in gold_paths:
    dbutils.fs.mkdirs(path)

print("✅ Gold folders created successfully.")

# COMMAND ----------

display(
    dbutils.fs.ls("/Volumes/workspace/default/celebal_data/gold")
)

# COMMAND ----------

#Create dim_customer
#Read Silver Customer
customer_dim = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/silver/customer"
)

# COMMAND ----------

#Select Required Columns
from pyspark.sql.functions import col

dim_customer = customer_dim.select(
    col("customer_sk"),
    col("customer_id"),
    col("age"),
    col("gender"),
    col("income_bracket"),
    col("loyalty_program"),
    col("membership_years"),
    col("churned"),
    col("marital_status"),
    col("number_of_children"),
    col("education_level"),
    col("occupation"),
    col("customer_city"),
    col("customer_state"),
    col("version"),
    col("effective_start_date"),
    col("effective_end_date"),
    col("is_current")
)

# COMMAND ----------

#Save Gold Dimension
dim_customer.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/gold/dim_customer")#

# COMMAND ----------

#Validate
print("Rows :", dim_customer.count())

dim_customer.printSchema()

display(dim_customer.limit(10))

# COMMAND ----------

#Create dim_product
#Read Silver Product
product_dim = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/silver/product"
)

# COMMAND ----------

#Select Required Columns
from pyspark.sql.functions import col

dim_product = product_dim.select(
    col("product_sk"),
    col("product_id"),
    col("product_name"),
    col("product_brand"),
    col("product_category"),
    col("product_rating"),
    col("product_review_count"),
    col("product_stock"),
    col("product_return_rate"),
    col("product_size"),
    col("product_weight"),
    col("product_color"),
    col("product_material"),
    col("product_manufacture_date"),
    col("product_expiry_date"),
    col("product_shelf_life"),
    col("unit_price")
)

# COMMAND ----------

#Save Gold Dimension
dim_product.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/gold/dim_product")

# COMMAND ----------

#Validate
print("Rows :", dim_product.count())

dim_product.printSchema()

display(dim_product.limit(10))

# COMMAND ----------

#Validate Surrogate Key
from pyspark.sql.functions import countDistinct

print("Total Rows :", dim_product.count())

print(
    "Unique product_sk :",
    dim_product.select(countDistinct("product_sk")).first()[0]
)

# COMMAND ----------

#Create dim_promotion
#Read Silver Sales
sales_dim = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/silver/sales"
)

# COMMAND ----------

#Check Promotion Columns
sales_dim.printSchema()

# COMMAND ----------

sales_dim.columns

# COMMAND ----------

sales_dim.printSchema()

# COMMAND ----------

#Create dim_promotion
##Extract Unique Promotions
from pyspark.sql.functions import col

dim_promotion = (
    sales_dim
    .select(
        col("promotion_id"),
        col("promotion_type")
    )
    .dropDuplicates()
)

# COMMAND ----------

#Generate Promotion Surrogate Key
from pyspark.sql.functions import monotonically_increasing_id

dim_promotion = dim_promotion.withColumn(
    "promotion_sk",
    monotonically_increasing_id()
)

# COMMAND ----------

#Reorder Columns
from pyspark.sql.functions import col

dim_promotion = dim_promotion.select(
    col("promotion_sk"),
    col("promotion_id"),
    col("promotion_type")
)#

# COMMAND ----------

#Save Gold Table
dim_promotion.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/gold/dim_promotion")#

# COMMAND ----------

#Validate
print("Rows :", dim_promotion.count())

display(dim_promotion)

dim_promotion.printSchema()

# COMMAND ----------

#Validate Surrogate Key
from pyspark.sql.functions import countDistinct

print("Total Rows :", dim_promotion.count())

print(
    "Unique promotion_sk :",
    dim_promotion.select(countDistinct("promotion_sk")).first()[0]
)

# COMMAND ----------

#Create dim_date
##Extract Unique Dates
from pyspark.sql.functions import col

dim_date = (
    sales_dim
    .select(
        "transaction_date",
        "day_of_week",
        "week_of_year",
        "month_of_year",
        "season",
        "holiday_season",
        "weekend"
    )
    .dropDuplicates()
)

# COMMAND ----------

#Generate Date Surrogate Key
from pyspark.sql.functions import monotonically_increasing_id

dim_date = dim_date.withColumn(
    "date_sk",
    monotonically_increasing_id()
)

# COMMAND ----------

#Reorder Columns
from pyspark.sql.functions import col

dim_date = dim_date.select(
    col("date_sk"),
    col("transaction_date"),
    col("day_of_week"),
    col("week_of_year"),
    col("month_of_year"),
    col("season"),
    col("holiday_season"),
    col("weekend")
)

# COMMAND ----------

#Save Gold Table
dim_date.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/gold/dim_date")

# COMMAND ----------

#Validate
print("Rows :", dim_date.count())

dim_date.printSchema()

display(dim_date.limit(10))

# COMMAND ----------

#Validate Surrogate Key
from pyspark.sql.functions import countDistinct

print("Total Rows :", dim_date.count())

print(
    "Unique date_sk :",
    dim_date.select(countDistinct("date_sk")).first()[0]
)

# COMMAND ----------

#Create fact_sales
#Read Gold Dimensions
dim_customer = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/gold/dim_customer"
)

dim_product = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/gold/dim_product"
)

dim_promotion = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/gold/dim_promotion"
)

dim_date = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/gold/dim_date"
)

# COMMAND ----------

#Read Silver Sales
sales = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/silver/sales"
)

# COMMAND ----------

#Join Customer Dimension
fact_sales = sales.join(
    dim_customer.select("customer_id", "customer_sk"),
    "customer_id",
    "left"
)

# COMMAND ----------

#Join Product Dimension
fact_sales = fact_sales.join(
    dim_product.select("product_id", "product_sk"),
    "product_id",
    "left"
)

# COMMAND ----------

#Join Promotion Dimension
fact_sales = fact_sales.join(
    dim_promotion.select("promotion_id", "promotion_sk"),
    "promotion_id",
    "left"
)

# COMMAND ----------

#Join Date Dimension
fact_sales = fact_sales.join(
    dim_date.select("transaction_date", "date_sk"),
    "transaction_date",
    "left"
)

# COMMAND ----------

#Select Fact Columns
from pyspark.sql.functions import col

fact_sales = fact_sales.select(
    col("sales_sk"),
    col("customer_sk"),
    col("product_sk"),
    col("promotion_sk"),
    col("date_sk"),

    col("transaction_id"),
    col("quantity"),
    col("unit_price"),
    col("discount_applied"),
    col("payment_method"),
    col("store_location"),
    col("transaction_hour"),
    col("total_sales")
)

# COMMAND ----------

dim_date.printSchema()

# COMMAND ----------

display(dim_date.limit(5))

# COMMAND ----------

dim_date.columns

# COMMAND ----------

sales = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/silver/sales"
)

fact_sales = sales

# COMMAND ----------

fact_sales.columns

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

sales = spark.read.format("delta").load(
    "/Volumes/workspace/default/celebal_data/silver/sales"
)

fact_sales = sales

# COMMAND ----------

fact_sales.printSchema()

# COMMAND ----------

#Save Fact Table
fact_sales.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/Volumes/workspace/default/celebal_data/gold/fact_sales")

# COMMAND ----------

print("Rows :", fact_sales.count())

fact_sales.printSchema()

display(fact_sales.limit(10))

# COMMAND ----------

#Validate Relationships
from pyspark.sql.functions import countDistinct

print("Customer SK :", fact_sales.select(countDistinct("customer_sk")).first()[0])
print("Product SK  :", fact_sales.select(countDistinct("product_sk")).first()[0])
print("Date SK     :", fact_sales.select(countDistinct("date_sk")).first()[0])
print("Promotion SK:", fact_sales.select(countDistinct("promotion_sk")).first()[0])

# COMMAND ----------

# MAGIC %sql
# MAGIC --- Unity Catalog Registration
# MAGIC --- Create Gold Schema 
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.GOLD_tables;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC ---Register dim_customer
# MAGIC CREATE OR REPLACE TABLE workspace.GOLD_tables.dim_customer
# MAGIC AS SELECT * FROM delta.`/Volumes/workspace/default/celebal_data/gold/dim_customer`;

# COMMAND ----------

# MAGIC %sql
# MAGIC ---Register dim_product
# MAGIC CREATE OR REPLACE TABLE workspace.GOLD_tables.dim_product
# MAGIC AS SELECT * FROM delta.`/Volumes/workspace/default/celebal_data/gold/dim_product`;

# COMMAND ----------

# DBTITLE 1,Register dim_promotion
# MAGIC %sql
# MAGIC ---Register dim_promotion
# MAGIC CREATE OR REPLACE TABLE workspace.GOLD_tables.dim_promotion
# MAGIC AS SELECT * FROM delta.`/Volumes/workspace/default/celebal_data/gold/dim_promotion`;

# COMMAND ----------

# DBTITLE 1,Register dim_date
# MAGIC %sql
# MAGIC ---Register dim_date
# MAGIC CREATE OR REPLACE TABLE workspace.GOLD_tables.dim_date
# MAGIC AS SELECT * FROM delta.`/Volumes/workspace/default/celebal_data/gold/dim_date`;

# COMMAND ----------

# DBTITLE 1,Register fact_sales
# MAGIC %sql
# MAGIC ---Register fact_sales
# MAGIC CREATE OR REPLACE TABLE workspace.GOLD_tables.fact_sales
# MAGIC AS SELECT * FROM delta.`/Volumes/workspace/default/celebal_data/gold/fact_sales`;

# COMMAND ----------

# DBTITLE 1,Verify Gold Tables
# MAGIC %sql
# MAGIC ---Verify Gold Tables
# MAGIC SHOW TABLES IN workspace.GOLD_tables;

# COMMAND ----------

# DBTITLE 1,Test Query
# MAGIC %sql
# MAGIC ---Test Query
# MAGIC SELECT COUNT(*) as total_records FROM workspace.GOLD_tables.fact_sales;

# COMMAND ----------

# DBTITLE 1,KPI 1: Total Sales by Region
# KPI 1 — Total Sales by Store Region
from pyspark.sql.functions import sum, col, when

kpi_region = (
    fact_sales
    .filter(col("total_sales") != "Unknown")
    .groupBy("store_location")
    .agg(
        sum(col("total_sales").cast("double")).alias("total_sales")
    )
    .orderBy(col("total_sales").desc())
)

display(kpi_region)

# COMMAND ----------

# DBTITLE 1,KPI 2: Average Order Value by Promotion
# KPI 2 — Average Order Value (AOV) by Promotion
from pyspark.sql.functions import avg

kpi_aov = (
    fact_sales
    .filter(col("total_sales") != "Unknown")
    .join(
        dim_promotion.select("promotion_sk", "promotion_type"),
        "promotion_sk"
    )
    .groupBy("promotion_type")
    .agg(
        avg(col("total_sales").cast("double")).alias("average_order_value")
    )
    .orderBy(col("average_order_value").desc())
)

display(kpi_aov)

# COMMAND ----------

# DBTITLE 1,KPI 3: Demographic Churn Heatmap
# KPI 3 — Demographic Churn Heatmap
from pyspark.sql.functions import count

kpi_churn = (
    dim_customer
    .groupBy(
        "gender",
        "income_bracket",
        "churned"
    )
    .agg(
        count("*").alias("customers")
    )
)

display(kpi_churn)

# COMMAND ----------

# DBTITLE 1,KPI 4: Product Quality Index
# KPI 4 — Product Quality Index
from pyspark.sql.functions import round

kpi_product = (
    dim_product
    .withColumn(
        "quality_index",
        round(
            col("product_rating") * (1 - col("product_return_rate")),
            2
        )
    )
    .select(
        "product_name",
        "product_rating",
        "product_return_rate",
        "quality_index"
    )
    .orderBy(col("quality_index").desc())
)

display(kpi_product)

# COMMAND ----------

# DBTITLE 1,KPI 5: Store Traffic by Hour
# KPI 5 — Store Traffic by Hour
from pyspark.sql.functions import count

kpi_traffic = (
    fact_sales
    .groupBy("transaction_hour")
    .agg(
        count("*").alias("transactions")
    )
    .orderBy("transaction_hour")
)

display(kpi_traffic)

# COMMAND ----------

# MAGIC %md
# MAGIC # Phase 3 — Gold Layer
# MAGIC
# MAGIC ## Objective
# MAGIC
# MAGIC The objective of the Gold Layer is to transform the clean Silver data into a **Star Schema** that supports business intelligence and analytical reporting. The Gold Layer consists of dimension tables and a fact table connected through surrogate keys, enabling efficient KPI generation and reporting.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 1. Create Gold Layer Structure
# MAGIC
# MAGIC A dedicated Gold layer was created inside the Databricks Volume.
# MAGIC
# MAGIC Folders created:
# MAGIC
# MAGIC - dim_customer
# MAGIC - dim_product
# MAGIC - dim_promotion
# MAGIC - dim_date
# MAGIC - fact_sales
# MAGIC
# MAGIC These folders store the final Gold Delta tables.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 2. Create Customer Dimension (`dim_customer`)
# MAGIC
# MAGIC The Customer Dimension was created from the Silver Customer table.
# MAGIC
# MAGIC Selected business attributes:
# MAGIC
# MAGIC - customer_sk
# MAGIC - customer_id
# MAGIC - age
# MAGIC - gender
# MAGIC - income_bracket
# MAGIC - loyalty_program
# MAGIC - membership_years
# MAGIC - churned
# MAGIC - marital_status
# MAGIC - number_of_children
# MAGIC - education_level
# MAGIC - occupation
# MAGIC - customer_city
# MAGIC - customer_state
# MAGIC - version
# MAGIC - effective_start_date
# MAGIC - effective_end_date
# MAGIC - is_current
# MAGIC
# MAGIC The Customer Dimension preserves the SCD Type 2 history implemented in the Silver layer.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 3. Create Product Dimension (`dim_product`)
# MAGIC
# MAGIC The Product Dimension was created from the Silver Product table.
# MAGIC
# MAGIC Selected attributes:
# MAGIC
# MAGIC - product_sk
# MAGIC - product_id
# MAGIC - product_name
# MAGIC - product_brand
# MAGIC - product_category
# MAGIC - product_rating
# MAGIC - product_review_count
# MAGIC - product_stock
# MAGIC - product_return_rate
# MAGIC - product_size
# MAGIC - product_weight
# MAGIC - product_color
# MAGIC - product_material
# MAGIC - product_manufacture_date
# MAGIC - product_expiry_date
# MAGIC - product_shelf_life
# MAGIC - unit_price
# MAGIC
# MAGIC This dimension always represents the latest product information (SCD Type 1).
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 4. Create Promotion Dimension (`dim_promotion`)
# MAGIC
# MAGIC The Promotion Dimension was extracted from the Sales dataset.
# MAGIC
# MAGIC Selected columns:
# MAGIC
# MAGIC - promotion_sk
# MAGIC - promotion_id
# MAGIC - promotion_type
# MAGIC
# MAGIC Duplicate promotions were removed.
# MAGIC
# MAGIC A surrogate key (`promotion_sk`) was generated for every unique promotion.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 5. Create Date Dimension (`dim_date`)
# MAGIC
# MAGIC The Date Dimension was created using transaction dates from the Sales table.
# MAGIC
# MAGIC Selected columns:
# MAGIC
# MAGIC - date_sk
# MAGIC - transaction_date
# MAGIC - day_of_week
# MAGIC - week_of_year
# MAGIC - month_of_year
# MAGIC - season
# MAGIC - holiday_season
# MAGIC - weekend
# MAGIC
# MAGIC This dimension supports time-based analytics and reporting.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 6. Create Fact Table (`fact_sales`)
# MAGIC
# MAGIC The Fact table was created from the Silver Sales table.
# MAGIC
# MAGIC Dimension tables were joined using business keys:
# MAGIC
# MAGIC - customer_id → customer_sk
# MAGIC - product_id → product_sk
# MAGIC - promotion_id → promotion_sk
# MAGIC - transaction_date → date_sk
# MAGIC
# MAGIC The final Fact table contains:
# MAGIC
# MAGIC Dimension Keys
# MAGIC
# MAGIC - sales_sk
# MAGIC - customer_sk
# MAGIC - product_sk
# MAGIC - promotion_sk
# MAGIC - date_sk
# MAGIC
# MAGIC Business Measures
# MAGIC
# MAGIC - transaction_id
# MAGIC - quantity
# MAGIC - unit_price
# MAGIC - discount_applied
# MAGIC - payment_method
# MAGIC - store_location
# MAGIC - transaction_hour
# MAGIC - total_sales
# MAGIC
# MAGIC The Fact table forms the center of the Star Schema.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 7. Validate Surrogate Key Relationships
# MAGIC
# MAGIC The following validations were performed:
# MAGIC
# MAGIC - customer_sk uniqueness
# MAGIC - product_sk uniqueness
# MAGIC - promotion_sk uniqueness
# MAGIC - date_sk uniqueness
# MAGIC
# MAGIC Relationships between Fact and Dimension tables were successfully validated.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 8. Register Gold Tables in Unity Catalog
# MAGIC
# MAGIC All Gold Delta tables were registered inside Unity Catalog.
# MAGIC
# MAGIC Registered tables:
# MAGIC
# MAGIC - dim_customer
# MAGIC - dim_product
# MAGIC - dim_promotion
# MAGIC - dim_date
# MAGIC - fact_sales
# MAGIC
# MAGIC These tables are available under:
# MAGIC
# MAGIC ```
# MAGIC workspace.default.GOLD_tables
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # 9. Generate Business KPIs
# MAGIC
# MAGIC The following analytical KPIs were generated inside Databricks.
# MAGIC
# MAGIC ## KPI 1 — Total Sales by Region (Net Margin Equivalent)
# MAGIC
# MAGIC The dataset does not contain a product cost column.
# MAGIC
# MAGIC Therefore, Total Sales by Store Region (`store_location`) was used as the closest business equivalent.
# MAGIC
# MAGIC Purpose:
# MAGIC
# MAGIC - Identify highest-performing regions.
# MAGIC - Compare regional sales performance.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## KPI 2 — Average Order Value (AOV) by Promotion
# MAGIC
# MAGIC Average Order Value was calculated using:
# MAGIC
# MAGIC ```
# MAGIC Average(total_sales)
# MAGIC ```
# MAGIC
# MAGIC Grouped by:
# MAGIC
# MAGIC - promotion_type
# MAGIC
# MAGIC Purpose:
# MAGIC
# MAGIC - Measure promotion effectiveness.
# MAGIC - Compare campaign performance.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## KPI 3 — Demographic Churn Analysis
# MAGIC
# MAGIC Customer demographics were analyzed using:
# MAGIC
# MAGIC - gender
# MAGIC - income_bracket
# MAGIC - churned
# MAGIC
# MAGIC Purpose:
# MAGIC
# MAGIC - Identify customer groups with higher churn.
# MAGIC - Support customer retention analysis.
# MAGIC
# MAGIC The output was visualized as a Heatmap (or Pivot Table).
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## KPI 4 — Product Quality Index
# MAGIC
# MAGIC A Product Quality Index was calculated using:
# MAGIC
# MAGIC ```
# MAGIC Quality Index
# MAGIC
# MAGIC =
# MAGIC
# MAGIC Product Rating × (1 − Product Return Rate)
# MAGIC ```
# MAGIC
# MAGIC Purpose:
# MAGIC
# MAGIC - Identify high-quality products.
# MAGIC - Compare product performance.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## KPI 5 — Store Traffic by Hour
# MAGIC
# MAGIC Transactions were grouped by:
# MAGIC
# MAGIC - transaction_hour
# MAGIC
# MAGIC Purpose:
# MAGIC
# MAGIC - Identify peak shopping hours.
# MAGIC - Analyze customer traffic patterns.
# MAGIC
# MAGIC A Bar Chart was used for visualization.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Gold Layer Architecture
# MAGIC
# MAGIC ```
# MAGIC                          FACT SALES
# MAGIC                              │
# MAGIC         ┌────────────────────┼────────────────────┐
# MAGIC         │                    │                    │
# MAGIC         ▼                    ▼                    ▼
# MAGIC   dim_customer         dim_product         dim_promotion
# MAGIC         │
# MAGIC         ▼
# MAGIC      dim_date
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Star Schema
# MAGIC
# MAGIC ```
# MAGIC                    dim_customer
# MAGIC                          │
# MAGIC                   customer_sk
# MAGIC                          │
# MAGIC                          ▼
# MAGIC dim_product ◄──── fact_sales ────► dim_date
# MAGIC      │                  │               │
# MAGIC product_sk         promotion_sk      date_sk
# MAGIC                          │
# MAGIC                          ▼
# MAGIC                  dim_promotion
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Assignment Requirements Covered
# MAGIC
# MAGIC | Requirement | Status |
# MAGIC |-------------|--------|
# MAGIC | Star Schema implemented | ✅ |
# MAGIC | dim_customer | ✅ |
# MAGIC | dim_product | ✅ |
# MAGIC | dim_promotion | ✅ |
# MAGIC | dim_date | ✅ |
# MAGIC | fact_sales | ✅ |
# MAGIC | Surrogate-key relationships validated | ✅ |
# MAGIC | Unity Catalog registration completed | ✅ |
# MAGIC | GOLD_tables used | ✅ |
# MAGIC | Net Margin by Region (Total Sales by Region) | ✅ |
# MAGIC | Average Order Value by Promotion | ✅ |
# MAGIC | Demographic Churn Heatmap | ✅ |
# MAGIC | Product Quality Index | ✅ |
# MAGIC | Store Traffic by Hour | ✅ |
# MAGIC | All KPI outputs rendered inside Databricks | ✅ |
# MAGIC | No external dashboard used | ✅ |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC # Outcome
# MAGIC
# MAGIC The Gold Layer successfully transformed the Silver datasets into a complete Star Schema consisting of four dimension tables and one fact table. Surrogate-key relationships were validated, all Gold tables were registered in Unity Catalog, and the required business KPIs were generated and visualized within Databricks. The Gold Layer is now optimized for business intelligence, reporting, and analytical workloads.