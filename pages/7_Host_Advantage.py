import plotly.graph_objects as go
import streamlit as st

from utils import analysis as an
from utils.data import load_data
from utils.ui import setup_page, show, table

setup_page("Host Advantage", "🏟️", "Do host nations win a bigger slice of the medals?")
df = load_data()

min_year = st.sidebar.slider("From edition", 1896, 2000, 1948, step=4)
res = an.host_advantage(df, min_year)
if res.empty:
    st.info("Not enough data for this range.")
    st.stop()

more = int((res["Change (pp)"] > 0).sum())
c = st.columns(3)
c[0].metric("Hosts who gained share", f"{more} of {len(res)}")
c[1].metric("Median multiple", f"{res['Multiple'].median():.2f}×", help="Host share ÷ usual share")
c[2].metric("Biggest boost", f"{res.loc[res['Multiple'].idxmax(), 'Host']} {res.loc[res['Multiple'].idxmax(), 'Year']}",
            f"{res['Multiple'].max():.2f}×", delta_color="off")

labels = res["Host"] + " " + res["Year"].astype(str)
fig = go.Figure()
fig.add_bar(x=labels, y=res["Usual share %"], name="Usual share (2 editions either side)", marker_color="#A8A9AD")
fig.add_bar(x=labels, y=res["Host share %"], name="Share as host", marker_color="#0085C7")
fig.update_layout(barmode="group", yaxis_title="% of all medals awarded", legend=dict(orientation="h", y=1.12))
show(fig, 440)
table(res)

with st.expander("Method and caveats"):
    st.markdown(
        "- **Share** = the country's medals ÷ all medals won at that edition, so growth in the "
        "number of events doesn't distort the comparison.\n"
        "- **Usual share** = average share over the host's two previous and two following editions.\n"
        "- Boycotts (1980, 1984), the split of Germany and the USSR, and small samples make some "
        "rows noisy. `Germany` merges West and East Germany; `Russia` includes the USSR.\n"
        "- This shows association, not proof of cause: hosts also enter more athletes and invest more.")
