# app.py — Multi-page Streamlit Dashboard entry point
import streamlit as st

st.set_page_config(page_title="Gapminder Dashboard", layout="wide")

pg = st.navigation([
    st.Page("pages/01_overview.py", title="How do countries compare today?"),
    st.Page("pages/02_trends.py", title="How has life expectancy changed?"),
    st.Page("pages/03_compare.py", title="What explains the differences?"),
])

pg.run()
