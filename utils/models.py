"""Two small ML models: a sport recommender and a medal-count forecaster."""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from .analysis import region_year_panel
from .constants import HOSTS, NEXT_EDITION

SPORT_FEATURES = ["male", "Age", "Height", "Weight"]
MEDAL_FEATURES = ["lag1", "lag2", "mean3", "athletes_lag1", "experience", "is_host"]


# ------------------------------------------------------------ sport matcher
def train_sport_model(df, top_n=20, seed=42):
    d = (df.dropna(subset=["Medal", "Age", "Height", "Weight", "Sex"])
         .query("Sport != 'Art Competitions'")
         .drop_duplicates(["ID", "Sport"]))
    d = d[d["Sport"].isin(d["Sport"].value_counts().head(top_n).index)].copy()
    d["male"] = (d["Sex"] == "M").astype(int)
    X, y = d[SPORT_FEATURES], d["Sport"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)

    model = RandomForestClassifier(n_estimators=300, min_samples_leaf=3, n_jobs=-1,
                                   class_weight="balanced_subsample", random_state=seed).fit(X_tr, y_tr)
    proba, classes = model.predict_proba(X_te), model.classes_
    top3 = np.argsort(proba, axis=1)[:, ::-1][:, :3]
    return {
        "model": model,
        "top1": float(np.mean(classes[top3[:, 0]] == y_te.values)),
        "top3": float(np.mean([t in classes[i] for t, i in zip(y_te.values, top3)])),
        "baseline": float(y_te.value_counts(normalize=True).max()),
        "n_train": len(X_tr), "n_test": len(X_te),
        "profile": d.groupby("Sport")[["Age", "Height", "Weight"]].mean().round(1),
        "importances": pd.Series(model.feature_importances_, index=SPORT_FEATURES).sort_values(),
    }


def recommend_sports(bundle, sex, age, height, weight, k=5):
    x = pd.DataFrame({"male": [int(sex == "M")], "Age": [age], "Height": [height], "Weight": [weight]})
    p = bundle["model"].predict_proba(x)[0]
    out = pd.DataFrame({"Sport": bundle["model"].classes_, "Match %": p * 100})
    return out.sort_values("Match %", ascending=False).head(k).reset_index(drop=True)


# ----------------------------------------------------------- medal forecaster
def build_features(df):
    p = region_year_panel(df)
    g = p.groupby("region")
    p["lag1"] = g["Total"].shift(1)
    p["lag2"] = g["Total"].shift(2).fillna(0)
    p["mean3"] = g["Total"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    p["athletes_lag1"] = g["Athletes"].shift(1)
    p["experience"] = g.cumcount()
    p["is_host"] = (p["Year"].map(HOSTS) == p["region"]).astype(int)
    return p


def _fit(X, y, seed=42):
    return GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=3,
                                     subsample=0.8, random_state=seed).fit(X, np.log1p(y))


def _predict(model, X):
    return np.clip(np.expm1(model.predict(X)), 0, None)


def _next_edition_rows(panel):
    year, host = NEXT_EDITION
    last = panel["Year"].max()
    rows = []
    for region, g in panel.groupby("region"):
        if g["Year"].max() != last:  # only nations that competed at the latest edition
            continue
        m = g["Total"].tolist()
        rows.append({"region": region, "Year": year, "lag1": m[-1],
                     "lag2": m[-2] if len(m) > 1 else 0, "mean3": float(np.mean(m[-3:])),
                     "athletes_lag1": g["Athletes"].iloc[-1], "experience": len(g),
                     "is_host": int(region == host)})
    return pd.DataFrame(rows)


def train_medal_model(df, test_years=(2008, 2012, 2016)):
    """Back-test on the last three editions, then refit on everything and forecast 2020."""
    feats = build_features(df)
    pool = feats[(feats["Year"] >= 1952) & feats["lag1"].notna()].copy()
    train, test = pool[pool["Year"] < min(test_years)], pool[pool["Year"].isin(test_years)].copy()

    back = _fit(train[MEDAL_FEATURES], train["Total"])
    test["Predicted"] = _predict(back, test[MEDAL_FEATURES])

    final = _fit(pool[MEDAL_FEATURES], pool["Total"])
    nxt = _next_edition_rows(feats)
    nxt["Predicted"] = _predict(final, nxt[MEDAL_FEATURES])

    top = test["lag1"] >= 10  # established medal-winning nations
    host = test["is_host"] == 1
    mae = mean_absolute_error
    return {
        "history": feats,
        "backtest": test[["region", "Year", "Total", "Predicted", "lag1", "is_host"]],
        "forecast": nxt.sort_values("Predicted", ascending=False).reset_index(drop=True),
        "mae_model": float(mean_absolute_error(test["Total"], test["Predicted"])),
        "mae_naive": float(mean_absolute_error(test["Total"], test["lag1"])),
        "r2": float(r2_score(test["Total"], test["Predicted"])),
        "mae_model_top": float(mae(test.loc[top, "Total"], test.loc[top, "Predicted"])),
        "mae_naive_top": float(mae(test.loc[top, "Total"], test.loc[top, "lag1"])),
        "mae_model_host": float(mae(test.loc[host, "Total"], test.loc[host, "Predicted"])),
        "mae_naive_host": float(mae(test.loc[host, "Total"], test.loc[host, "lag1"])),
        "n_host": int(host.sum()),
        "n_train": len(train), "n_test": len(test),
        "importances": pd.Series(final.feature_importances_, index=MEDAL_FEATURES).sort_values(),
    }
