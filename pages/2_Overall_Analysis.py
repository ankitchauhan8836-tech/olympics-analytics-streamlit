import plotly.express as px
import streamlit as st

from utils import analysis as an
from utils.data import load_data
from utils.ui import setup_page, show, table

setup_page("Overall Analysis", "📈", "How the Games have grown since 1896.")
df = load_data()

tab1, tab2, tab3 = st.tabs(["Growth over time", "Events per sport", "Most successful athletes"])

with tab1:
    for col, label, title in [("region", "Nations", "Participating nations"),
                              ("Event", "Events", "Events held"),
                              ("ID", "Athletes", "Athletes competing")]:
        data = an.data_over_time(df, col)
        fig = px.line(data, x="Year", y="count", markers=True, title=title, labels={"count": label})
        show(fig, 320)

with tab2:
    st.caption("Number of distinct events each sport offered at every edition. Hover for exact values.")
    pt = an.events_heatmap(df)
    fig = px.imshow(pt, aspect="auto", color_continuous_scale="YlGnBu",
                    labels=dict(color="Events", x="Year"))
    fig.update_xaxes(type="category")
    show(fig, 900)

with tab3:
    sports = ["Overall"] + sorted(df["Sport"].dropna().unique())
    sport = st.selectbox("Sport", sports)
    top = an.most_successful(df, sport)
    fig = px.bar(top.iloc[::-1], x="Medals", y="Name", orientation="h", color="Country",
                 hover_data=["Sport", "Gold", "Silver", "Bronze"])
    fig.update_layout(yaxis_title=None)
    show(fig, 520)
    table(top)
