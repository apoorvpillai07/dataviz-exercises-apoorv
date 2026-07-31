# utils.py — Shared data loading functionality (imported by every page)
import plotly.express as px
import streamlit as st


@st.cache_data
def load_gapminder():
    # Plotly built-in gapminder dataset: country, continent, year, lifeExp, pop, gdpPercap
    return px.data.gapminder()
