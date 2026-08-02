# Assignment Summary

## Objective
Demonstrate incremental processing with a Delta Lake MERGE using Apache Spark.

## Dataset
- `Sample - Superstore.csv`: initial Superstore dataset
- `superstore_incremental.csv`: simulated new records and updates

## Cleaning
- Converted source column names to Delta-compatible names
- Renamed key fields for readability
- Removed duplicate records and filled missing city/state values

## MERGE
- Updated existing records where the ID already existed
- Inserted records where the ID was not present
- Used SCD Type 1-style behaviour: matched records are overwritten with the
  latest values, without retaining historical versions

## Validation
- Displayed the final Delta table after the MERGE
- Validated the final row count and duplicate-ID count

## Conclusion
The MERGE operation successfully updated existing records and inserted new ones
into the Delta table.
