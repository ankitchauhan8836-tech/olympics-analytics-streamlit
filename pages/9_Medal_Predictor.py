import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from utils import models
from utils.constants import NEXT_EDITION
from utils.data import load_data
from utils.ui import setup_page, show, table

setup_page("Medal Predictor", "🔮", "Gradient-boosting forecast of each country's medal count.")
df = load_data()


@st.cache_resource(show_spinner="Training the forecaster (first visit only)…")
def get_result(_df):
    return models.train_medal_model(_df)


res = get_result(df)
year, host = NEXT_EDITION
st.caption(f"The dataset ends at Rio 2016, so the forecast is for the next edition ({year}, host: {host}). "
           "You can compare it with the real results.")

tab1, tab2, tab3 = st.tabs([f"{year} forecast", "Country view", "Model quality"])

with tab1:
    top = res["forecast"].head(15).copy()
    top["Role"] = top["is_host"].map({1: "Host", 0: "Other"})
    fig = px.bar(top.iloc[::-1], x="Predicted", y="region", orientation="h", color="Role",
                 color_discrete_map={"Host": "#DF0024", "Other": "#0085C7"}, text_auto=".0f",
                 labels={"Predicted": "Predicted medals", "region": ""}, title=f"Top 15 predicted medal tables, {year}")
    show(fig, 520)
    out = res["forecast"][["region", "lag1", "Predicted"]].rename(
        columns={"region": "Country", "lag1": "Medals at last edition", "Predicted": f"Predicted {year}"})
    out[f"Predicted {year}"] = out[f"Predicted {year}"].round(1)
    table(out)

with tab2:
    countries = sorted(res["forecast"]["region"])
    country = st.selectbox("Country", countries, index=countries.index("USA") if "USA" in countries else 0)
    hist = res["history"].query("region == @country")
    bt = res["backtest"].query("region == @country")
    nxt = res["forecast"].query("region == @country")
    fig = go.Figure()
    fig.add_scatter(x=hist["Year"], y=hist["Total"], mode="lines+markers", name="Actual", line_color="#0085C7")
    if not bt.empty:
        fig.add_scatter(x=bt["Year"], y=bt["Predicted"], mode="markers", name="Back-test prediction",
                        marker=dict(symbol="diamond", size=12, color="#F4C300", line=dict(width=1, color="#1B1B1B")))
    fig.add_scatter(x=[year], y=nxt["Predicted"], mode="markers", name=f"{year} forecast",
                    marker=dict(symbol="star", size=16, color="#DF0024"))
    fig.update_layout(title=f"{country}: medals per edition", xaxis_title="Year", yaxis_title="Medals")
    show(fig, 420)

with tab3:
    st.markdown(f"**Back-test:** trained on editions before 2008 ({res['n_train']:,} country-edition rows), "
                f"then predicted 2008, 2012 and 2016 ({res['n_test']:,} rows), one edition ahead each time.")
    c = st.columns(3)
    c[0].metric("MAE: all nations", f"{res['mae_model']:.2f}", f"naive {res['mae_naive']:.2f}", delta_color="off")
    c[1].metric("MAE: medal contenders", f"{res['mae_model_top']:.2f}", f"naive {res['mae_naive_top']:.2f}", delta_color="off",
                help="Nations with 10+ medals at the previous edition")
    c[2].metric("MAE: host nations", f"{res['mae_model_host']:.2f}", f"naive {res['mae_naive_host']:.2f}", delta_color="off",
                help=f"Only {res['n_host']} host editions in the test set, so read with care")
    st.caption("MAE = mean absolute error in medals (lower is better). "
               "“Naive” predicts the same number as the previous edition.")
    c = st.columns(2)
    c[0].metric("R²", f"{res['r2']:.2f}")
    c[1].metric("Test rows", f"{res['n_test']:,}")
    imp = res["importances"].reset_index()
    imp.columns = ["Feature", "Importance"]
    show(px.bar(imp, x="Importance", y="Feature", orientation="h", title="Feature importance"), 300)
    with st.expander("Features, method and limitations"):
        st.markdown(
            "- **Features:** medals at the last edition, two editions ago, rolling mean of the last three, "
            "athletes sent last time, number of previous editions, and whether the country hosts.\n"
            "- **Model:** `GradientBoostingRegressor` on `log(1 + medals)`, predictions clipped at 0.\n"
            "- **Honest read:** most nations win few medals, so overall error looks small for every method. "
            "The gain over the naive baseline is clearer for contenders and hosts.\n"
            "- **Limits:** it can't know about boycotts, doping bans, new sports, team size or the "
            "athletes actually selected. Medal counts are mostly persistent, which is why `rolling mean` dominates.\n"
            "- **Next steps:** add GDP and population, qualified-athlete counts, and prediction intervals.")
        table(res["backtest"].round(1).sort_values(["Year", "Total"], ascending=[True, False]).head(40))
