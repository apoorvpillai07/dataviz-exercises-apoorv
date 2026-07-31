#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecture 10 Exercise — Streamlit CO2 Explorer with Chained Filters, KPI Row, and SWD/BBD Design
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page config (Emoji-free and clean professional aesthetic)
st.set_page_config(page_title="CO2 Dashboard", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    local_path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    github_url = 'https://raw.githubusercontent.com/apoorvpillai07/dataviz-exercises-apoorv/main/data/co2_emissions.csv'
    try:
        if local_path.exists():
            df = pd.read_csv(local_path)
        else:
            df = pd.read_csv(github_url)
    except Exception:
        df = pd.read_csv(github_url)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("CO2 Emissions Explorer")
st.caption("Source: Our World in Data | ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    
    # a) st.selectbox for Region (with 'All')
    regions = ['All'] + sorted(df['Region'].dropna().unique().tolist())
    selected_region = st.selectbox("Region", regions)
    
    # b) st.multiselect for Countries (chained to selected region)
    if selected_region == 'All':
        country_options = sorted(df['Country'].dropna().unique().tolist())
    else:
        country_options = sorted(df[df['Region'] == selected_region]['Country'].dropna().unique().tolist())
    
    default_selection = country_options[:5] if len(country_options) >= 5 else country_options
    selected_countries = st.multiselect("Countries", country_options, default=default_selection)
    
    # Guard: empty countries
    if not selected_countries:
        st.warning("Please select at least one country to view analysis.")
        st.stop()
        
    # c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    default_start = pd.to_datetime('2000-01-01').date() if pd.to_datetime('2000-01-01').date() >= min_date else min_date
    
    date_range = st.date_input(
        "Date Range",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Guard: incomplete date_input
    if not isinstance(date_range, (tuple, list)) or len(date_range) < 2:
        st.warning("Please select both a start and end date on the calendar.")
        st.stop()
        
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    
    st.divider()
    # d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])
    
    # e) st.checkbox labelled "Show only top emitter highlighted"
    highlight_top = st.checkbox("Show only top emitter highlighted", value=False)
    
    st.markdown("---")
    st.caption("Designed following SWD grey-and-highlight guidelines and BBD filter visibility rules.")

# Apply all filters to create filtered dataframe
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_date) &
    (df['Date'] <= end_date)
]

if filtered.empty:
    st.warning("No emission records found for the selected countries and timeframe.")
    st.stop()

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'Total CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 Emissions per Capita'

# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# BBD rule: always show users how many records match current filters
st.caption(f"Active Filters Summary: {len(selected_countries)} countries selected | Region: {selected_region} | Date Range: {start_date.strftime('%Y')}–{end_date.strftime('%Y')} | Metric: {metric} ({len(filtered)} records matching)")

# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
last_year_in_range = filtered['Year'].max()
first_year_in_range = filtered['Year'].min()

latest_data = filtered[filtered['Year'] == last_year_in_range]
first_data = filtered[filtered['Year'] == first_year_in_range]

total_last_year = latest_data[y_col].sum()
total_first_year = first_data[y_col].sum()

pct_change = ((total_last_year - total_first_year) / total_first_year * 100) if total_first_year != 0 else 0.0

top_emitter_row = latest_data.nlargest(1, y_col)
top_emitter_name = top_emitter_row['Country'].values[0] if not top_emitter_row.empty else "N/A"
top_emitter_val = top_emitter_row[y_col].values[0] if not top_emitter_row.empty else 0.0

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric(f"Total Selected ({last_year_in_range})", f"{total_last_year:,.1f}", f"{pct_change:+.1f}% vs {first_year_in_range}")
col_kpi2.metric("Analysis Period", f"{first_year_in_range} to {last_year_in_range}", f"{last_year_in_range - first_year_in_range} years span", delta_color="off")
col_kpi3.metric(f"Top Emitter ({last_year_in_range})", top_emitter_name, f"{top_emitter_val:,.2f}")

st.divider()

# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Emissions Trajectory Over Time")
    
    # Find overall highest emitter across the timeframe to highlight
    top_emitter_overall = filtered.groupby('Country')[y_col].max().idxmax()
    
    # BBD colour requirement: HIGHLIGHT colour type (monochrome neutral grey background with single saturated blue focus) when checkbox is checked; CATEGORICAL palette otherwise.
    if highlight_top:
        color_map = {c: ('#D3D3D3' if c != top_emitter_overall else '#1F77B4') for c in selected_countries}
        chart_title = f"{top_emitter_overall} leads emissions among selected countries ({start_date.year}–{end_date.year})"
    else:
        color_map = None
        chart_title = f"{metric} trajectory comparison ({start_date.year}–{end_date.year})"
        
    fig1 = px.line(
        filtered, x='Year', y=y_col, color='Country',
        color_discrete_map=color_map if highlight_top else None,
        color_discrete_sequence=px.colors.qualitative.G10 if not highlight_top else None,
        labels={y_col: y_label, 'Year': 'Year'},
        title=chart_title
    )
    
    # SWD grey-and-highlight styling and line-end labeling
    if highlight_top:
        for trace in fig1.data:
            if trace.name == top_emitter_overall:
                trace.line.width = 3.5
                trace.opacity = 1.0
            else:
                trace.line.width = 1.5
                trace.opacity = 0.55
                
        # SWD guideline: Label highlighted line directly at the end of the trajectory
        top_df = filtered[filtered['Country'] == top_emitter_overall].sort_values('Year')
        if not top_df.empty:
            last_pt = top_df.iloc[-1]
            fig1.add_annotation(
                x=last_pt['Year'],
                y=last_pt[y_col],
                text=f"  <b>{top_emitter_overall}</b>",
                showarrow=False,
                xanchor="left",
                yanchor="middle",
                font=dict(color="#1F77B4", size=13, family="Arial")
            )
        fig1.update_layout(showlegend=False)
    else:
        for trace in fig1.data:
            trace.line.width = 2.5
            
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        xaxis=dict(gridcolor='#EEEEEE', showline=True, linecolor='#CCCCCC'),
        yaxis=dict(gridcolor='#EEEEEE', showline=True, linecolor='#CCCCCC'),
        margin=dict(l=10, r=50 if highlight_top else 10, t=40, b=10)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader(f"Rankings in {last_year_in_range}")
    
    latest_ranking = filtered[filtered['Year'] == last_year_in_range].sort_values(y_col, ascending=True)
    
    # BBD colour requirement: SEQUENTIAL single-color bar chart (monochrome blue #2E75B6) since bars represent quantitative sorted magnitudes without separate categorical meaning.
    fig2 = px.bar(
        latest_ranking, x=y_col, y='Country', orientation='h',
        color_discrete_sequence=['#2E75B6'],
        labels={y_col: y_label, 'Country': ''},
        title=f"Latest Year Ranking ({last_year_in_range})"
    )
    
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        xaxis=dict(gridcolor='#EEEEEE', range=[0, latest_ranking[y_col].max() * 1.15] if not latest_ranking.empty and latest_ranking[y_col].max() > 0 else None),
        margin=dict(l=10, r=10, t=40, b=10)
    )
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.caption("Week 10 CO2 Emissions Dashboard | Designed with Streamlit & Plotly")
