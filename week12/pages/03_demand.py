# pages/03_demand.py — Demand Drill-Down Page (BBD Squiggle Level 3)
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters

# ─────────────────────────────────────────────────────────────────────────────
# Load data + shared sidebar (inherits persistent filtering automatically)
# ─────────────────────────────────────────────────────────────────────────────
df, p95 = load_data()
filtered = sidebar_filters(df, p95)

st.title("Where is guest demand strongest?")
st.caption("BBD squiggle level 3: drilling into guest demand intensity using monthly review frequency as a proxy.")

# ─────────────────────────────────────────────────────────────────────────────
# Persisted custom widget with session_state keep-alive and guard protection
# ─────────────────────────────────────────────────────────────────────────────
rooms_avail = sorted(filtered['room_type'].unique())
if 'sel_room' not in st.session_state:
    st.session_state.sel_room = rooms_avail[0]
st.session_state.sel_room = st.session_state.sel_room  # Keep alive across page navigation

if st.session_state.sel_room not in rooms_avail:       # Guard if sidebar filters remove saved option
    st.session_state.sel_room = rooms_avail[0]

st.selectbox("Focus on a room type", rooms_avail, key="sel_room")
room = st.session_state.sel_room
room_df = filtered[filtered['room_type'] == room]

# ─────────────────────────────────────────────────────────────────────────────
# 5-Second Test KPI row focused on selected room type demand metrics
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
k1.metric("Listings in Category", f"{len(room_df):,}", f"{len(room_df) - len(filtered):+,} vs filtered total")
k2.metric("Median Reviews / Month", f"{room_df['reviews_per_month'].median():.2f}",
          f"{room_df['reviews_per_month'].median() - filtered['reviews_per_month'].median():+.2f} vs market median")
k3.metric("Median Price", f"£{room_df['price'].median():.0f}/night",
          f"£{room_df['price'].median() - filtered['price'].median():+.0f} vs market median")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# BBD / SWD / Plotly Express compliant demand analysis scatter chart
# ─────────────────────────────────────────────────────────────────────────────
plot_df = filtered.copy()
plot_df['highlight'] = plot_df['room_type'].apply(lambda r: room if r == room else 'Other room types')

# BBD HIGHLIGHT colour type: saturated blue for focused room category, neutral grey for comparison context.
# BBD CVD safety: blue vs grey contrast ensures clear legibility for color-vision deficiencies.
fig = px.scatter(
    plot_df, x='price', y='reviews_per_month', color='highlight',
    color_discrete_map={room: '#2E75B6', 'Other room types': '#AAAAAA'},
    category_orders={'highlight': ['Other room types', room]},  # Plots highlighted series on top
    opacity=0.75,
    labels={'price': 'Nightly Price (£)', 'reviews_per_month': 'Reviews per Month (Demand Proxy)', 'highlight': 'Category'},
    title=f"Guest demand peaks below £150/night — activity distribution for {room}"
)
fig.update_traces(marker=dict(size=7, line=dict(width=0)))
fig.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    xaxis=dict(gridcolor='#EEEEEE'),
    yaxis=dict(gridcolor='#EEEEEE'),
    legend=dict(orientation='h', y=1.08)
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Show demand data sample"):
    st.dataframe(room_df.head(100), use_container_width=True)
