# Celebal Data Engineering Project

A complete end-to-end data engineering pipeline built on Databricks, implementing medallion architecture (Bronze-Silver-Gold) with PySpark. This project demonstrates data ingestion, transformation, quality validation, SCD implementation, and business intelligence layer creation using Delta Lake and Unity Catalog.

---

## Project Objectives

This project was developed as part of my Data Engineering internship to demonstrate proficiency in:

- Designing and implementing a multi-layer data lakehouse architecture
- Building fault-tolerant data pipelines with audit validation
- Applying data quality rules and handling missing/duplicate data
- Implementing Slowly Changing Dimensions (SCD Type 1 and Type 2)
- Creating a star schema for analytical reporting
- Generating business KPIs using PySpark and Databricks SQL
- Ensuring pipeline idempotency and data consistency

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Platform** | Databricks (Serverless Compute) |
| **Language** | PySpark, SQL |
| **Storage** | Databricks Volumes |
| **File Formats** | CSV, Parquet, Delta Lake |
| **Data Catalog** | Unity Catalog |
| **Architecture** | Medallion (Bronze-Silver-Gold) |

---

## Project Architecture

![Architecture](documentation/Architecture.png)

The project follows a medallion architecture with five distinct layers:

- **Raw Layer**: Source CSV files stored as-is in Databricks Volumes
- **Landing Layer**: Data converted to Parquet format with audit validation
- **Bronze Layer**: Delta Lake tables with append-only ingestion and audit trails
- **Silver Layer**: Cleaned, deduplicated data with SCD Type 1/2 implementations
- **Gold Layer**: Star schema optimized for analytics and reporting

Each layer is validated before data flows to the next stage. Audit logs track row counts at every step, and the pipeline halts if validation fails.

---

## Project Workflow

```
Raw (CSV)
    ↓
Landing (Parquet + Audit Validation)
    ↓
Bronze (Delta Lake - Append Only)
    ↓
Silver (Delta Lake - Cleaned, SCD)
    ↓
Gold (Star Schema - Unity Catalog)
    ↓
Analytics (KPIs & Reports)
```

**Raw → Landing**: Ingest CSV files, convert to Parquet, validate row counts  
**Landing → Bronze**: Load raw data into Delta tables with ingestion timestamps  
**Bronze → Silver**: Apply data quality rules, deduplicate, implement SCD logic  
**Silver → Gold**: Build dimension and fact tables, register in Unity Catalog  
**Gold → Analytics**: Generate business KPIs and insights

---

## Folder Structure

```
celebal-data-engineering-project/
│
├── notebooks/
│   ├── 01_Raw_Landing_Audit.ipynb
│   ├── 02_Bronze_Silver.ipynb
│   ├── 03_Gold_StarSchema_KPIs.ipynb
│   └── 04_Final_Validation_Testing.ipynb
│
├── documentation/
│   ├── Architecture.png
│   ├── screenshots.md
│   └── phase-details/
│
├── screenshots/
│   ├── phase1/
│   ├── phase2/
│   ├── phase3/
│   └── phase4/
│
└── README.md
```

---

## Phase 1 — Ingestion & Audit Validation

**Objective**: Ingest raw CSV data into the lakehouse with audit validation to ensure data integrity.

**Implementation**:
- Uploaded source CSV files (Customer, Product, Sales) to Databricks Volumes
- Separated historical and incremental datasets
- Ingested raw data as strings to prevent schema inference issues
- Converted to Parquet in the Landing layer for efficient storage
- Implemented dynamic audit validation comparing expected vs actual row counts
- Pipeline stops execution if audit validation fails (PASS/FAIL mechanism)
- Created Bronze Delta tables with `ingested_at` timestamp
- Configured incremental append for new data while keeping Bronze append-only

**Key Deliverable**: Fault-tolerant ingestion pipeline with automated audit trails.

---

## Phase 2 — Silver Layer Transformations

**Objective**: Clean and transform Bronze data, implement business logic, and ensure data quality.

**Implementation**:

**Data Quality**:
- Removed records with missing primary keys
- Handled duplicates using window-based deduplication
- Cast numeric columns to appropriate types (int, double)
- Replaced string nulls ("Unknown", "N/A") with NULL
- Applied default values for numeric nulls

**SCD Implementation**:
- **Customer**: SCD Type 2 with version history, effective dates, and `is_current` flag
- **Product**: SCD Type 1 with simple updates (always latest version)
- **Sales**: Immutable ledger with window-based deduplication

**Delta MERGE**:
- Used Delta Lake MERGE operations for upserts
- Existing records updated, new records inserted
- Maintained full history for SCD Type 2 entities

**Surrogate Keys**:
- Generated `customer_sk`, `product_sk`, `sales_sk` using `monotonically_increasing_id()`
- Validated uniqueness and referential integrity

**Key Deliverable**: Clean, normalized Silver layer with SCD logic and surrogate keys.

---

## Phase 3 — Gold Star Schema & KPIs

**Objective**: Build a star schema optimized for analytics and generate business KPIs.

**Star Schema Design**:

**Dimension Tables**:
- `dim_customer`: Customer demographics, loyalty, SCD Type 2 history
- `dim_product`: Product attributes, pricing, quality metrics
- `dim_promotion`: Promotion types and IDs
- `dim_date`: Date hierarchy with seasonality and weekend flags

**Fact Table**:
- `fact_sales`: Transactional data with foreign keys to all dimensions

**Unity Catalog Registration**:
- All Gold tables registered in `workspace.GOLD_tables` schema
- Tables queryable across the organization

**KPIs Generated**:
1. **Net Margin by Region**: Total sales grouped by store location
2. **Average Order Value by Promotion**: AOV calculated per promotion type
3. **Demographic Churn Heatmap**: Customer churn analysis by gender and income bracket
4. **Product Quality Index**: Calculated as `rating × (1 - return_rate)`
5. **Store Traffic by Hour**: Transaction counts by hour of day

**Key Deliverable**: Production-ready star schema with business intelligence layer.

---

## Phase 4 — Final Validation & Testing

**Objective**: Ensure the entire pipeline is robust, idempotent, and production-ready.

**Tests Executed**:

1. **End-to-End Pipeline Testing**: Validated data flow across all layers (Raw → Gold)
2. **Idempotency Testing**: Verified re-running the pipeline produces consistent results
3. **Duplicate Validation**: Confirmed Bronze preserves duplicates, Silver deduplicates
4. **Audit Failure Testing**: Tested pipeline behavior when audit validation fails
5. **Data Quality Validation**: Checked data types, null values, and value ranges
6. **Star Schema Integrity**: Validated foreign key relationships in the star schema
7. **Code Quality Review**: Verified Delta Lake best practices and naming conventions

**Results**:
- **Total Tests**: 44
- **Passed**: 44
- **Failed**: 0
- **Success Rate**: 100%

**Key Deliverable**: Fully validated, production-grade data pipeline.

---

## Star Schema

### Dimension Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| **dim_customer** | Customer demographics and loyalty information with SCD Type 2 history | `customer_sk`, `customer_id`, `age`, `gender`, `income_bracket`, `churned`, `version`, `is_current` |
| **dim_product** | Product catalog with pricing and quality metrics | `product_sk`, `product_id`, `product_name`, `product_category`, `product_rating`, `product_return_rate` |
| **dim_promotion** | Promotion types and identifiers | `promotion_sk`, `promotion_id`, `promotion_type` |
| **dim_date** | Date dimension with time hierarchy and seasonality | `date_sk`, `transaction_date`, `day_of_week`, `month_of_year`, `season`, `holiday_season`, `weekend` |

### Fact Table

| Table | Description | Key Columns |
|-------|-------------|-------------|
| **fact_sales** | Transactional sales data with foreign keys to dimensions | `sales_sk`, `customer_sk`, `product_sk`, `promotion_sk`, `date_sk`, `quantity`, `unit_price`, `total_sales` |

The star schema enables efficient analytical queries by denormalizing data and pre-joining dimensions to the central fact table.

---

## KPIs Implemented

| KPI | Description | Business Value |
|-----|-------------|----------------|
| **Net Margin by Region** | Total sales grouped by store location | Identifies highest-performing regions for resource allocation |
| **Average Order Value by Promotion** | AOV calculated per promotion type | Measures promotion effectiveness and campaign ROI |
| **Demographic Churn Heatmap** | Customer churn analysis by gender and income bracket | Identifies at-risk customer segments for retention strategies |
| **Product Quality Index** | Quality score: `rating × (1 - return_rate)` | Highlights high-quality products and flags problematic items |
| **Store Traffic by Hour** | Transaction counts by hour of day | Optimizes staffing and identifies peak shopping hours |

All KPIs are generated using PySpark transformations and are ready for visualization in Databricks dashboards or BI tools.

---

## Data Quality Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| **Primary Key Validation** | Remove records with missing primary keys | Filter out NULL `customer_id`, `product_id`, `transaction_id` |
| **Duplicate Removal** | Remove exact duplicate records | Use `dropDuplicates()` in Silver layer |
| **Type Casting** | Ensure numeric columns have correct types | Cast strings to `int`, `double` where appropriate |
| **Null Handling** | Replace string nulls with NULL | Map "Unknown", "N/A", empty strings to NULL |
| **Value Range Validation** | Ensure values are within valid ranges | Age: 18-120, Membership years: non-negative |
| **SCD Type 2 Logic** | Track historical changes for customers | Maintain version, effective dates, `is_current` flag |
| **Surrogate Key Uniqueness** | Ensure surrogate keys are unique | Validate `customer_sk`, `product_sk`, `sales_sk` |

---

## Project Screenshots

Detailed screenshots documenting each phase are available here:

[📸 View Project Screenshots](documentation/screenshots.md)

---

## How to Run

### Prerequisites
- Databricks Workspace (Community or Enterprise Edition)
- Databricks Volumes enabled
- Serverless Compute (or cluster with DBR 13.0+)

### Setup Instructions

1. **Upload Source Data**
   - Upload CSV files to `/Volumes/workspace/default/celebal_data/raw/`
   - Structure: `historical/` and `incremental/` folders for each entity

2. **Create Audit Files**
   - Place audit CSV files in `/Volumes/workspace/default/celebal_data/raw/audit_landing/`

3. **Run Notebooks in Order**
   ```
   01_Raw_Landing_Audit.ipynb
   02_Bronze_Silver.ipynb
   03_Gold_StarSchema_KPIs.ipynb
   04_Final_Validation_Testing.ipynb
   ```

4. **Verify Output**
   - Check Unity Catalog for `workspace.GOLD_tables` schema
   - Run KPI queries to validate output

### Expected Runtime
- Phase 1: ~2 minutes
- Phase 2: ~3 minutes
- Phase 3: ~2 minutes
- Phase 4: ~1 minute
- **Total**: ~8 minutes

---

## Key Learnings

- **Medallion Architecture**: Learned how to structure a lakehouse with clear separation of concerns (Raw, Bronze, Silver, Gold)
- **Delta Lake**: Gained hands-on experience with Delta MERGE, time travel, and schema evolution
- **Audit-Driven Development**: Implemented validation at every stage to catch data issues early
- **SCD Implementation**: Built both SCD Type 1 and Type 2 logic for different business needs
- **PySpark Optimization**: Used window functions, broadcast joins, and efficient aggregations
- **Data Quality**: Applied systematic cleaning rules instead of ad-hoc transformations
- **Star Schema Design**: Understood how to model data for analytical workloads
- **Idempotency**: Ensured re-running the pipeline produces consistent results
- **Unity Catalog**: Learned to register and manage tables in a centralized data catalog
- **Testing**: Wrote comprehensive validation tests to ensure production readiness

---

## Future Improvements

- Implement incremental processing using Delta Lake Change Data Feed (CDF)
- Add data lineage tracking using Databricks Lineage API
- Automate pipeline execution using Databricks Jobs or Workflows
- Implement data quality monitoring with Great Expectations or Databricks Data Quality
- Add unit tests for individual transformation functions
- Create Databricks dashboards for real-time KPI visualization
- Implement CI/CD pipeline using Databricks Asset Bundles (DABs)
- Add alerting for audit failures using Databricks Alerts
- Optimize large tables with Z-Ordering and partitioning
- Extend to support streaming data ingestion using Auto Loader

---

## Author

**Name**: Samradni Ashok Dahiphale  
**Role**: Data Engineering Intern  
**Platform**: Databricks

---

## Acknowledgments

This project was completed as part of the Celebal Technologies Data Engineering internship program. Special thanks to the mentors and team for guidance throughout the development process.