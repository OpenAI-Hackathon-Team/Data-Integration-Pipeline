"""OpenAI-powered, aggregate-only insights for the Store Pulse dashboard."""

import json
import os
from typing import Any

import pandas as pd
from dotenv import load_dotenv


load_dotenv()
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
DEMO_MODE = not bool(os.getenv("OPENAI_API_KEY"))


SYSTEM_INSTRUCTIONS = """
You are Store Pulse's retail analyst assistant. You have access only to the
pre-aggregated JSON summary supplied in this request, never to raw sales rows.
Answer only from that summary. If the summary does not contain enough detail to
answer a question, say so clearly and explain what additional aggregate would
be needed. Be concise, factual, and use currency formatting where useful.
""".strip()


def _json_scalar(value: Any) -> Any:
    """Convert pandas and NumPy scalar values into JSON-safe Python values."""

    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _ranked_sales(sales_df: pd.DataFrame, column: str, label: str) -> list[dict[str, Any]]:
    """Return the five strongest entities for a grouping column."""

    ranked = (
        sales_df.groupby(column, as_index=False)["weekly_sales"]
        .sum()
        .nlargest(5, "weekly_sales")
    )
    return [
        {label: _json_scalar(row[column]), "total_sales": float(row["weekly_sales"])}
        for _, row in ranked.iterrows()
    ]


def build_data_summary(sales_df: pd.DataFrame) -> dict[str, Any]:
    """Build a small, JSON-safe aggregate for the currently filtered sales slice."""

    sales = sales_df.dropna(subset=["weekly_sales"]).copy()
    if sales.empty:
        return {
            "total_sales": 0.0,
            "date_range": {"start": None, "end": None},
            "average_weekly_sales": 0.0,
            "active_store_count": 0,
            "active_department_count": 0,
            "top_stores": [],
            "top_departments": [],
            "average_weekly_sales_by_week_type": {"holiday": None, "non_holiday": None},
        }

    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    weekly_totals = sales.groupby("date", as_index=False)["weekly_sales"].sum()
    holiday_weekly_totals = (
        sales.assign(isholiday=sales["isholiday"].fillna(False).astype(bool))
        .groupby(["date", "isholiday"], as_index=False)["weekly_sales"]
        .sum()
    )
    holiday_averages = holiday_weekly_totals.groupby("isholiday")["weekly_sales"].mean()

    return {
        "total_sales": float(sales["weekly_sales"].sum()),
        "date_range": {
            "start": sales["date"].min().date().isoformat(),
            "end": sales["date"].max().date().isoformat(),
        },
        "average_weekly_sales": float(weekly_totals["weekly_sales"].mean()),
        "active_store_count": int(sales["store"].nunique()),
        "active_department_count": int(sales["dept"].nunique()),
        "top_stores": _ranked_sales(sales, "store", "store"),
        "top_departments": _ranked_sales(sales, "dept", "department"),
        "average_weekly_sales_by_week_type": {
            "holiday": None if True not in holiday_averages.index else float(holiday_averages[True]),
            "non_holiday": None if False not in holiday_averages.index else float(holiday_averages[False]),
        },
    }


def _get_client():
    """Create an authenticated Responses API client or raise a clear setup error."""

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your environment or .env file to use Ask Store Pulse.")

    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("The OpenAI SDK is not installed. Run `pip install -r requirements.txt` and restart the app.") from error

    return OpenAI(api_key=api_key)


def _create_response(instructions: str, prompt: str, model: str) -> str:
    """Send a text request that contains only the pre-aggregated data summary."""

    response = _get_client().responses.create(model=model, instructions=instructions, input=prompt)
    return response.output_text


def _escape_dollar_signs(text: str) -> str:
    """Escape literal $ so Streamlit's Markdown renderer doesn't treat pairs
    of them as LaTeX math delimiters."""

    return text.replace("$", "\\$")


def _leader(data_summary: dict[str, Any], collection: str, label: str) -> str:
    """Format the top entity in a summary collection for demo-mode copy."""

    entries = data_summary.get(collection, [])
    if not entries:
        return f"No {label.lower()} ranking is available for this selection"

    leader = entries[0]
    return f"{label} {leader[label.lower()]} leads with ${leader['total_sales']:,.0f}"


def _holiday_comparison(data_summary: dict[str, Any]) -> str:
    """Describe the holiday-week comparison when both averages are available."""

    averages = data_summary.get("average_weekly_sales_by_week_type", {})
    holiday, non_holiday = averages.get("holiday"), averages.get("non_holiday")
    if holiday is None or non_holiday is None:
        return "Holiday-week comparison is unavailable for the current selection"

    difference = holiday - non_holiday
    direction = "higher" if difference >= 0 else "lower"
    return (
        f"Holiday weeks averaged ${holiday:,.0f}, which is ${abs(difference):,.0f} "
        f"{direction} than the ${non_holiday:,.0f} non-holiday average"
    )


def _demo_summary(data_summary: dict[str, Any]) -> str:
    """Create a deterministic executive summary from the aggregate data."""

    date_range = data_summary.get("date_range", {})
    headline = (
        f"Across {data_summary.get('active_store_count', 0):,} active stores and "
        f"{data_summary.get('active_department_count', 0):,} departments from "
        f"{date_range.get('start') or 'the selected start date'} to "
        f"{date_range.get('end') or 'the selected end date'}, total sales reached "
        f"${data_summary.get('total_sales', 0):,.0f}, averaging "
        f"${data_summary.get('average_weekly_sales', 0):,.0f} per week."
    )
    leaders = f"{_leader(data_summary, 'top_stores', 'Store')}; {_leader(data_summary, 'top_departments', 'Department')}."
    return f"{headline} {leaders} {_holiday_comparison(data_summary)}."


def _demo_answer(question: str, data_summary: dict[str, Any]) -> str:
    """Return a deterministic, data-grounded response for an offline demo."""

    normalized_question = question.lower()
    if "holiday" in normalized_question:
        return f"For the current filters, {_holiday_comparison(data_summary)}."
    if "department" in normalized_question or "dept" in normalized_question:
        return f"For the current filters, {_leader(data_summary, 'top_departments', 'Department')} across {data_summary.get('active_department_count', 0):,} active departments."
    if "store" in normalized_question:
        return f"For the current filters, {_leader(data_summary, 'top_stores', 'Store')} across {data_summary.get('active_store_count', 0):,} active stores."
    return (
        f"The filtered selection totals ${data_summary.get('total_sales', 0):,.0f} and averages "
        f"${data_summary.get('average_weekly_sales', 0):,.0f} per week. "
        f"{_leader(data_summary, 'top_stores', 'Store')}; {_leader(data_summary, 'top_departments', 'Department')}."
    )


def generate_summary(data_summary: dict[str, Any], model: str = DEFAULT_MODEL) -> str:
    """Generate a concise executive summary from aggregate sales data."""

    if DEMO_MODE:
        return _escape_dollar_signs(_demo_summary(data_summary))

    prompt = (
        "Write a 3-5 sentence executive summary. Highlight the headline total, "
        "the strongest stores and departments, and anything notable about holiday weeks.\n\n"
        f"Pre-aggregated Store Pulse summary:\n{json.dumps(data_summary, ensure_ascii=False)}"
    )
    return _escape_dollar_signs(_create_response(SYSTEM_INSTRUCTIONS, prompt, model))


def answer_question(question: str, data_summary: dict[str, Any], model: str = DEFAULT_MODEL) -> str:
    """Answer one user question using only the supplied aggregate sales data."""

    if DEMO_MODE:
        return _escape_dollar_signs(_demo_answer(question, data_summary))

    prompt = (
        f"Pre-aggregated Store Pulse summary:\n{json.dumps(data_summary, ensure_ascii=False)}\n\n"
        f"User question: {question}"
    )
    return _escape_dollar_signs(_create_response(SYSTEM_INSTRUCTIONS, prompt, model))