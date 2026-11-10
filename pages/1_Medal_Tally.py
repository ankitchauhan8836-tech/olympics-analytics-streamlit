import plotly.express as px
import streamlit as st

from utils import analysis as an
from utils.constants import MEDAL_COLORS, MEDALS
from utils.data import load_data
from utils.ui import setup_page, show, table

setup_page("Medal Tally", "🏅", "Team events count as one medal, not one per athlete.")
df = load_data()

years, countries = an.country_year_list(df)
year = st.sidebar.selectbox("Edition", years)
country = st.sidebar.selectbox("Country", countries)
tally = an.fetch_medal_tally(df, year, country)

if year == "Overall" and country == "Overall":
    st.subheader("Overall medal table")
elif country == "Overall":
    st.subheader(f"Medal table: {year} Games")
elif year == "Overall":
    st.subheader(f"{country}: medals by edition")
else:
    st.subheader(f"{country} at the {year} Games")

if tally.empty or tally["Total"].sum() == 0:
    st.info("No medals for this selection.")
    st.stop()

if len(tally) == 1:  # one country, one edition
    r = tally.iloc[0]
    c = st.columns(4)
    for col, name in zip(c, MEDALS + ["Total"]):
        col.metric(name, int(r[name]))
else:
    if country != "Overall":  # one country across editions
        fig = px.bar(tally, x="Year", y=MEDALS, color_discrete_map=MEDAL_COLORS)
        fig.update_xaxes(type="category")
    else:
        fig = px.bar(tally.head(15), x="region", y=MEDALS, color_discrete_map=MEDAL_COLORS,
                     title="Top 15 nations")
        fig.update_xaxes(title=None)
    fig.update_layout(legend_title_text="Medal", yaxis_title="Medals")
    show(fig, 420)

table(tally)
st.download_button("⬇️ Download table as CSV", tally.to_csv(index=False), "medal_tally.csv", "text/csv")
