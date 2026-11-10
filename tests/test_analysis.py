import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import analysis as an  # noqa: E402
from utils.constants import MEDALS, NO_ISO  # noqa: E402
from utils.data import DATA_DIR, preprocess  # noqa: E402


@pytest.fixture(scope="session")
def df():
    return preprocess(pd.read_csv(DATA_DIR / "athlete_events.csv"),
                      pd.read_csv(DATA_DIR / "noc_regions.csv"))


def test_only_summer_and_no_missing_regions(df):
    assert df["Season"].eq("Summer").all()
    assert df["region"].notna().all()


def test_rio_2016_usa_medals(df):
    row = an.fetch_medal_tally(df, 2016, "USA").iloc[0]
    assert (row["Gold"], row["Silver"], row["Bronze"], row["Total"]) == (46, 37, 38, 121)


def test_year_can_be_str_or_int(df):
    assert an.fetch_medal_tally(df, "2016", "USA").equals(an.fetch_medal_tally(df, 2016, "USA"))


def test_tally_total_is_sum(df):
    t = an.fetch_medal_tally(df)
    assert (t["Total"] == t[MEDALS].sum(axis=1)).all()
    assert t["Rank"].tolist() == list(range(1, len(t) + 1))


def test_team_medals_counted_once(df):
    # 2016 men's football is one gold for Brazil, not one per player
    t = an.medal_events(df)
    brazil = t[(t.Year == 2016) & (t.region == "Brazil") & (t.Event == "Football Men's Football")]
    assert len(brazil) == 1


def test_men_vs_women_counts_each_athlete_per_year(df):
    mw = an.men_vs_women(df)
    assert mw["Female %"].between(0, 100).all()
    assert mw.loc[mw.Year == 2016, "Female %"].iloc[0] > 40


def test_most_successful_phelps(df):
    top = an.most_successful(df, n=1).iloc[0]
    assert "Phelps" in top["Name"] and top["Medals"] == 28


def test_world_map_isos_are_valid(df):
    pycountry = pytest.importorskip("pycountry")
    valid = {c.alpha_3 for c in pycountry.countries} | {"XKX"}
    medal_nocs = an.medal_events(df)["NOC"].unique()
    bad = [n for n in medal_nocs if n not in NO_ISO and an._iso(n) not in valid]
    assert bad == []


def test_host_advantage_has_rows(df):
    res = an.host_advantage(df)
    assert not res.empty and (res["Host share %"] > 0).all()
