"""Pure pandas analysis functions (no Streamlit), so they are easy to unit-test."""
import numpy as np
import pandas as pd

from .constants import HOSTS, MEDALS, NO_ISO, NOC_ISO_FIXES, NON_COUNTRIES

EVENT_KEY = ["Team", "NOC", "Games", "Year", "City", "Sport", "Event", "Medal"]
MEDAL_RANK = {"Gold": 0, "Silver": 1, "Bronze": 2}


def medal_events(df: pd.DataFrame) -> pd.DataFrame:
    """One row per medal won. A team medal counts once, not once per athlete."""
    return df.dropna(subset=["Medal"]).drop_duplicates(subset=EVENT_KEY)


def athlete_level(df: pd.DataFrame) -> pd.DataFrame:
    """One row per athlete, keeping the row where they won their best medal."""
    rank = df["Medal"].map(MEDAL_RANK).fillna(3)
    return df.assign(_rank=rank).sort_values("_rank").drop_duplicates("ID").drop(columns="_rank")


# --------------------------------------------------------------- medal tally
def country_year_list(df):
    years = ["Overall"] + sorted(df["Year"].unique().tolist())
    countries = sorted(set(df["region"].dropna()) - NON_COUNTRIES)
    return years, ["Overall"] + countries


def fetch_medal_tally(df, year="Overall", country="Overall"):
    t = medal_events(df)
    if year != "Overall":
        t = t[t["Year"] == int(year)]
    if country != "Overall":
        t = t[t["region"] == country]

    by_year = country != "Overall" and year == "Overall"
    out = t.groupby("Year" if by_year else "region")[MEDALS].sum()
    if by_year:
        out = out.sort_index()
    else:
        out = out.sort_values(MEDALS, ascending=False)
    out["Total"] = out[MEDALS].sum(axis=1)
    out = out.astype(int).reset_index()
    if not by_year:
        out.insert(0, "Rank", range(1, len(out) + 1))
    return out


# ------------------------------------------------------------ overall trends
def data_over_time(df, col):
    return df.groupby("Year")[col].nunique().reset_index(name="count")


def events_heatmap(df):
    x = df.drop_duplicates(["Year", "Sport", "Event"])
    return x.pivot_table(index="Sport", columns="Year", values="Event",
                         aggfunc="count", fill_value=0).astype(int)


def most_successful(df, sport="Overall", country=None, n=15):
    t = df.dropna(subset=["Medal"])
    if sport != "Overall":
        t = t[t["Sport"] == sport]
    if country:
        t = t[t["region"] == country]
    g = (t.groupby(["ID", "Name"])
         .agg(Gold=("Gold", "sum"), Silver=("Silver", "sum"), Bronze=("Bronze", "sum"),
              Medals=("Medal", "size"),
              Sport=("Sport", lambda s: s.mode().iat[0]),
              Country=("region", lambda s: s.mode().iat[0]))
         .reset_index()
         .sort_values(["Medals", "Gold", "Silver"], ascending=False)
         .head(n))
    return g[["Name", "Sport", "Country", "Gold", "Silver", "Bronze", "Medals"]].reset_index(drop=True)


# ------------------------------------------------------------ country views
def country_medals_by_year(df, country):
    t = medal_events(df)
    t = t[t["region"] == country]
    return t.groupby("Year").size().reset_index(name="Medals")


def country_sport_pivot(df, country):
    t = medal_events(df)
    t = t[t["region"] == country]
    pt = t.pivot_table(index="Sport", columns="Year", values="Medal", aggfunc="count", fill_value=0)
    return pt.loc[pt.sum(axis=1).sort_values(ascending=False).index]


def country_summary(df, country):
    t = medal_events(df)
    t = t[t["region"] == country]
    by_year = t.groupby("Year").size()
    by_sport = t.groupby("Sport").size()
    return {
        "gold": int(t["Gold"].sum()), "silver": int(t["Silver"].sum()),
        "bronze": int(t["Bronze"].sum()), "total": int(len(t)),
        "editions": int(df.loc[df["region"] == country, "Year"].nunique()),
        "best_year": (int(by_year.idxmax()), int(by_year.max())) if len(by_year) else None,
        "best_sport": (by_sport.idxmax(), int(by_sport.max())) if len(by_sport) else None,
    }


# ------------------------------------------------------------ athlete views
def age_distribution(df):
    a = athlete_level(df).dropna(subset=["Age"])
    parts = [a.assign(Group="All athletes")]
    for m in MEDALS:
        parts.append(a[a["Medal"] == m].assign(Group=f"{m} medalists"))
    return pd.concat(parts)[["Group", "Age"]]


def gold_age_by_sport(df, min_golds=30):
    g = df[df["Medal"] == "Gold"].drop_duplicates(["ID", "Sport"]).dropna(subset=["Age"])
    counts = g["Sport"].value_counts()
    return g[g["Sport"].isin(counts[counts >= min_golds].index)][["Sport", "Age"]]


def weight_v_height(df, sport="Overall"):
    d = df.assign(_r=df["Medal"].map(MEDAL_RANK).fillna(3)).sort_values("_r")
    if sport == "Overall":
        d = d.drop_duplicates("ID")
    else:
        d = d[d["Sport"] == sport].drop_duplicates("ID")
    d = d.dropna(subset=["Height", "Weight"]).copy()
    d["Medal"] = d["Medal"].fillna("No Medal")
    return d[["Name", "Sex", "Height", "Weight", "Medal", "Sport"]]


def men_vs_women(df):
    a = df.drop_duplicates(["ID", "Year"])
    tab = a.groupby(["Year", "Sex"])["ID"].nunique().unstack(fill_value=0)
    tab = tab.rename(columns={"M": "Male", "F": "Female"})
    for c in ("Male", "Female"):
        if c not in tab:
            tab[c] = 0
    tab["Female %"] = 100 * tab["Female"] / (tab["Male"] + tab["Female"])
    return tab[["Male", "Female", "Female %"]].reset_index()


# ------------------------------------------------------------------ map
def _iso(noc):
    return None if noc in NO_ISO else NOC_ISO_FIXES.get(noc, noc)


def _by_iso(t):
    t = t.assign(iso=t["NOC"].map(_iso)).dropna(subset=["iso"])
    return t


def world_map_data(df, year="Overall"):
    t = medal_events(df)
    if year != "Overall":
        t = t[t["Year"] == int(year)]
    g = (_by_iso(t).groupby("iso")
         .agg(Gold=("Gold", "sum"), Silver=("Silver", "sum"), Bronze=("Bronze", "sum"),
              Country=("region", lambda s: s.mode().iat[0]))
         .reset_index())
    g["Total"] = g[MEDALS].sum(axis=1)
    return g


def world_map_animation(df):
    t = _by_iso(medal_events(df))
    g = (t.groupby(["Year", "iso"])
         .agg(Gold=("Gold", "sum"), Silver=("Silver", "sum"), Bronze=("Bronze", "sum"),
              Country=("region", lambda s: s.mode().iat[0]))
         .reset_index())
    g["Total"] = g[MEDALS].sum(axis=1)
    return g.sort_values("Year")


# ---------------------------------------------------- country panel + hosts
def region_year_panel(df):
    """One row per country per edition: athletes sent and medals won."""
    d = df[df["region"].notna() & ~df["region"].isin(NON_COUNTRIES) & (df["Year"] != 1906)]
    athletes = d.groupby(["region", "Year"])["ID"].nunique().rename("Athletes").to_frame()
    medals = medal_events(d).groupby(["region", "Year"])[MEDALS].sum()
    p = athletes.join(medals).fillna(0).astype(int)
    p["Total"] = p[MEDALS].sum(axis=1)
    return p.reset_index().sort_values(["region", "Year"]).reset_index(drop=True)


def host_advantage(df, min_year=1948):
    """Host's share of all medals in its hosting year vs. its two editions either side."""
    p = region_year_panel(df)
    p["Share"] = p["Total"] / p["Year"].map(p.groupby("Year")["Total"].sum())
    rows = []
    for year, host in HOSTS.items():
        if year < min_year:
            continue
        h = p[p["region"] == host]
        cur = h[h["Year"] == year]
        base = pd.concat([h[h["Year"] < year].tail(2), h[h["Year"] > year].head(2)])
        if cur.empty or base.empty:
            continue
        host_share, base_share = cur["Share"].iloc[0] * 100, base["Share"].mean() * 100
        rows.append({
            "Year": year, "Host": host, "Host medals": int(cur["Total"].iloc[0]),
            "Usual medals": round(base["Total"].mean(), 1),
            "Host share %": round(host_share, 2), "Usual share %": round(base_share, 2),
            "Change (pp)": round(host_share - base_share, 2),
            "Multiple": round(host_share / base_share, 2) if base_share > 0 else np.nan,
        })
    return pd.DataFrame(rows)
