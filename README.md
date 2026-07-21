
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
- ✅ Interactive Streamlit dashboard

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
├── .streamlit/
│   └── config.toml
│
├── Config/
│   └── schema.yaml
│
├── data/
│   ├── raw/
│   │   ├── train.csv
│   │   ├── stores.csv
│   │   └── features.csv
│
├── etl/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── validation.py
│   └── load.py
│
├── sql/
│   └── schema.sql
│
├── .env.example
├── .gitignore
├── ai_insights.py
├── app.py
├── LICENSE
├── pipeline_logs.jsonl
├── pipeline_logs.py
├── README.md
├── requirements.txt
├── run_pipeline.py
└── test_logging.py
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
- Validate required fields, types, unique store keys, allowed store types, and value ranges using `Config/schema.yaml`
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
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-terra
```

---

## Run ETL Pipeline

```bash
python run_pipeline.py
```

The pipeline compares the raw source files with the last successful run and
skips the database load when nothing changed. To deliberately reload unchanged
data, set `FORCE_FULL_REFRESH=true` in `.env` for that run.

## Run Dashboard

After the ETL has loaded `clean_sales`, activate the virtual environment and
start the Streamlit dashboard:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Open the Local URL printed in the terminal, usually
`http://localhost:8501`.

The dashboard uses the same `DB_*` environment variables as the ETL and reads
from the PostgreSQL `clean_sales` table. It includes:

- Date, store, department, and holiday-week filters
- Total sales, average weekly sales, active-store, and sales-record KPIs
- A weekly sales trend
- Top 10 stores and departments by total sales
- A filtered data table with CSV download

The dashboard's native dark theme is configured in `.streamlit/config.toml`.

---

## How Codex and GPT-5.6 were used in building this project

### Codex usage

Codex was used throughout the project to scaffold the ETL workflow: extract, transform, validate, and load the Walmart sales data. It helped build the schema-driven validation system, pipeline logging, and the Streamlit dashboard, then iterate on the dashboard's Overview, Store Performance, Department Performance, and Trends & External Factors tabs. Codex also helped implement the Ask Store Pulse AI experience and diagnose issues encountered during development rather than only adding features. Those fixes included a blank-render issue caused by missing display calls, an `ImportError` caused by a stale cached module, and a Streamlit Markdown/LaTeX rendering problem in which multiple `$` characters in one string were interpreted as math delimiters. The development process involved inspecting the failing behavior, tracing it to the responsible code or cached state, applying a targeted fix, and re-running the dashboard or pipeline to verify it.

### GPT-5.6 usage (Ask Store Pulse)

The dashboard's fifth tab, Ask Store Pulse, calls GPT-5.6 (`gpt-5.6-terra`) through OpenAI's Responses API to produce an executive summary and answer follow-up questions about the currently filtered sales data. To control cost and latency, it sends the model a pre-aggregated JSON summary—totals, top stores, top departments, and holiday averages—rather than raw sales rows. The feature deliberately includes a `DEMO_MODE` fallback: if `OPENAI_API_KEY` is not set, it returns deterministic, data-grounded responses based on those same real aggregate values instead of making a live API call. The UI displays a visible “Demo mode” caption whenever this fallback is active, so demo output is never represented as live AI output. Adding a real `OPENAI_API_KEY` to `.env` switches the same functions to live GPT-5.6 calls with no code changes.

---

# 📈 Current Progress

- ✅ Extract Pipeline
- ✅ Transform Pipeline
- ✅ Load Pipeline
- ✅ PostgreSQL Integration
- ✅ SQL Schema
- ✅ Dashboard Development
- ✅ Business KPIs
- ✅ Streamlit Web App

---

# 👥 Team

- **Maira Naveed**
- **Muhammad Burhan Ahmed**
- **Khansa Ahmed**

Project: **Store Pulse**

---

# 📄 License

This project is licensed under the MIT License — see LICENSE for details.
