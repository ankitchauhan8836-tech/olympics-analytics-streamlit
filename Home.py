import plotly.express as px
import streamlit as st

from utils import analysis as an
from utils.constants import MEDAL_COLORS, MEDALS
from utils.data import load_data
from utils.ui import highlight_card, rings, setup_page, short_name, show

setup_page("Olympics Analytics", "🏅", show_title=False)
df = load_data()

st.markdown(
    f'<div class="hero">{rings()}<h1>Olympics Analytics</h1>'
    "<p>120 years of Summer Games: explore medals, athletes and countries, "
    "then try two machine-learning tools built on the data.</p></div>",
    unsafe_allow_html=True,
)

# --- headline numbers -------------------------------------------------------
cols = st.columns(6)
stats = [
    ("Editions", df["Year"].nunique() - 1),  # -1: the 1906 Intercalated Games are not official
    ("Host cities", df["City"].nunique()),
    ("Sports", df["Sport"].nunique()),
    ("Events", df["Event"].nunique()),
    ("Nations", df["region"].nunique()),
    ("Athletes", df["ID"].nunique()),
]
for col, (label, value) in zip(cols, stats):
    col.metric(label, f"{value:,}")

# --- highlights -------------------------------------------------------------
tally = an.fetch_medal_tally(df)
star = an.most_successful(df, n=1).iloc[0]
medals = an.medal_events(df).dropna(subset=["Age"])
young = medals.sort_values("Age").iloc[0]
old = medals.sort_values("Age").iloc[-1]

st.subheader("Highlights")
h = st.columns(4)
with h[0]:
    highlight_card("Most medals (all-time)", tally.iloc[0]["region"], f"{tally.iloc[0]['Total']:,} medals")
with h[1]:
    highlight_card("Most decorated athlete", short_name(star["Name"]), f"{star['Medals']} medals · {star['Sport']}")
with h[2]:
    highlight_card("Youngest medalist", short_name(young["Name"]), f"{int(young['Age'])} yrs · {young['Sport']} {young['Year']}")
with h[3]:
    highlight_card("Oldest medalist", short_name(old["Name"]), f"{int(old['Age'])} yrs · {old['Sport']} {old['Year']}")

top = tally.head(10).melt(id_vars="region", value_vars=MEDALS, var_name="Medal", value_name="Count")
fig = px.bar(top, x="region", y="Count", color="Medal", color_discrete_map=MEDAL_COLORS,
             category_orders={"Medal": MEDALS}, title="All-time medal table: top 10 nations")
fig.update_layout(xaxis_title=None)
show(fig, 380)

# --- navigation -------------------------------------------------------------
st.subheader("Explore")
pages = [
    ("pages/1_Medal_Tally.py", "Medal Tally", "🏅", "Filter by edition and country"),
    ("pages/2_Overall_Analysis.py", "Overall Analysis", "📈", "Growth of the Games, top athletes"),
    ("pages/3_Country_Analysis.py", "Country Analysis", "🌍", "One nation's story over time"),
    ("pages/4_Athlete_Analysis.py", "Athlete Analysis", "🏃", "Age, body size and gender"),
    ("pages/5_World_Map.py", "World Map", "🗺️", "Animated medal choropleth"),
    ("pages/6_Country_vs_Country.py", "Country vs Country", "⚔️", "Head-to-head comparison"),
    ("pages/7_Host_Advantage.py", "Host Advantage", "🏟️", "Do hosts really win more?"),
    ("pages/8_Sport_Matcher.py", "Sport Matcher (ML)", "🤖", "Which sport fits your body?"),
    ("pages/9_Medal_Predictor.py", "Medal Predictor (ML)", "🔮", "Forecast medals per country"),
]
grid = st.columns(3)
for i, (path, label, icon, desc) in enumerate(pages):
    with grid[i % 3]:
        st.page_link(path, label=label, icon=icon, help=desc)
        st.caption(desc)
