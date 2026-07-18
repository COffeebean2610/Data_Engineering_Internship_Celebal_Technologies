# Celebal Week 5 - Apache Spark (PySpark) Data Cleaning & Aggregation

## Objective
Learn Spark fundamentals and perform data cleaning, transformation, and aggregation using **DataFrames**.

## Folder Structure
```
week5-spark-assignment/
│── data/
│   └── customers.csv
│── notebook/
│   └── spark_basics.ipynb
│── output/
│   ├── cleaned_data.csv
│   └── grouped_results.csv
└── README.md
```

> Note: Your provided dataset is located in the top-level `Employee` folder. The notebook automatically reads it from there.

## What the notebook does
1. Starts a Spark session
2. Loads the Kaggle Employee dataset (CSV)
3. Removes duplicates (`dropDuplicates()`)
4. Handles nulls using `fillna()`
5. Cleans schema (casts numeric fields where needed)
6. Filters data using conditions
7. Renames columns (if required)
8. Performs aggregations (`count`, `avg`, `min`, `max`, `sum`)
9. Groups data with `groupBy()` and aggregates
10. Saves outputs as CSV into `output/`

## How to run
1. Open `notebook/spark_basics.ipynb`
2. Run all cells in order
3. Check generated CSV files under `output/`

## Outputs
- `output/cleaned_data.csv`
- `output/grouped_results.csv`

## Short Spark Insights (include in your submission)
- **Why Spark is faster than MapReduce**: Spark keeps intermediate results **in memory** and uses a more efficient execution engine (DAG), reducing disk I/O.
- **DataFrames & immutability**: Transformations return new DataFrames; they do not modify the original.
- **Wide transformations / shuffle**: `groupBy()` and `join()` require data movement across partitions (shuffle), which is slower than narrow transformations.

