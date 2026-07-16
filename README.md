
# 🛒 Store Pulse

**Store Pulse** is an end-to-end retail analytics platform that transforms raw Walmart sales data into clean, analytics-ready datasets using a modern ETL pipeline. The project is being developed as part of the OpenAI Hackathon.

---

## 📌 Project Overview

Retail businesses generate massive amounts of transactional data every day. However, raw data is often incomplete, inconsistent, and difficult to analyze directly.

Store Pulse solves this problem by:

- Extracting raw retail datasets
- Cleaning and validating the data
- Combining multiple data sources
- Loading the processed dataset into PostgreSQL
- Preparing the data for dashboards and business analytics

---

## 🎯 Objectives

- Build a complete ETL pipeline
- Store cleaned data in PostgreSQL (Supabase)
- Generate business insights through SQL
- Build interactive dashboards
- Demonstrate a real-world Data Engineering workflow

---

## ✨ Features

- ✅ Automated data extraction
- ✅ Data cleaning and preprocessing
- ✅ Missing value handling
- ✅ Duplicate removal
- ✅ Data quality checks
- ✅ Merge multiple datasets
- ✅ PostgreSQL integration
- ✅ SQL-based analytics
- 🔄 Dashboard visualization *(Coming Soon)*

---

# 🏗 Project Architecture

```
               Raw CSV Files
                      │
                      ▼
              Extract Pipeline
                      │
                      ▼
           Data Cleaning & Merge
                      │
                      ▼
          Data Quality Validation
                      │
                      ▼
         Processed Clean Dataset
                      │
                      ▼
        PostgreSQL (Supabase)
                      │
                      ▼
        SQL Analytics & Dashboard
```

---

# 📂 Project Structure

```
store-pulse/
│
├── config/
│   └── schema.yaml
│
├── data/
│   ├── raw/
│   │   ├── train.csv
│   │   ├── stores.csv
│   │   └── features.csv
│   │
│   └── processed/
│       └── clean_sales.csv
│
├── etl/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── sql/
│   ├── schema.sql
│   └── queries.sql
│
├── run_pipeline.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Data Processing | Pandas |
| Database | PostgreSQL |
| Cloud Database | Supabase |
| ORM | SQLAlchemy |
| Environment | python-dotenv |
| SQL Driver | psycopg2 |
| Version Control | Git & GitHub |

---

# 🔄 ETL Workflow

## 1. Extract

Reads the following datasets:

- `train.csv`
- `stores.csv`
- `features.csv`

---

## 2. Transform

The transformation stage performs:

- Merge datasets
- Convert date formats
- Handle missing values
- Remove duplicates
- Validate data quality
- Generate clean dataset

---

## 3. Load

The cleaned dataset is:

- Saved as `clean_sales.csv`
- Loaded into PostgreSQL (Supabase)
- Verified after insertion

---

# 📊 Database

The cleaned data is stored inside the PostgreSQL table:

```
clean_sales
```

Main columns include:

- Store
- Department
- Date
- Weekly Sales
- Store Type
- Temperature
- Fuel Price
- CPI
- Unemployment
- Holiday Flag
- Markdown Features

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/OpenAI-Hackathon-Team/store-pulse.git

cd store-pulse
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file using `.env.example`.

Example:

```env
DB_HOST=your_host
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## Run ETL Pipeline

```bash
python run_pipeline.py
```

---

# 📈 Current Progress

- ✅ Extract Pipeline
- ✅ Transform Pipeline
- ✅ Load Pipeline
- ✅ PostgreSQL Integration
- ✅ SQL Schema
- 🚧 Dashboard Development
- 🚧 Business KPIs
- 🚧 Streamlit Web App

---

# 🔮 Future Enhancements

- Interactive Streamlit Dashboard
- Sales Forecasting
- Automated ETL Scheduling
- Incremental Data Loading
- Docker Support
- Cloud Deployment
- CI/CD Pipeline

---

# 👥 Team

**OpenAI Hackathon Team**

Project: **Store Pulse**

---

# 📄 License

This project is developed for the OpenAI Hackathon and is intended for educational and demonstration purposes.
