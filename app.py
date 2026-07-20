"""Store Pulse retail analytics dashboard.

Run with: streamlit run app.py
"""

import os

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


st.set_page_config(
    page_title="Store Pulse",
    page_icon=":material/monitoring:",
    layout="wide",
)


@st.cache_resource
def get_engine():
    """Build the database connection from the project's .env configuration."""

    load_dotenv()
    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing database settings: {', '.join(missing)}")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=300, show_spinner="Loading sales data…")
def load_sales_data():
    """Load the dashboard fields; refresh the cache every five minutes."""

    query = text("""
        SELECT store, dept, date, weekly_sales, isholiday, type, size,
               temperature, fuel_price, cpi, unemployment
        FROM clean_sales
    """)
    with get_engine().connect() as connection:
        data = pd.read_sql(query, connection)

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["weekly_sales"] = pd.to_numeric(data["weekly_sales"], errors="coerce")
    return data


def currency(value: float) -> str:
    return f"${value:,.0f}"


def build_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar controls and return the selected data slice."""

    sales = data.dropna(subset=["weekly_sales"]).copy()
    if sales.empty:
        return sales

    with st.sidebar:
        st.title("Store Pulse")
        st.caption("Retail sales intelligence")
        st.subheader("Filters")

        date_min, date_max = sales["date"].min().date(), sales["date"].max().date()
        selected_dates = st.date_input(
            "Date range",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max,
        )
        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])
            sales = sales[sales["date"].between(start_date, end_date)]

        stores = sorted(sales["store"].dropna().unique().tolist())
        selected_stores = st.multiselect("Stores", stores, default=stores)
        if selected_stores:
            sales = sales[sales["store"].isin(selected_stores)]
        else:
            sales = sales.iloc[0:0]

        departments = sorted(sales["dept"].dropna().unique().tolist())
        selected_departments = st.multiselect("Departments", departments, default=departments)
        if selected_departments:
            sales = sales[sales["dept"].isin(selected_departments)]
        else:
            sales = sales.iloc[0:0]

        holiday_only = st.toggle("Holiday weeks only")
        if holiday_only:
            sales = sales[sales["isholiday"].fillna(False)]

        st.caption("Filters apply to every KPI and chart.")
    return sales


def show_dashboard(data: pd.DataFrame) -> None:
    sales = build_filters(data)
    if sales.empty:
        st.warning("No sales records match the selected filters.")
        return

    total_sales = sales["weekly_sales"].sum()
    sales_rows = len(sales)
    weekly_sales = sales.groupby("date", as_index=False)["weekly_sales"].sum()
    average_weekly_sales = weekly_sales["weekly_sales"].mean()
    active_stores = sales["store"].nunique()

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.title("Sales performance")
        st.badge("Live database view", icon=":material/database:", color="blue")
    st.caption(
        f"{sales['date'].min():%b %d, %Y} – {sales['date'].max():%b %d, %Y}  ·  "
        "Updated from `clean_sales`"
    )

    with st.container(horizontal=True):
        st.metric("Total sales", currency(total_sales), border=True)
        st.metric("Average weekly sales", currency(average_weekly_sales), border=True)
        st.metric("Active stores", f"{active_stores:,}", border=True)
        st.metric("Sales records", f"{sales_rows:,}", border=True)

    time_chart = (
        alt.Chart(weekly_sales)
        .mark_area(
            line={"color": "#60A5FA"},
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="#60A5FA", offset=0), alt.GradientStop(color="#0F172A", offset=1)],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
        )
        .encode(
            x=alt.X("date:T", title="Week"),
            y=alt.Y("weekly_sales:Q", title="Weekly sales", axis=alt.Axis(format="$,.0f")),
            tooltip=[alt.Tooltip("date:T", title="Week"), alt.Tooltip("weekly_sales:Q", title="Sales", format="$,.2f")],
        )
        .properties(height=330)
    )
    with st.container(border=True):
        st.subheader("Sales over time")
        st.caption("Weekly sales volume across the selected stores and departments")
        st.altair_chart(time_chart, width="stretch")

    left, right = st.columns(2)
    store_sales = (
        sales.groupby("store", as_index=False)["weekly_sales"].sum()
        .nlargest(10, "weekly_sales")
        .sort_values("weekly_sales")
    )
    dept_sales = (
        sales.groupby("dept", as_index=False)["weekly_sales"].sum()
        .nlargest(10, "weekly_sales")
        .sort_values("weekly_sales")
    )
    with left:
        with st.container(border=True):
            st.subheader("Top stores")
            st.caption("Top 10 by total sales")
            st.bar_chart(store_sales.set_index("store"), y="weekly_sales", color="#60A5FA", height=310)
    with right:
        with st.container(border=True):
            st.subheader("Top departments")
            st.caption("Top 10 by total sales")
            st.bar_chart(dept_sales.set_index("dept"), y="weekly_sales", color="#34D399", height=310)

    with st.expander("View and export filtered records", icon=":material/table_chart:"):
        st.dataframe(
            sales.sort_values("date", ascending=False),
            width="stretch",
            height=360,
            hide_index=True,
        )
        st.download_button(
            "Download filtered data as CSV",
            data=sales.to_csv(index=False).encode("utf-8"),
            file_name="store_pulse_filtered_sales.csv",
            mime="text/csv",
        )


try:
    sales_data = load_sales_data()
    show_dashboard(sales_data)
except Exception as error:
    st.error("The dashboard could not load data from PostgreSQL.")
    st.exception(error)
    st.info("Check that `.env` has valid DB_* values and that the ETL has created `clean_sales`.")
