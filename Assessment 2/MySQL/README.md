# MySQL version of the SQL assignment

Use these files in MySQL Workbench, MySQL Command Line Client, or any MySQL-compatible tool.

## Steps in MySQL
1. Open MySQL Workbench or terminal.
2. Create the database:
   ```sql
   CREATE DATABASE IF NOT EXISTS sales_assignment;
   USE sales_assignment;
   ```
3. Run the setup script:
   - In Workbench: open the file and execute it.
   - In terminal: mysql -u root -p < setup/create_tables.sql
4. Load the data:
   - mysql -u root -p < setup/load_data.sql
5. Run the section files one by one.

## Files
- setup/create_tables.sql
- setup/load_data.sql
- Section_A/basic_queries.sql
- Section_B/filtering_queries.sql
- Section_C/aggregation_queries.sql
- Section_D/joins_queries.sql
- Section_E/advanced_queries.sql
