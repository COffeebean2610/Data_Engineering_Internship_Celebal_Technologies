# Assessment 3: Advanced SQL Analytics on Superstore Dataset

## Objective
The objective of this project was to apply advanced SQL concepts to a retail sales dataset by loading raw transactional data into a staging table, normalizing it into relational tables, and performing business analysis using Subqueries, Common Table Expressions (CTEs), Window Functions, and JOIN operations. The project aims to transform raw sales data into meaningful insights that support business decision-making.

## Dataset Description
The Superstore dataset contains approximately 9,994 sales transactions across different customers, products, categories, and regions. Each record includes order information, customer details, product information, sales amount, quantity, discount, and profit, making it suitable for practicing advanced SQL analytics and business intelligence techniques.

## Database Schema
- superstore_raw – staging table containing imported raw sales data.
- customers – customer information.
- products – product information.
- orders – transactional sales records containing order-level information linked to customers.

## Workflow
CSV Dataset
        │
        ▼
superstore_raw (Staging Table)
        │
        ▼
Normalized Tables
(customers, products, orders)
        │
        ▼
Advanced SQL Queries
(Subqueries, CTEs, Window Functions, JOINs)
        │
        ▼
Business Insights & Analysis

## Techniques Used
- Subqueries
- Common Table Expressions (CTEs)
- Window Functions (ROW_NUMBER(), RANK(), DENSE_RANK())
- Aggregate Functions (SUM(), AVG(), COUNT())
- GROUP BY and HAVING
- JOIN operations

## Key Findings
1. Customers whose total sales exceeded the average customer sales were identified using CTEs and subqueries, showing that a relatively small number of customers generated significantly higher revenue.
2. Window functions ranked customers by total sales, making it easy to identify the top-performing and lowest-performing customers.
3. Category-wise sales analysis showed differences in revenue contribution across product categories.
4. Several customers placed only one order, indicating opportunities for improving customer retention.
5. Profit analysis revealed that high sales values do not always correspond to high profits because discounts can reduce profitability.
6. Joining customer, order, and product data provided a comprehensive view of customer purchasing behavior and sales performance.

## Conclusion
This project demonstrated how advanced SQL techniques can be applied to transform raw transactional data into meaningful business insights. Through data normalization, analytical queries, Subqueries, CTEs, Window Functions, and JOIN operations, the dataset was effectively analyzed to identify customer behavior, sales trends, and business performance. The assignment strengthened practical SQL skills commonly used in data analytics and business intelligence.

## File Included
- superstore_advanced_sql.sql: complete SQL script for loading, transforming, and analyzing the dataset
