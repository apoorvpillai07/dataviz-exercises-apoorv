import streamlit as st
import plotly.express as px
import math
import sys, os

# Ensure project root is on Python's import path to locate utils.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_gapminder

df = load_gapminder()
df_latest = df[df['year'] == df['year'].max()].copy()

st.header("What explains the differences?")
st.caption("BBD squiggle methodology: drill down from high-level summary to individual country stories.")

# st.session_state persists the selected country across reruns AND across tabs/pages
if 'highlight_country' not in st.session_state:
    st.session_state.highlight_country = 'China'

countries = sorted(df_latest['country'].unique())
st.session_state.highlight_country = st.selectbox(
    "Highlight a country", countries,
    index=countries.index(st.session_state.highlight_country)
)
h = st.session_state.highlight_country
h_continent = df_latest[df_latest['country'] == h]['continent'].values[0]

tab1, tab2 = st.tabs(["GDP vs Life Expectancy", "Continent comparison"])

with tab1:
    # BBD HIGHLIGHT colour type: bold saturated blue for the selected series of interest, neutral grey for all background points.
    df_plot = df_latest.copy()
    df_plot['highlight'] = df_plot['country'].apply(lambda c: 'Selected' if c == h else 'Other')

    fig1 = px.scatter(
        df_plot, x='gdpPercap', y='lifeExp', color='highlight', log_x=True,
        color_discrete_map={'Selected': '#2E75B6', 'Other': '#AAAAAA'},
        category_orders={'highlight': ['Other', 'Selected']},
        hover_name='country',
        labels={'gdpPercap': 'GDP per Capita (log)', 'lifeExp': 'Life Expectancy (yrs)'}, height=600
    )
    fig1.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=0)))

    h_row = df_plot[df_plot['country'] == h]
    fig1.add_annotation(
        x=math.log10(h_row['gdpPercap'].values[0]),
        y=h_row['lifeExp'].values[0],
        text=f'<b>{h}</b>', showarrow=True, arrowhead=1, ax=40, ay=-30,
        font=dict(color='#2E75B6', size=11, family='Arial')
    )
    fig1.update_xaxes(gridcolor='#EEEEEE')
    fig1.update_yaxes(gridcolor='#EEEEEE')
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial', size=12), showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    # BBD HIGHLIGHT colour type: bold blue bar for highlighted country, neutral grey bars for regional peers.
    continent_df = (df_latest[df_latest['continent'] == h_continent]
                    .sort_values('lifeExp').copy())
    continent_df['highlight'] = continent_df['country'].apply(lambda c: 'Selected' if c == h else 'Peer')

    fig2 = px.bar(
        continent_df, x='lifeExp', y='country', orientation='h', color='highlight',
        color_discrete_map={'Selected': '#2E75B6', 'Peer': '#AAAAAA'},
        category_orders={'country': continent_df['country'].tolist()},
        labels={'lifeExp': 'Life Expectancy (yrs)', 'country': ''},
        title=f'{h} vs {h_continent} peers — life expectancy in {df_latest["year"].max()}', height=1000
    )
    fig2.update_traces(marker_line_width=0)
    fig2.update_xaxes(gridcolor='#EEEEEE', range=[0, continent_df['lifeExp'].max() * 1.1])
    fig2.update_yaxes(showgrid=False)
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial', size=12), showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)
