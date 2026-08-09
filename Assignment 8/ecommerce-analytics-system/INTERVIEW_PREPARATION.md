# Interview Preparation

1. **Why use SQLite for this project?**  
   SQLite is lightweight, serverless, portable, and supports the relational constraints and analytical SQL needed for a local project.

2. **How does pandas support the pipeline?**  
   It loads CSV files, standardizes fields, validates values, handles missing data, and exports cleaned and report datasets.

3. **How is referential integrity enforced?**  
   SQLite foreign keys link orders to customers and order items to orders and products. The connection enables `PRAGMA foreign_keys = ON`.

4. **Why use parameterized SQL in the CLI?**  
   Parameters safely pass date filters to SQLite and avoid SQL injection caused by string-built values.

5. **What is the difference between `RANK`, `DENSE_RANK`, and `ROW_NUMBER`?**  
   `RANK` leaves gaps after ties, `DENSE_RANK` does not leave gaps, and `ROW_NUMBER` assigns a unique sequence to every row.

6. **What problem do CTEs solve?**  
   CTEs name intermediate result sets, making multi-step business logic easier to read, validate, and reuse within one query.

7. **What is cohort analysis in this project?**  
   Customers are grouped by their first purchase month, then measured for repeat activity in Month 0 through Month 3 to calculate retention.

8. **What does RFM analysis measure?**  
   Recency is time since the latest order, Frequency is order count, and Monetary is total spend. Together they support customer prioritization.

9. **How does the CLI handle invalid input?**  
   `argparse` validates report names, ISO date parsing validates dates, and the tool rejects a start date later than the end date with a friendly error.

10. **Which database design decisions matter most here?**  
    Entity tables use business primary keys, relationships are enforced with foreign keys, and indexes support common joins and analytical filters.
