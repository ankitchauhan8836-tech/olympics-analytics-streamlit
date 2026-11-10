import plotly.express as px
import streamlit as st

from utils import analysis as an
from utils.constants import MEDAL_COLORS, MEDALS, NON_COUNTRIES
from utils.data import load_data
from utils.ui import setup_page, show

setup_page("Country vs Country", "⚔️", "Pick two nations and compare their Olympic records.")
df = load_data()

countries = sorted(set(df["region"].dropna()) - NON_COUNTRIES)
default = lambda name, fallback: countries.index(name) if name in countries else fallback
a = st.sidebar.selectbox("Country A", countries, index=default("USA", 0))
b = st.sidebar.selectbox("Country B", countries, index=default("China", 1))
if a == b:
    st.warning("Choose two different countries.")
    st.stop()

sa, sb = an.country_summary(df, a), an.country_summary(df, b)
c = st.columns(2)
for col, name, s in [(c[0], a, sa), (c[1], b, sb)]:
    col.subheader(name)
    col.metric("Total medals", s["total"])
    col.caption(f"🥇 {s['gold']}   🥈 {s['silver']}   🥉 {s['bronze']}   ·   {s['editions']} editions")

# --- medals by type ---------------------------------------------------------
tally = an.fetch_medal_tally(df)
tally = tally[tally["region"].isin([a, b])].melt(id_vars="region", value_vars=MEDALS,
                                                  var_name="Medal", value_name="Count")
fig = px.bar(tally, x="Medal", y="Count", color="region", barmode="group",
             category_orders={"Medal": MEDALS}, title="Medals by type")
show(fig, 360)

# --- medals per edition + who won more --------------------------------------
panel = an.region_year_panel(df)
both = panel[panel["region"].isin([a, b])]
fig = px.line(both, x="Year", y="Total", color="region", markers=True, title="Medals per edition")
show(fig, 360)

wide = both.pivot(index="Year", columns="region", values="Total").dropna()
if not wide.empty:
    wins_a, wins_b = int((wide[a] > wide[b]).sum()), int((wide[b] > wide[a]).sum())
    st.info(f"Across the {len(wide)} editions where both competed: **{a}** out-medalled **{b}** "
            f"{wins_a} times, **{b}** won more {wins_b} times, "
            f"and they tied {len(wide) - wins_a - wins_b}.")

# --- sport strengths --------------------------------------------------------
t = an.medal_events(df)
t = t[t["region"].isin([a, b])]
by_sport = t.groupby(["Sport", "region"]).size().reset_index(name="Medals")
top_sports = by_sport.groupby("Sport")["Medals"].sum().nlargest(12).index
fig = px.bar(by_sport[by_sport["Sport"].isin(top_sports)], y="Sport", x="Medals", color="region",
             barmode="group", orientation="h", title="Strongest sports (top 12 combined)")
fig.update_yaxes(categoryorder="total ascending")
show(fig, 520)
