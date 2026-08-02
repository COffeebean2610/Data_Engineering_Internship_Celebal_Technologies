# Delta Lake MERGE Assignment

This project demonstrates a Delta Lake MERGE operation using Apache Spark.

## Steps performed
- Loaded the Superstore master data from CSV
- Cleaned duplicate and null values
- Wrote the cleaned data as a Delta table
- Loaded an incremental dataset
- Applied MERGE to update existing rows and insert new rows
- Validated the final row count and duplicate IDs

## Folder structure
- data/: CSV input files
- notebooks/: Jupyter notebook with the full workflow
- screenshots/: screenshots for each major step
- report/: project summary file

## Screenshot checklist

- `screenshots/data_loading/`: source and incremental CSV previews
- `screenshots/data_cleaning/`: renamed columns, null handling, and duplicate removal
- `screenshots/scd1/`: initial cleaned Delta-table write
- `screenshots/scd2/merge_completed.png`: Delta MERGE completion output
- `screenshots/validation/`: row count and duplicate-ID validation
- `screenshots/final_output/`: final Delta table preview

The notebook demonstrates an SCD Type 1-style MERGE: existing customer IDs
are updated, while new customer IDs are inserted.

## Run the validation script

Prerequisites: Python with a virtual environment, Java 17, and the included
Delta Lake JAR files.

From this directory in PowerShell:

```powershell
..\venv\Scripts\python.exe -m pip install -r requirements.txt
..\venv\Scripts\python.exe verify_delta_merge.py
```

Expected validation result:

```text
row_count= 4
duplicate_ids= 0
```
