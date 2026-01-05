import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Kroenke HTML Table --> CSV", layout="centered")

st.title("Kroenke HTML Table to CSV Converter")

st.markdown(
    """
Open the jotform table. Right click --> Inspect  
Locate the data table by expanding the <body> (click the ... between body tags)  
Click on the ... on the left side of the table with id "data-table" --> Copy --> Copy Element  
Paste the HTML table below  
This tool will extract the table and convert it into a downloadable CSV.
"""
)

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None

html_input = st.text_area(
    "Paste HTML here:",
    height=300,
    placeholder="<table>...</table>"
)

if html_input.strip():
    try:
        tables = pd.read_html(StringIO(html_input))

        if not tables:
            st.error("No HTML tables were found.")
        else:
            df = tables[0]

            column_name = "Donation Amount: Payer Info"
            if column_name in df.columns:
                df[column_name] = df[column_name].astype(str).str.strip()
                df = df[df[column_name] != "-"]

            st.session_state.df = df  # ✅ persist it

            st.success("Table successfully extracted!")
            st.dataframe(df, width="stretch")

    except Exception as e:
        st.error("Unable to parse HTML.")
        st.code(str(e))

# --- DOWNLOAD ---
if st.session_state.df is not None and not st.session_state.df.empty:
    import base64

    csv_bytes = st.session_state.df.to_csv(index=False).encode("utf-8")
    b64 = base64.b64encode(csv_bytes).decode()

    st.markdown(
        f"""
        <a href="data:file/csv;base64,{b64}" download="output.csv">
            ⬇️ Download CSV
        </a>
        """,
        unsafe_allow_html=True
    )
