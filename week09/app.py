#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecture 9 Exercise — Streamlit Dashboard with Diverging Colour Scale & Midpoint Annotation
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page configuration
st.set_page_config(
    page_title="World Happiness Dashboard",
    page_icon="🌍",
    layout="wide"
)

# 2. Robust data loading (supports local execution and Streamlit Community Cloud deployment)
@st.cache_data
def load_data():
    local_path = '../data/world_happiness_2023.csv'
    local_path_alt = 'data/world_happiness_2023.csv'
    github_url = 'https://raw.githubusercontent.com/apoorvpillai07/dataviz-exercises-apoorv/main/data/world_happiness_2023.csv'
    
    if os.path.exists(local_path):
        df = pd.read_csv(local_path)
    elif os.path.exists(local_path_alt):
        df = pd.read_csv(local_path_alt)
    else:
        df = pd.read_csv(github_url)
        
    df.columns = [
        'Country', 'Region', 'Score', 'GDP', 'Social_Support',
        'Life_Expectancy', 'Freedom', 'Generosity', 'Corruption'
    ]
    return df

df = load_data()
global_mean = df['Score'].mean()

# 3. Sidebar filters and controls
with st.sidebar:
    st.header("Filters & Controls")
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show Top N Countries", 5, 25, 15)
    
    st.markdown("---")
    st.markdown("### BBD Design Highlights")
    st.caption("✅ **5-Second Summary**: KPI row at the top for rapid monitoring.\n\n✅ **Deliberate Color Usage**: Sequential blue for rankings, categorical color for scatter, and **diverging RdBu** centered at global mean for departure analysis.")

filtered = df if selected_region == 'All' else df[df['Region'] == selected_region]

# 4. Dashboard Header
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Built with Streamlit & Plotly")

# 5. KPI Row — BBD: big numbers at the top, readable in 5 seconds
col1, col2, col3 = st.columns(3)
col1.metric("Countries Analyzed", len(filtered))
col2.metric(
    "Average Score",
    f"{filtered['Score'].mean():.2f}",
    f"{filtered['Score'].mean() - global_mean:+.2f} vs Global Avg"
)
col3.metric("Happiest Country", filtered.nlargest(1, 'Score')['Country'].values[0])

st.divider()

# 6. Two-column layout for standard charts (Step 4 from lecture)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 Rankings")
    top = filtered.nlargest(top_n, 'Score').sort_values('Score')
    
    fig1 = px.bar(
        top, x='Score', y='Country', orientation='h',
        color_discrete_sequence=['#2E75B6'],
        labels={'Score': 'Score (0–10)', 'Country': ''}
    )
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(range=[0, 8.5], gridcolor='#EEEEEE'),
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("💰 Score vs GDP")
    fig2 = px.scatter(
        filtered, x='GDP', y='Score', hover_name='Country',
        color_discrete_sequence=['#E63946'],
        labels={'GDP': 'GDP per Capita (Log)', 'Score': 'Score (0–10)'}
    )
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(gridcolor='#EEEEEE'),
        yaxis=dict(gridcolor='#EEEEEE'),
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# 7. STEP 6: Exercise — Third chart with DIVERGING colour scale & Midpoint Annotation
st.subheader("⚖️ Happiness Score Departure from Global Average")
st.markdown(
    f"This visualization uses a **diverging colour scale (`RdBu`)** centered at **0.00** (representing the global average happiness score of **{global_mean:.2f}**). "
    "Countries plotted in **blue** exceed the global average, while countries in **red** fall below the global average."
)

# Compute departure from global average happiness score
filtered['Score_Diff'] = filtered['Score'] - global_mean

# To prevent visual crowding when 'All' regions are selected, highlight the top and bottom departures
if len(filtered) > 30:
    subset = pd.concat([
        filtered.nlargest(15, 'Score_Diff'),
        filtered.nsmallest(15, 'Score_Diff')
    ]).drop_duplicates().sort_values(by='Score_Diff', ascending=True)
else:
    subset = filtered.sort_values(by='Score_Diff', ascending=True)

fig3 = px.bar(
    subset,
    x='Score_Diff',
    y='Country',
    orientation='h',
    color='Score_Diff',
    color_continuous_scale='RdBu',
    color_continuous_midpoint=0,
    hover_name='Country',
    hover_data={'Score': ':.2f', 'Score_Diff': ':.2f', 'Country': False},
    labels={
        'Score_Diff': f'Difference vs Global Avg ({global_mean:.2f})',
        'Country': ''
    },
    height=max(450, len(subset) * 24)
)

# Add dashed midpoint reference line
fig3.add_vline(
    x=0,
    line_dash="dash",
    line_color="#444444",
    line_width=1.5
)

# Add explicit midpoint annotation as required by STEP 6
fig3.add_annotation(
    x=0,
    y=1.03,
    yref="paper",
    text=f"📍 Midpoint Reference: Global Average ({global_mean:.2f})",
    showarrow=False,
    font=dict(size=12, color="#111111", family="Arial"),
    bgcolor="rgba(245, 245, 245, 0.95)",
    bordercolor="#888888",
    borderwidth=1,
    yanchor="bottom"
)

fig3.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    xaxis=dict(gridcolor='#EEEEEE', zeroline=False),
    coloraxis_colorbar=dict(title="vs Global Avg", thickness=15, len=0.75),
    margin=dict(l=10, r=10, t=55, b=10)
)
fig3.update_traces(marker_line_width=0)

st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.caption("🚀 Designed & Deployed for Week 09 Data Visualization | Streamlit Community Cloud Ready")
