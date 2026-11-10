"""Loading + preprocessing of the raw Kaggle files."""
from pathlib import Path

import pandas as pd
import streamlit as st

from .constants import MEDALS, REGION_FIXES

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def preprocess(df: pd.DataFrame, region_df: pd.DataFrame) -> pd.DataFrame:
    """Summer Games only, attach country names, add medal indicator columns."""
    df = df[df["Season"] == "Summer"].copy()
    df = df.merge(region_df[["NOC", "region"]], on="NOC", how="left")
    df["region"] = df["region"].fillna(df["NOC"].map(REGION_FIXES))
    df = df.drop_duplicates()
    for medal in MEDALS:  # 0/1 columns, easy to sum
        df[medal] = (df["Medal"] == medal).astype(int)
    df["BMI"] = df["Weight"] / (df["Height"] / 100) ** 2
    return df.reset_index(drop=True)


@st.cache_data(show_spinner="Loading Olympic data…")
def load_data() -> pd.DataFrame:
    athletes = pd.read_csv(DATA_DIR / "athlete_events.csv")
    regions = pd.read_csv(DATA_DIR / "noc_regions.csv")
    return preprocess(athletes, regions)
