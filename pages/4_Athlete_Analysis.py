import plotly.express as px
import streamlit as st

from utils import analysis as an
from utils.constants import MEDAL_COLORS
from utils.data import load_data
from utils.ui import setup_page, show

setup_page("Athlete Analysis", "🏃", "Age, body size and gender balance of Olympic athletes.")
df = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["Age", "Age by sport", "Height vs weight", "Men vs women"])

with tab1:
    ages = an.age_distribution(df)
    fig = px.violin(ages, x="Group", y="Age", color="Group", box=True, points=False,
                    color_discrete_map={"All athletes": "#0085C7", "Gold medalists": MEDAL_COLORS["Gold"],
                                        "Silver medalists": MEDAL_COLORS["Silver"],
                                        "Bronze medalists": MEDAL_COLORS["Bronze"]})
    fig.update_layout(showlegend=False, xaxis_title=None, title="Age distribution (one entry per athlete)")
    show(fig, 480)

with tab2:
    g = an.gold_age_by_sport(df)
    order = g.groupby("Sport")["Age"].median().sort_values().index.tolist()
    fig = px.box(g, x="Age", y="Sport", category_orders={"Sport": order}, points=False,
                 title="Age of gold medalists by sport (sports with 30+ gold medalists)")
    fig.update_traces(marker_color="#0085C7")
    show(fig, 120 + 22 * len(order))
    st.caption(f"Youngest median: **{order[0]}** · oldest median: **{order[-1]}**")

with tab3:
    sports = ["Overall"] + sorted(df["Sport"].dropna().unique())
    sport = st.selectbox("Sport", sports, key="hw_sport")
    d = an.weight_v_height(df, sport)
    if len(d) > 12000:
        d = d.sample(12000, random_state=1)
        st.caption("Showing a random sample of 12,000 athletes.")
    if d.empty:
        st.info("No height/weight data for this sport.")
    else:
        fig = px.scatter(d, x="Weight", y="Height", color="Medal", symbol="Sex", opacity=0.65,
                         color_discrete_map=MEDAL_COLORS, hover_name="Name",
                         category_orders={"Medal": ["Gold", "Silver", "Bronze", "No Medal"]},
                         labels={"Weight": "Weight (kg)", "Height": "Height (cm)"})
        show(fig, 520)

with tab4:
    mw = an.men_vs_women(df)
    fig = px.line(mw, x="Year", y=["Male", "Female"], markers=True, title="Athletes per edition",
                  labels={"value": "Athletes", "variable": ""})
    show(fig, 380)
    fig = px.area(mw, x="Year", y="Female %", title="Women's share of athletes (%)")
    fig.update_traces(line_color="#DF0024")
    show(fig, 300)
