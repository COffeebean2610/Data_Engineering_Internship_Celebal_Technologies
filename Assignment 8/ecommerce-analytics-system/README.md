# E-Commerce Order Analytics System

An end-to-end data engineering project that generates e-commerce data, validates and loads it into SQLite, performs SQL analytics, and exposes reports through a Python command-line interface.

## Features

- Synthetic customer, product, order, and order-item data generation
- Cleaning, normalization, validation, and referential-integrity reporting
- SQLite schema with keys, checks, foreign keys, and analytical indexes
- Basic and advanced SQL analytics with views, CTEs, window functions, cohorts, and RFM segmentation
- Command-line reports with optional date filters and CSV/TXT export
- Automated validation, database, report, and edge-case tests

## Architecture

```text
Raw CSV data → Cleaning and validation → SQLite database
                                         ├─ SQL analytics and views
                                         ├─ Advanced analytics exports
                                         ├─ CLI reporting
                                         └─ Automated tests
```

## Project Structure

```text
ecommerce-analytics-system/
├── data/
│   ├── raw/                 # Generated source CSV files
│   └── cleaned/             # Validated CSV files used for loading
├── database/                # Local SQLite database
├── output/
│   ├── reports/             # CLI report exports
│   ├── sql_reports/         # Standard SQL analytics exports
│   ├── advanced_reports/    # Advanced analytics exports
│   └── tests/               # Test reports
├── scripts/                 # Python pipeline, reporting, and test modules
├── sql/                     # Schema, indexes, views, and analytical queries
├── tests/                   # Automated unittest suite
├── main.py                  # End-to-end pipeline entry point
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Technologies

- Python 3.10+
- SQLite and SQL
- pandas
- Faker
- tabulate
- unittest

## Database Schema

| Table | Purpose | Key relationships |
|---|---|---|
| `customers` | Customer master records | Referenced by `orders.customer_id` |
| `products` | Product catalog and pricing | Referenced by `order_items.product_id` |
| `orders` | Order headers and status | Belongs to a customer; referenced by order items |
| `order_items` | Order line items | Belongs to an order and product |

The schema enforces primary keys, customer email uniqueness, foreign keys, valid statuses/customer types, non-negative price and stock values, positive quantities, and discount limits.

## Workflow

1. Generate raw CSV files.
2. Clean and validate values, dates, and relationships.
3. Recreate and load the SQLite database.
4. Run basic and advanced SQL analytics.
5. Generate interactive CLI reports.
6. Run automated tests and export the test summary.

## Installation

```bash
git clone <repository-url>
cd ecommerce-analytics-system
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Requirements

Install the dependencies listed in `requirements.txt`:

- `faker` for synthetic data generation
- `pandas` for data transformation and exports
- `tabulate` for formatted terminal reports

## How to Run

Run the complete data pipeline:

```bash
python main.py
```

Run standard SQL analytics:

```bash
python -m scripts.run_queries
```

Run advanced SQL analytics:

```bash
python -m scripts.advanced_reports
```

Run all automated tests:

```bash
python scripts/test_runner.py
```

## CLI Usage

Generate a report for all available data:

```bash
python -m scripts.report_cli --report revenue
```

Use an inclusive date range:

```bash
python -m scripts.report_cli --report revenue --start-date 2025-01-01 --end-date 2025-06-30
```

Available reports:

```text
revenue, orders, customers, products, monthly_sales, category, region,
top_customers, top_products, segmentation, cohort, retention, returns
```

Use `--help` to view command options:

```bash
python -m scripts.report_cli --help
```

## SQL Analytics

The SQL modules include revenue, customer, product, order, regional, category, time, and return analytics. Reusable views include customer, product, order, revenue, monthly sales, and customer-revenue summaries.

Advanced modules cover:

- Ranking, running totals, moving averages, `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, and `NTILE`
- Multi-level CTEs for monthly, customer, product, churn, and repeat-purchase analysis
- First-purchase cohorts and a Month 0–3 retention matrix
- Purchase-frequency, spend, and RFM customer segmentation

## Testing

The test suite covers cleaned-data validation, database schema and integrity, every registered CLI report, exports, invalid arguments, missing databases, temporary constraint failures, empty files, and empty result sets.

Current test artifacts are saved in `output/tests/`:

- `test_report.txt`
- `test_summary.csv`

## Output Reports

| Location | Contents |
|---|---|
| `output/reports/` | CLI CSV and TXT reports |
| `output/sql_reports/` | Standard SQL analytics reports and log |
| `output/advanced_reports/` | Window, CTE, cohort, and segmentation reports |
| `output/tests/` | Test report and summary |

## Suggested Screenshots

Add screenshots to a `docs/screenshots/` directory and reference them here before publishing:

1. Project folder structure in VS Code
2. Data generation terminal output
3. Cleaning summary and validation files
4. SQLite tables and schema browser
5. SQL analytics terminal output
6. CLI revenue report with date filters
7. Cohort matrix or RFM segmentation CSV
8. Final automated test report

## Future Enhancements

- Add configurable data volumes and deterministic random seeds
- Add dashboard visualizations
- Support PostgreSQL as an alternative warehouse
- Schedule incremental loads and report delivery
- Add CI workflow for automated test execution

## Author

Samradni Dahiphale

## License

This project is licensed under the [MIT License](LICENSE).

For the project summary, repository metadata, interview preparation, and final checklist, see [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md), [INTERVIEW_PREPARATION.md](INTERVIEW_PREPARATION.md), and [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md).
