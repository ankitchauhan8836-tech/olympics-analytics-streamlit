import plotly.express as px
import streamlit as st

from utils import analysis as an
from utils.constants import NON_COUNTRIES
from utils.data import load_data
from utils.ui import setup_page, show, table

setup_page("Country Analysis", "🌍")
df = load_data()

countries = sorted(set(df["region"].dropna()) - NON_COUNTRIES)
country = st.sidebar.selectbox("Country", countries, index=countries.index("India") if "India" in countries else 0)
s = an.country_summary(df, country)

st.subheader(country)
if s["total"] == 0:
    st.info(f"{country} has not won a medal at the Summer Games in this dataset.")
    st.metric("Editions competed", s["editions"])
    st.stop()

c = st.columns(5)
c[0].metric("Total medals", s["total"])
c[1].metric("Gold / Silver / Bronze", f"{s['gold']} / {s['silver']} / {s['bronze']}")
c[2].metric("Editions", s["editions"])
c[3].metric("Best edition", s["best_year"][0], f"{s['best_year'][1]} medals", delta_color="off")
c[4].metric("Best sport", s["best_sport"][0], f"{s['best_sport'][1]} medals", delta_color="off")

by_year = an.country_medals_by_year(df, country)
fig = px.line(by_year, x="Year", y="Medals", markers=True, title=f"{country}: medals over the years")
show(fig, 340)

pt = an.country_sport_pivot(df, country)
n = st.slider("Sports to show in the heatmap", 5, min(30, len(pt)), min(15, len(pt))) if len(pt) > 5 else len(pt)
fig = px.imshow(pt.head(n), aspect="auto", color_continuous_scale="YlOrRd", text_auto=True,
                labels=dict(color="Medals", x="Year"), title=f"Where {country} wins medals")
fig.update_xaxes(type="category")
show(fig, 120 + 38 * n)

st.subheader(f"Top athletes of {country}")
table(an.most_successful(df, country=country, n=10))
