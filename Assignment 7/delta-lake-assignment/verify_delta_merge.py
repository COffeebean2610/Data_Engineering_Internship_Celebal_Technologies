from pathlib import Path
from pyspark.sql import SparkSession
from delta import *
from delta.tables import DeltaTable

project_root = Path.cwd()
data_dir = project_root / 'data'
master_csv = data_dir / 'customer_master.csv'
incremental_csv = data_dir / 'customer_incremental.csv'
delta_table_path = project_root / 'delta_tables' / 'customer_master'

delta_jar = project_root / 'delta-spark_2.12-3.2.0.jar'
delta_storage_jar = project_root / 'delta-storage-3.2.0.jar'

spark = (
    SparkSession.builder
    .appName('delta-scd-assignment')
    .config('spark.jars', f'{delta_jar},{delta_storage_jar}')
    .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension')
    .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog')
    .master('local[*]')
    .getOrCreate()
)
spark.sparkContext.setLogLevel('ERROR')

master_df = spark.read.option('header', True).option('inferSchema', True).csv(str(master_csv))
cleaned_df = master_df.dropDuplicates(['ID', 'Name', 'City']).na.fill({'City': 'Mumbai'})
cleaned_df.write.format('delta').mode('overwrite').save(str(delta_table_path))

incremental_df = spark.read.option('header', True).option('inferSchema', True).csv(str(incremental_csv))

delta_table = DeltaTable.forPath(spark, str(delta_table_path))
(
    delta_table.alias('target')
    .merge(incremental_df.alias('source'), 'target.ID = source.ID')
    .whenMatchedUpdate(set={'Name': 'source.Name', 'City': 'source.City'})
    .whenNotMatchedInsert(values={'ID': 'source.ID', 'Name': 'source.Name', 'City': 'source.City'})
    .execute()
)

final_df = spark.read.format('delta').load(str(delta_table_path))
final_df.orderBy('ID').show(truncate=False)
print('row_count=', final_df.count())
print('duplicate_ids=', final_df.groupBy('ID').count().filter('count > 1').count())
spark.stop()
