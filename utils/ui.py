"""Shared look & feel + small wrappers so every page behaves the same."""
import html
import inspect
import re

import plotly.express as px
import streamlit as st

from .constants import BLACK, BLUE, GREEN, RED, YELLOW

CSS = """
<style>
.block-container {padding-top: 2rem; max-width: 1250px;}
[data-testid="stMetric"] {
    background: #F2F7FB; border: 1px solid #DCE8F2; border-left: 5px solid #0085C7;
    padding: 14px 16px; border-radius: 10px;
}
[data-testid="stMetricValue"] {font-weight: 700;}
[data-testid="stMetricValue"] > div {white-space: normal; overflow-wrap: anywhere; line-height: 1.15;}
.hl-card {background: #F2F7FB; border: 1px solid #DCE8F2; border-left: 5px solid #0085C7;
    padding: 14px 16px; border-radius: 10px;}
.hl-label {font-size: .9rem; color: #4A5560;}
.hl-value {font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.35;}
.hl-sub {font-size: .85rem; color: #5B6670; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.rings span {display:inline-block; width:18px; height:18px; border-radius:50%;
    border:3px solid; margin-right:4px; background:transparent;}
.hero {background: linear-gradient(120deg, #0085C7 0%, #00A3E0 55%, #009F3D 100%);
    color: white; padding: 34px 36px; border-radius: 16px; margin-bottom: 1.2rem;}
.hero h1 {color: white; margin: 6px 0 4px 0; font-size: 2.3rem;}
.hero p {color: #EAF6FD; margin: 0; font-size: 1.05rem;}
.hero .rings span {border-color: white;}
</style>
"""


def rings():
    colors = [BLUE, YELLOW, BLACK, GREEN, RED]
    return '<div class="rings">' + "".join(f'<span style="border-color:{c}"></span>' for c in colors) + "</div>"


def setup_page(title, icon, subtitle=None, show_title=True):
    """Must be the first Streamlit call on every page."""
    st.set_page_config(page_title=f"{title} · Olympics Analytics", page_icon=icon, layout="wide")
    px.defaults.template = "plotly_white"
    st.markdown(CSS, unsafe_allow_html=True)
    st.sidebar.markdown(rings(), unsafe_allow_html=True)
    st.sidebar.caption("Summer Olympics 1896–2016 · Kaggle `120 years of Olympic history`")
    if show_title:
        st.title(f"{icon} {title}")
        if subtitle:
            st.caption(subtitle)


def _streamlit_at_least(major, minor):
    nums = re.findall(r"\d+", st.__version__)[:2]
    return (int(nums[0]), int(nums[1])) >= (major, minor)


# `width="stretch"` is accepted by st.dataframe from Streamlit 1.49 but by st.plotly_chart
# only from 1.51. On older versions an unknown `width` is passed to Plotly as a deprecated
# keyword and triggers a warning, so each call uses what its own Streamlit version supports.
_PLOTLY_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters
_TABLE_WIDTH = _streamlit_at_least(1, 49)


def show(fig, height=None):
    """st.plotly_chart that works on old and new Streamlit versions."""
    if height:
        fig.update_layout(height=height)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    if _PLOTLY_WIDTH:
        st.plotly_chart(fig, width="stretch")
    else:
        st.plotly_chart(fig, use_container_width=True)


def table(df, **kwargs):
    if _TABLE_WIDTH:
        st.dataframe(df, width="stretch", hide_index=True, **kwargs)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)


def short_name(name):
    """'Michael Fred Phelps, II' -> 'Michael Phelps' (first + last name only)."""
    name = re.sub(r"\(.*?\)", "", str(name)).split(",")[0].strip()
    parts = name.split()
    return f"{parts[0]} {parts[-1]}" if len(parts) > 2 else name


def highlight_card(label, value, sub=""):
    """Metric-style card whose value always fits on one line (font shrinks with length)."""
    n = len(value)
    size = 2.0 if n <= 11 else 1.7 if n <= 15 else 1.45 if n <= 20 else 1.25
    st.markdown(
        f'<div class="hl-card"><div class="hl-label">{html.escape(label)}</div>'
        f'<div class="hl-value" style="font-size:{size}rem" title="{html.escape(value)}">{html.escape(value)}</div>'
        f'<div class="hl-sub" title="{html.escape(sub)}">{html.escape(sub)}</div></div>',
        unsafe_allow_html=True,
    )
