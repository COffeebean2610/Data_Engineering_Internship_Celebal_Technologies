# Shopping Dataset - Data Engineering Analysis 🛍️

A comprehensive **data engineering and exploratory data analysis** project on a large-scale e-commerce shopping dataset. This project demonstrates data loading, cleaning, transformation, analysis, and visualization using Python for the Celebal Technologies Data Engineering Internship.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Dataset Description](#dataset-description)
- [Key Features & Concepts](#key-features--concepts)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Requirements](#requirements)
- [Running the Project](#running-the-project)
- [Analysis Workflow](#analysis-workflow)
- [Technologies Used](#technologies-used)
- [Dataset Source](#dataset-source)

---

## 🎯 Project Overview

This project provides an **end-to-end data engineering pipeline** for analyzing a comprehensive e-commerce shopping dataset containing **1000+ products** across multiple categories. The analysis includes:

- **Data Exploration**: Understanding dataset structure, shape, and statistical properties
- **Data Cleaning**: Handling missing values, duplicates, and data type conversions
- **Feature Engineering**: Creating new features and enriching existing data
- **Exploratory Data Analysis (EDA)**: Discovering patterns, trends, and insights
- **Data Visualization**: Creating meaningful charts and dashboards to communicate findings
- **Statistical Analysis**: Computing metrics and relationships between variables

This project is ideal for learning **data engineering practices**, **pandas manipulation**, **data visualization**, and **business intelligence**.

---

## 📊 Dataset Description

### Overview
The dataset comprises **e-commerce product data** from multiple product categories including clothing, accessories, home goods, and more. The combined dataset aggregates data from **95+ category files** into a unified CSV structure.

### Dataset Statistics
- **Total Records**: 1000+ products
- **Total Features**: Multiple columns covering product attributes
- **Categories**: 95+ categories (clothing, footwear, home goods, beauty products, etc.)
- **File Format**: CSV
- **File Size**: ~11 MB (combined dataset)
- **Data Quality**: Well-structured with realistic e-commerce attributes

### Key Columns

| Column Name | Description |
|---|---|
| `product_id` | Unique identifier for each product |
| `title` | Product name/title |
| `product_description` | Detailed product description |
| `rating` | Average customer rating (0-5 scale) |
| `ratings_count` | Number of customer ratings received |
| `initial_price` | Original product price before discount |
| `discount` | Discount percentage (%) |
| `final_price` | Final price after discount |
| `currency` | Currency type (e.g., USD, INR) |
| `images` | URL(s) of product images |
| `delivery_options` | Available delivery methods |
| `product_details` | Additional product attributes |
| `breadcrumbs` | Category hierarchy/path |
| `product_specifications` | Technical specifications |
| `seller_name` | Name of the seller |
| `seller_information` | Seller details and ratings |
| `sizes` | Available sizes (for applicable products) |
| `variations` | Different product variants |
| `category` | Product category classification |

---

## 🔑 Key Features & Concepts

### Data Engineering Concepts
1. **ETL Pipeline**: Extract, Transform, Load data systematically
2. **Data Validation**: Ensure data integrity and quality
3. **Data Normalization**: Convert and standardize data types
4. **Missing Value Handling**: Strategies for incomplete data
5. **Duplicate Detection**: Identify and remove redundant records

### Analysis Concepts
1. **Descriptive Statistics**: Mean, median, mode, standard deviation
2. **Distribution Analysis**: Understanding data spread and patterns
3. **Correlation Analysis**: Relationships between numerical features
4. **Category Analysis**: Insights by product categories
5. **Price Analysis**: Pricing trends, discounts, and strategies
6. **Rating Analysis**: Customer satisfaction patterns
7. **Seller Performance**: Comparative seller metrics

### Visualization Techniques
- Histograms for distribution analysis
- Box plots for outlier detection
- Scatter plots for correlation analysis
- Bar charts for categorical comparisons
- Heatmaps for correlation matrices
- Time series plots (if applicable)

---

## 📁 Project Structure

```
Data_Engineering_Internship_Celebal_Technologies/
│
├── README.md                          # Project documentation (this file)
├── data_analysis.ipynb               # Main analysis notebook
│
└── combined_dataset/                 # Dataset directory
    ├── Combined_dataset.csv          # Merged dataset from all categories
    ├── backpacks.csv
    ├── bath-robe.csv
    ├── boots.csv
    ├── dresses.csv
    ├── jeans.csv
    ├── kurtas.csv
    ├── sandals.csv
    └── [90+ more category files]
```

### File Descriptions
- **data_analysis.ipynb**: Main Jupyter notebook containing all analysis code, visualizations, and insights
- **Combined_dataset.csv**: Aggregated dataset from all product categories
- **Individual CSV Files**: Separate datasets for each product category

---

## 🔧 Installation

### Prerequisites
- **Python**: 3.7 or higher
- **pip**: Python package manager
- **Git**: For version control (optional)

### Step-by-Step Setup

#### 1. Clone or Download the Repository
```bash
# If using git
git clone <repository-url>
cd Data_Engineering_Internship_Celebal_Technologies

# Or simply download and extract the project folder
```

#### 2. Create a Virtual Environment (Recommended)
```bash
# On Windows
python -m venv .venv
.\.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Upgrade pip
```bash
pip install --upgrade pip
```

#### 4. Install Required Dependencies
```bash
pip install -r requirements.txt
```

**If requirements.txt is not available**, install manually:
```bash
pip install pandas numpy matplotlib seaborn jupyter notebook
```

---

## 📦 Requirements

### Python Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| `pandas` | >=1.3.0 | Data manipulation and analysis |
| `numpy` | >=1.21.0 | Numerical computing |
| `matplotlib` | >=3.4.0 | Data visualization |
| `seaborn` | >=0.11.0 | Statistical data visualization |
| `jupyter` | >=1.0.0 | Interactive notebook environment |
| `notebook` | >=6.4.0 | Jupyter Notebook server |

### System Requirements
- **RAM**: Minimum 4 GB (8 GB recommended)
- **Disk Space**: 500 MB for dataset and project files
- **Operating System**: Windows, macOS, or Linux

---

## 🚀 Running the Project

### Method 1: Using Jupyter Notebook (Recommended)

#### 1. Start Jupyter Notebook Server
```bash
# Make sure you're in the project directory with virtual environment activated
jupyter notebook
```

#### 2. Open the Analysis Notebook
- Jupyter will open in your default browser at `http://localhost:8888`
- Click on `data_analysis.ipynb` to open the main notebook

#### 3. Run the Analysis
- **Run all cells**: Click `Cell` → `Run All` in the menu
- **Run individual cells**: Click the cell and press `Shift + Enter`
- **Clear outputs**: Click `Cell` → `All Output` → `Clear` to reset

### Method 2: Using VS Code

#### 1. Open Project in VS Code
```bash
code .
```

#### 2. Install Jupyter Extension
- Go to Extensions (Ctrl+Shift+X)
- Search for "Jupyter" and install the official Microsoft Jupyter extension

#### 3. Open and Run Notebook
- Click on `data_analysis.ipynb`
- Select Python interpreter from the top-right dropdown
- Run cells individually or all at once

### Method 3: Using Command Line

#### 1. Run Notebook as Script (Convert to Python)
```bash
jupyter nbconvert --to script data_analysis.ipynb
python data_analysis.py
```

#### 2. Generate HTML Report
```bash
jupyter nbconvert --to html data_analysis.ipynb
# This creates data_analysis.html - open in any browser
```

---

## 📈 Analysis Workflow

The project is organized into sequential analysis steps:

### Step 1: Load Data
- Import required libraries (pandas, numpy, matplotlib, seaborn)
- Load the combined dataset from CSV
- Display dataset shape and column information

### Step 2: Understand Data
- Check data types for all columns
- Identify missing/null values and compute percentages
- Generate summary statistics using `.info()` and `.describe()`

### Step 3: Data Cleaning
- Convert price columns to numeric format
- Handle missing values (removal or imputation)
- Remove duplicate records
- Fix data type inconsistencies

### Step 4: Feature Engineering
- Create new features from existing columns
- Extract useful information from product descriptions
- Engineer price-related features (discount impact, price ranges)
- Normalize categorical variables

### Step 5: Exploratory Data Analysis
- Analyze price distributions and statistics
- Examine customer ratings and reviews
- Explore product categories and popularity
- Investigate seller performance metrics

### Step 6: Data Visualization
- Distribution plots for numerical features
- Category analysis charts
- Price vs. Rating correlations
- Discount impact visualizations
- Top categories and products
- Heatmaps for feature correlations

### Step 7: Insights & Conclusions
- Summarize key findings
- Identify business insights
- Highlight data quality issues
- Suggest improvements

---

## 💻 Technologies Used

### Data Processing & Analysis
- **Pandas**: Data manipulation, cleaning, and transformation
- **NumPy**: Numerical operations and array computations

### Visualization
- **Matplotlib**: Core plotting library
- **Seaborn**: Statistical visualization and styling

### Development Environment
- **Jupyter Notebook**: Interactive coding and documentation
- **Python 3.7+**: Programming language

### Version Control (Optional)
- **Git**: Source code management

---

## 📥 Dataset Source

**Dataset**: Kaggle Shopping Dataset (Ecommerce Dataset with Products & Sizes)

- **Source**: https://www.kaggle.com/datasets/anvitkumar/shopping-dataset
- **Author**: Anvit Kumar
- **License**: MIT License
- **Update Frequency**: Hourly
- **Use Cases**: 
  - E-commerce website development
  - Price prediction models
  - Recommendation systems
  - Sentiment analysis on customer reviews
  - Market and competitor analysis

---

## 🎓 Learning Outcomes

By completing this project, you will learn:

✅ How to load and explore large datasets
✅ Data cleaning and preprocessing techniques
✅ Missing value handling strategies
✅ Feature engineering methodologies
✅ Statistical analysis and EDA
✅ Professional data visualization
✅ Working with Jupyter Notebooks
✅ Python data science libraries (pandas, numpy, matplotlib, seaborn)
✅ Business insights extraction from data
✅ Best practices for data engineering projects

---

## 💡 Tips & Best Practices

1. **Always use virtual environments** to avoid package conflicts
2. **Explore data incrementally** - don't skip the data understanding step
3. **Handle missing values thoughtfully** - context matters
4. **Validate assumptions** with visualizations before drawing conclusions
5. **Document your findings** with markdown cells in the notebook
6. **Keep your notebook clean** - remove debugging code before finalizing
7. **Use descriptive variable names** for better code readability

---

## 🤝 Contributing

This is an educational project for Celebal Technologies internship. Feel free to:
- Add more analysis sections
- Improve visualizations
- Create additional insights
- Fix bugs or improve code quality

---

## 📝 License

This project is provided under the **MIT License** (same as the source dataset).

---

## ❓ FAQ

**Q: Can I use this project for commercial purposes?**
A: The dataset is under MIT License, so yes, with proper attribution.

**Q: How do I handle large datasets that don't fit in memory?**
A: Use pandas `chunksize` parameter when reading CSV, or use tools like Dask.

**Q: Can I extend this analysis further?**
A: Absolutely! Consider adding machine learning models, advanced visualizations, or deeper statistical analysis.

**Q: Where can I get help?**
A: Check Kaggle discussion forums for the dataset, or consult pandas documentation.

---

## 📧 Contact & Support

For questions about this project, please refer to the Celebal Technologies internship guidelines or consult the project documentation.

---

**Last Updated**: June 2026
**Project Status**: Active
**Python Version**: 3.7+
