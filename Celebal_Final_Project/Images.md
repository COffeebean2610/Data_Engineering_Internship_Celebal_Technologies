# Project Screenshots

This document contains the screenshots captured as evidence for each phase of the Data Engineering project.

---

# Phase 1 — Ingestion & Bronze

## 1. Databricks Workspace & Raw Folder Structure

![Raw Folder Structure](screenshots/phase1/raw_folder_structure1.png)
![Raw Folder Structure](screenshots/phase1/raw_folder_structure2.png)
![Raw Folder Structure](screenshots/phase1/raw_folder_structure3.png)
![Raw Folder Structure](screenshots/phase1/raw_folder_structure4.png)

---

## 2. Landing Parquet Files

![Landing Parquet](screenshots/phase1/landing_parquet1.png)
![Landing Parquet](screenshots/phase1/landing_parquet2.png)
![Landing Parquet](screenshots/phase1/landing_parquet3.png)

---

## 3. Audit Validation (PASS)

![Audit PASS](screenshots/phase1/audit_pass1.png)
![Audit PASS](screenshots/phase1/audit_pass2.png)
![Audit PASS](screenshots/phase1/audit_pass3.png)

---

## 4. Bronze Delta Tables

![Bronze Delta](screenshots/phase1/bronze_delta1.png)
![Bronze Delta](screenshots/phase1/bronze_delta2.png)

---

## 5. Bronze Row Count Validation

![Bronze Row Counts](screenshots/phase1/bronze_row_counts1.png)
![Bronze Row Counts](screenshots/phase1/bronze_row_counts2.png)

---

# Phase 2 — Silver

## 1. Customer SCD Type 2

![Customer SCD Type 2](screenshots/phase2/customer_scd_type2-1.png)
![Customer SCD Type 2](screenshots/phase2/customer_scd_type2-2.png)
![Customer SCD Type 2](screenshots/phase2/customer_scd_type2-3.png)

---

## 2. Product SCD Type 1

![Product SCD Type 1](screenshots/phase2/product_scd_type1-1.png)
![Product SCD Type 1](screenshots/phase2/product_scd_type1-2.png)
![Product SCD Type 1](screenshots/phase2/product_scd_type1-3.png)

---

## 3. Delta MERGE Operation

![MERGE Operation](screenshots/phase2/merge_operation1.png)
![MERGE Operation](screenshots/phase2/merge_operation2.png)
![MERGE Operation](screenshots/phase2/merge_operation3.png)

---

## 4. Duplicate Removal Validation

![Duplicate Removal](screenshots/phase2/duplicate_removal1.png)
![Duplicate Removal](screenshots/phase2/duplicate_removal2.png)
![Duplicate Removal](screenshots/phase2/duplicate_removal3.png)

---

## 5. Surrogate Key Generation

![Surrogate Keys](screenshots/phase2/surrogate_keys1.png)
![Surrogate Keys](screenshots/phase2/surrogate_keys2.png)
![Surrogate Keys](screenshots/phase2/surrogate_keys3.png)
![Surrogate Keys](screenshots/phase2/surrogate_keys4.png)
![Surrogate Keys](screenshots/phase2/surrogate_keys5.png)

---

## 6. Silver Tables

### Customer

![Silver Customer](screenshots/phase2/silver_customer1.png)

### Product

![Silver Product](screenshots/phase2/silver_customer2.png)

### Sales

![Silver Sales](screenshots/phase2/silver_customer3.png)

---

# Phase 3 — Gold

## 1. Star Schema

![Star Schema](screenshots/phase3/star_schema.png)

---

## 2. Dimension Tables

### Customer Dimension

![dim_customer](screenshots/phase3/dim_customer1.png)
![dim_customer](screenshots/phase3/dim_customer2.png)

### Product Dimension

![dim_product](screenshots/phase3/dim_product1.png)
![dim_product](screenshots/phase3/dim_product2.png)
![dim_product](screenshots/phase3/dim_product3.png)

### Promotion Dimension

![dim_promotion](screenshots/phase3/dim_promotion1.png)
![dim_promotion](screenshots/phase3/dim_promotion2.png)

### Date Dimension

![dim_date](screenshots/phase3/dim_date1.png)
![dim_date](screenshots/phase3/dim_date2.png)

---

## 3. Fact Table

![fact_sales](screenshots/phase3/fact_sales1.png)
![fact_sales](screenshots/phase3/fact_sales2.png)

---

## 4. Unity Catalog Registration

![Unity Catalog](screenshots/phase3/unity_catalog_gold_tables.png)

---

## 5. KPI Outputs

### Net Margin by Region

![Net Margin](screenshots/phase3/kpi_net_margin_region.png)

---

### Average Order Value by Promotion

![AOV](screenshots/phase3/kpi_aov_promotion.png)

---

### Demographic Churn Heatmap

![Churn Heatmap](screenshots/phase3/kpi_churn_heatmap.png)

---

### Product Quality Index

![Product Quality Index](screenshots/phase3/kpi_product_quality.png)

---

### Store Traffic by Hour

![Store Traffic](screenshots/phase3/kpi_store_traffic.png)

---

# Phase 4 — Final Validation

## 1. End-to-End Pipeline Execution

![End-to-End Validation](screenshots/phase4/end_to_end_validation1.png)
![End-to-End Validation](screenshots/phase4/end_to_end_validation2.png)
![End-to-End Validation](screenshots/phase4/end_to_end_validation3.png)
![End-to-End Validation](screenshots/phase4/end_to_end_validation4.png)
![End-to-End Validation](screenshots/phase4/end_to_end_validation5.png)

---

## 2. Idempotency Test

![Idempotency Test](screenshots/phase4/idempotency_test1.png)
![Idempotency Test](screenshots/phase4/idempotency_test2.png)
![Idempotency Test](screenshots/phase4/idempotency_test3.png)
![Idempotency Test](screenshots/phase4/idempotency_test4.png)
![Idempotency Test](screenshots/phase4/idempotency_test5.png)
![Idempotency Test](screenshots/phase4/idempotency_test6.png)

---

## 3. Audit Failure Test

![Audit Failure](screenshots/phase4/audit_failure_test1.png)
![Audit Failure](screenshots/phase4/audit_failure_test2.png)
![Audit Failure](screenshots/phase4/audit_failure_test3.png)
![Audit Failure](screenshots/phase4/audit_failure_test4.png)
![Audit Failure](screenshots/phase4/audit_failure_test5.png)
![Audit Failure](screenshots/phase4/audit_failure_test6.png)
![Audit Failure](screenshots/phase4/audit_failure_test7.png)

---

## 4. Duplicate Validation

![Duplicate Validation](screenshots/phase4/duplicate_validation1.png)
![Duplicate Validation](screenshots/phase4/duplicate_validation2.png)
![Duplicate Validation](screenshots/phase4/duplicate_validation3.png)
![Duplicate Validation](screenshots/phase4/duplicate_validation4.png)
![Duplicate Validation](screenshots/phase4/duplicate_validation5.png)
![Duplicate Validation](screenshots/phase4/duplicate_validation6.png)

---

## 5. Final Validation Summary

![Validation Summary](screenshots/phase4/final_summary1.png)
![Validation Summary](screenshots/phase4/final_summary2.png)
![Validation Summary](screenshots/phase4/final_summary3.png)
![Validation Summary](screenshots/phase4/final_summary4.png)
![Validation Summary](screenshots/phase4/final_summary5.png)
![Validation Summary](screenshots/phase4/final_summary6.png)
![Validation Summary](screenshots/phase4/final_summary7.png)
![Validation Summary](screenshots/phase4/final_summary8.png)

---

## 6. Overall Project Completion

![Project Completion](screenshots/phase4/project_completion.png)

---

# Screenshot Folder Structure

```
screenshots/
│
├── phase1/
│   ├── raw_folder_structure.png
│   ├── landing_parquet.png
│   ├── audit_pass.png
│   ├── bronze_delta.png
│   └── bronze_row_counts.png
│
├── phase2/
│   ├── customer_scd_type2.png
│   ├── product_scd_type1.png
│   ├── merge_operation.png
│   ├── duplicate_removal.png
│   ├── surrogate_keys.png
│   ├── silver_customer.png
│   ├── silver_product.png
│   └── silver_sales.png
│
├── phase3/
│   ├── star_schema.png
│   ├── dim_customer.png
│   ├── dim_product.png
│   ├── dim_promotion.png
│   ├── dim_date.png
│   ├── fact_sales.png
│   ├── unity_catalog_gold_tables.png
│   ├── kpi_net_margin_region.png
│   ├── kpi_aov_promotion.png
│   ├── kpi_churn_heatmap.png
│   ├── kpi_product_quality.png
│   └── kpi_store_traffic.png
│
└── phase4/
    ├── end_to_end_validation.png
    ├── idempotency_test.png
    ├── audit_failure_test.png
    ├── duplicate_validation.png
    ├── final_summary.png
    └── project_completion.png
```
