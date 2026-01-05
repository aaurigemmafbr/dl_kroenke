import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Kroenke HTML Table --> CSV", layout="centered")

st.title("Kroenke HTML Table to CSV Converter")

st.markdown(
    """
Open the jotform table. Right click --> Inspect
<br>Locate the data table by expanding the <body> (click the ... between body tags)
<br>Click on the ... on the left side of the table with id "data-table" --> Copy --> Copy Element
<br>Paste the HTML table below
<br>This tool will extract the table and convert it into a downloadable CSV.
"""
)

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

            # --- FILTER LOGIC ---
            column_name = "Donation Amount: Payer Info"

            if column_name in df.columns:
                original_count = len(df)

                df[column_name] = df[column_name].astype(str).str.strip()
                df = df[df[column_name] != "-"]

                removed = original_count - len(df)

                if removed > 0:
                    st.info(f"Removed {removed} row(s) where '{column_name}' was '-'.")

            else:
                st.warning(f"Column '{column_name}' not found. No rows removed.")

            # --- PREVIEW ---
            st.success("Table successfully extracted!")

            st.subheader("Preview")
            st.dataframe(df, use_container_width=True)

            # --- DOWNLOAD ---
            csv_data = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="output.csv",
                mime="text/csv"
            )

            if len(tables) > 1:
                st.info(f"{len(tables)} tables found. Only the first table was used.")

    except Exception as e:
        st.error("Unable to parse HTML. Make sure it contains a valid <table>.")
        st.code(str(e))
