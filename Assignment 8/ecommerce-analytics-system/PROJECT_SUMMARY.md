# Project Summary

## Problem Statement

E-commerce operational data is often distributed across customer, product, order, and line-item files. The project demonstrates how to transform that data into a validated, queryable analytics system.

## Solution

The system generates realistic source data, cleans and validates it with pandas, loads it into a constrained SQLite schema, and produces SQL and command-line business reports. Automated tests verify data quality, database integrity, report exports, and failure handling.

## Modules

- Data generation
- Data cleaning and validation
- SQLite schema creation and loading
- Standard SQL analytics and views
- Advanced SQL analytics
- Python CLI reporting
- Automated testing

## Tech Stack

Python, pandas, Faker, SQLite, SQL, tabulate, unittest, and pathlib.

## Key Features

- Transactional SQLite loading with foreign-key enforcement
- Business KPIs and report exports
- Window functions, CTEs, cohort analysis, and RFM segmentation
- Date-filtered command-line reporting
- CSV, TXT, logging, and test-summary artifacts

## Business Insights

The project identifies customer lifetime value, high-value customers and products, revenue trends, category and regional performance, repeat behavior, returns, churn, retention, and customer segments.

## Learning Outcomes

- Design normalized relational schemas and enforce integrity rules
- Build repeatable ETL-style workflows in Python
- Write analytical SQL using joins, aggregates, CTEs, views, and windows
- Build robust CLI tools and automated tests

## GitHub Metadata

**Repository description (max 350 characters):** End-to-end e-commerce data engineering project using Python, pandas, SQLite, SQL analytics, cohort and RFM analysis, a date-filtered CLI reporting tool, and automated tests.

**Tagline:** From raw e-commerce data to validated, queryable business insights.

**Topics:** `python`, `pandas`, `sqlite`, `sql`, `data-engineering`, `data-analytics`, `etl`, `cli`, `cohort-analysis`, `rfm-analysis`, `window-functions`, `testing`
