import plotly.express as px
import streamlit as st

from utils import analysis as an
from utils.data import load_data
from utils.ui import setup_page, show, table

setup_page("World Map", "🗺️", "Where in the world are Olympic medals won?")
df = load_data()

metric = st.sidebar.radio("Colour by", ["Total", "Gold", "Silver", "Bronze"])
animate = st.sidebar.checkbox("Animate through every edition", value=False)

if animate:
    data = an.world_map_animation(df)
    fig = px.choropleth(data, locations="iso", color=metric, hover_name="Country",
                        animation_frame="Year", color_continuous_scale="YlOrRd",
                        range_color=(0, float(data[metric].max())), projection="natural earth")
    fig.update_layout(title=f"{metric} medals by edition")
    show(fig, 560)
else:
    years, _ = an.country_year_list(df)
    year = st.sidebar.selectbox("Edition", years)
    data = an.world_map_data(df, year)
    fig = px.choropleth(data, locations="iso", color=metric, hover_name="Country",
                        hover_data=["Gold", "Silver", "Bronze", "Total"],
                        color_continuous_scale="YlOrRd", projection="natural earth")
    fig.update_layout(title=f"{metric} medals: {'all editions' if year == 'Overall' else year}")
    show(fig, 560)
    st.subheader("Top 10")
    table(data.sort_values(metric, ascending=False).head(10)[["Country", "Gold", "Silver", "Bronze", "Total"]])

st.caption("Historical teams (USSR, East/West Germany, Yugoslavia, Czechoslovakia…) are folded into "
           "their modern successor so the map stays continuous.")
