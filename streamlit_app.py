import streamlit as st
import pandas as pd
from io import StringIO
import re
from datetime import datetime

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Kroenke HTML Table → CSV",
    layout="centered"
)

st.title("Kroenke HTML Table to CSV Converter")

st.markdown(
    """
Paste the HTML table copied from Jotform below.

**Steps:**
1. Open the Jotform table  
2. Right-click → Inspect  
3. Expand `<body>` → find the table with id `data-table`  
4. Click `…` → Copy → Copy Element  
5. Paste the HTML below
"""
)

# -------------------------------------------------
# Session state
# -------------------------------------------------
if "final_df" not in st.session_state:
    st.session_state.final_df = None

# -------------------------------------------------
# HTML input
# -------------------------------------------------
html_input = st.text_area(
    "Paste HTML table here:",
    height=300,
    placeholder="<table>...</table>"
)

# -------------------------------------------------
# Date range selectors
# -------------------------------------------------
st.subheader("Filter by Submission Date")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start date",
        value=None,
        format="MM/DD/YYYY"
    )

with col2:
    end_date = st.date_input(
        "End date",
        value=None,
        format="MM/DD/YYYY"
    )

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def parse_submission_date(val):
    """Convert 'YYYY-MM-DD HH:MM:SS' → datetime.date"""
    try:
        return datetime.strptime(val, "%Y-%m-%d %H:%M:%S").date()
    except Exception:
        return None


def parse_payer_info(text):
    """
    Extract:
    First Name
    Middle Initial (only if exactly one letter)
    Last Name
    Email
    Transaction ID
    """
    if pd.isna(text):
        return pd.Series([None, None, None, None, None])

    text = str(text)

    # Full Name
    full_name_match = re.search(r"Full Name:\s*(.*?)\s+Email:", text)
    full_name = full_name_match.group(1).strip() if full_name_match else ""

    parts = full_name.split()

    first_name = None
    middle_initial = None
    last_name = None

    if len(parts) == 1:
        first_name = parts[0]

    elif len(parts) >= 2:
        first_name = parts[0]

        if len(parts[1]) == 1 and parts[1].isalpha():
            middle_initial = parts[1]
            last_name = " ".join(parts[2:]) if len(parts) > 2 else None
        else:
            last_name = " ".join(parts[1:])

    # Email
    email_match = re.search(r"Email:\s*([^\s]+)", text)
    email = email_match.group(1) if email_match else None

    # Transaction ID
    tx_match = re.search(r"Transaction ID:\s*([^\s]+)", text)
    transaction_id = tx_match.group(1) if tx_match else None

    return pd.Series([
        first_name,
        middle_initial,
        last_name,
        email,
        transaction_id
    ])

# -------------------------------------------------
# Main processing
# -------------------------------------------------
if html_input.strip():
    try:
        tables = pd.read_html(StringIO(html_input))

        if not tables:
            st.error("No HTML tables found.")
        else:
            df = tables[0]

            # Parse Submission Date
            df["Parsed Submission Date"] = df["Submission Date"].apply(parse_submission_date)

            # Date filtering
            if start_date:
                df = df[df["Parsed Submission Date"] >= start_date]

            if end_date:
                df = df[df["Parsed Submission Date"] <= end_date]

            # Remove rows with "-" payer info
            payer_col = "Donation Amount: Payer Info"
            if payer_col in df.columns:
                df[payer_col] = df[payer_col].astype(str).str.strip()
                df = df[df[payer_col] != "-"]

            # Parse payer info
            parsed_cols = df[payer_col].apply(parse_payer_info)
            parsed_cols.columns = [
                "First Name",
                "Middle Initial",
                "Last Name",
                "Email",
                "Transaction ID"
            ]

            df = pd.concat([df, parsed_cols], axis=1)

            # Final formatted output
            df["Date"] = df["Parsed Submission Date"].apply(
                lambda d: d.strftime("%m/%d/%Y") if pd.notna(d) else None
            )

            final_df = df[[
                "Date",
                "First Name",
                "Middle Initial",
                "Last Name",
                "Email",
                "Transaction ID",
                "Total Donation Amount"
            ]]

            st.session_state.final_df = final_df

            st.success("Table processed successfully!")
            st.dataframe(final_df, width="stretch")

    except Exception as e:
        st.error("Unable to parse HTML.")
        st.code(str(e))

# -------------------------------------------------
# Download instructions (locked-down safe)
# -------------------------------------------------
if st.session_state.final_df is not None and not st.session_state.final_df.empty:
    st.info(
        "⬇️ To download the CSV, hover over the preview output and click the download icon in the top right corner "
    )
