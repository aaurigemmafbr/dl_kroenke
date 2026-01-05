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

            st.success("Table successfully extracted!")

            st.subheader("Preview")
            st.dataframe(df, use_container_width=True)

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
