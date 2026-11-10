import plotly.express as px
import streamlit as st

from utils import models
from utils.data import load_data
from utils.ui import setup_page, show, table

setup_page("Sport Matcher", "🤖", "A random-forest model that suggests Olympic sports for your body.")
df = load_data()


@st.cache_resource(show_spinner="Training the model (first visit only)…")
def get_bundle(_df):
    return models.train_sport_model(_df)


bundle = get_bundle(df)

c = st.columns(4)
sex = c[0].selectbox("Sex", ["M", "F"], format_func=lambda s: "Male" if s == "M" else "Female")
age = c[1].slider("Age", 12, 50, 22)
height = c[2].slider("Height (cm)", 140, 220, 175)
weight = c[3].slider("Weight (kg)", 35, 150, 70)

rec = models.recommend_sports(bundle, sex, age, height, weight)
left, right = st.columns([3, 2])
with left:
    fig = px.bar(rec.iloc[::-1], x="Match %", y="Sport", orientation="h", text_auto=".1f",
                 title="Top 5 matching sports")
    fig.update_traces(marker_color="#0085C7")
    show(fig, 360)
with right:
    st.markdown("**You vs. a typical medalist**")
    prof = bundle["profile"].loc[rec["Sport"].head(3)].reset_index()
    prof.loc[len(prof)] = ["You", age, height, weight]
    table(prof.rename(columns={"Height": "Height (cm)", "Weight": "Weight (kg)"}))

st.subheader("How reliable is it?")
m = st.columns(3)
m[0].metric("Top-1 accuracy", f"{bundle['top1']:.0%}", f"baseline {bundle['baseline']:.0%}", delta_color="off")
m[1].metric("Top-3 accuracy", f"{bundle['top3']:.0%}")
m[2].metric("Held-out athletes", f"{bundle['n_test']:,}")
with st.expander("About this model"):
    st.markdown(
        f"- **Data:** medalists (one row per athlete per sport) in the 20 sports with the most medalists, "
        f"excluding Art Competitions. Split 80/20 stratified; {bundle['n_train']:,} train / {bundle['n_test']:,} test.\n"
        "- **Model:** `RandomForestClassifier` (300 trees, balanced class weights).\n"
        "- **Features:** sex, age, height, weight.\n"
        "- **Top-k accuracy:** how often the athlete's real sport is among the model's top 1 / top 3 guesses. "
        "The baseline is always guessing the most common sport.\n"
        "- **Limits:** body measurements alone can't capture talent, training or access to facilities. "
        "Treat the output as a fun profile match, not advice.")
    imp = bundle["importances"].reset_index()
    imp.columns = ["Feature", "Importance"]
    show(px.bar(imp, x="Importance", y="Feature", orientation="h", title="Feature importance"), 260)
