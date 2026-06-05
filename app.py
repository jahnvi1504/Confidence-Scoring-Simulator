import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter

st.set_page_config(
    page_title="Confidence Scoring Simulator",
    page_icon="\U0001F50D",
    layout="wide",
    initial_sidebar_state="expanded",
)

SOURCE_WEIGHTS = {
    "Official Website": 3.0,
    "Press Release": 2.5,
    "News Article": 2.0,
    "Review Platform": 1.0,
    "Community Forum": 0.5,
}

SOURCE_OPTIONS = list(SOURCE_WEIGHTS.keys())

PRESETS = {
    "All Forums": ["Community Forum"] * 5,
    "Mixed Sources": ["Official Website", "News Article", "News Article", "Community Forum", "Community Forum"],
    "Official Heavy": ["Official Website", "Official Website", "Official Website", "News Article"],
}

CATEGORY_COLORS = {
    "Low": "#ef4444",
    "Medium": "#f59e0b",
    "High": "#22c55e",
}

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(20, 184, 166, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(45, 212, 191, 0.12), transparent 22%),
            linear-gradient(180deg, #071318 0%, #09181f 35%, #081017 100%);
        color: #e5f7f4;
    }
    .hero {
        border: 1px solid rgba(45, 212, 191, 0.25);
        background: rgba(6, 17, 22, 0.72);
        border-radius: 22px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
    }
    .hero h1 {
        margin: 0;
        font-size: 2.1rem;
        color: #d8fffb;
    }
    .hero p {
        margin: 0.45rem 0 0;
        color: rgba(226, 249, 246, 0.8);
        font-size: 1rem;
    }
    .metric-card {
        border: 1px solid rgba(45, 212, 191, 0.18);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        background: rgba(8, 20, 26, 0.8);
    }
    .metric-label {
        color: rgba(226, 249, 246, 0.7);
        font-size: 0.86rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.45rem;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #f3fffe;
        margin-bottom: 0.45rem;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
        color: #f8fffd;
    }
    .table-wrap {
        border: 1px solid rgba(45, 212, 191, 0.15);
        border-radius: 18px;
        overflow: hidden;
        background: rgba(8, 20, 26, 0.72);
    }
    .callout {
        border-left: 5px solid #2dd4bf;
        background: rgba(10, 30, 35, 0.95);
        color: #e9fffd;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        font-size: 1.02rem;
    }
    .section-title {
        color: #d8fffb;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 1rem 0 0.65rem;
    }
    div[data-testid="stButton"] > button {
        border-radius: 999px;
        border: 1px solid rgba(45, 212, 191, 0.3);
        background: rgba(9, 24, 30, 0.85);
        color: #e7fffc;
        padding: 0.55rem 1rem;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: rgba(45, 212, 191, 0.65);
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def ensure_state() -> None:
    if "sources" not in st.session_state:
        st.session_state.sources = []


def score_naive(count: int) -> tuple[str, int]:
    if count >= 4:
        return "High", 3
    if count >= 2:
        return "Medium", 2
    return "Low", 1


def score_weighted(total_weight: float) -> str:
    if total_weight >= 5:
        return "High"
    if total_weight >= 2.5:
        return "Medium"
    return "Low"


def badge_html(label: str) -> str:
    return f'<span class="badge" style="background:{CATEGORY_COLORS[label]};">{label}</span>'


def format_score_value(score: str) -> str:
    return f"{score}"


def explain_difference(count: int, total_weight: float, naive_label: str, weighted_label: str) -> str:
    if count == 0:
        return "Add sources or load a preset to see how the two scoring systems diverge."

    if weighted_label == naive_label:
        return (
            f"Both systems agree right now: the naive model sees {count} sources and says {naive_label}, "
            f"while the weighted model adds up {total_weight:.1f} quality points and also says {weighted_label}."
        )

    source_counts = Counter(source["type"] for source in st.session_state.sources)
    low_quality_count = source_counts.get("Community Forum", 0) + source_counts.get("Review Platform", 0)
    high_quality_count = source_counts.get("Official Website", 0) + source_counts.get("Press Release", 0)

    if naive_label == "High" and weighted_label != "High":
        return (
            f"Naive sees {count} sources and says High. Weighted sees {low_quality_count} lower-trust sources "
            f"mixed with {high_quality_count} higher-trust sources, so it lands at {weighted_label}."
        )
    if naive_label == "Low" and weighted_label != "Low":
        return (
            f"Naive only counts {count} source{'' if count == 1 else 's'} and says Low. Weighted gives more credit to "
            f"stronger sources, so the total rises to {total_weight:.1f} points and becomes {weighted_label}."
        )
    return (
        f"Naive counts {count} sources and says {naive_label}. Weighted adds up {total_weight:.1f} quality points, "
        f"which pushes the result to {weighted_label}."
    )


def reset_sources(source_types: list[str]) -> None:
    st.session_state.sources = [{"type": source_type, "weight": SOURCE_WEIGHTS[source_type]} for source_type in source_types]


ensure_state()

st.markdown(
    """
    <div class="hero">
        <h1>Confidence Scoring Simulator</h1>
        <p>Compare a naive source-count model against a weighted source-quality model for AI research on loyalty programs.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

with st.sidebar:
    st.markdown("### Add a Source")
    selected_source = st.selectbox("Source type", SOURCE_OPTIONS, key="source_picker")
    if st.button("Add Source", use_container_width=True):
        st.session_state.sources.append({"type": selected_source, "weight": SOURCE_WEIGHTS[selected_source]})
        st.rerun()

    st.markdown("### Scenario Presets")
    preset_cols = st.columns(1)
    if st.button("All Forums", use_container_width=True):
        reset_sources(PRESETS["All Forums"])
        st.rerun()
    if st.button("Mixed Sources", use_container_width=True):
        reset_sources(PRESETS["Mixed Sources"])
        st.rerun()
    if st.button("Official Heavy", use_container_width=True):
        reset_sources(PRESETS["Official Heavy"])
        st.rerun()
    if st.button("Clear All", use_container_width=True):
        st.session_state.sources = []
        st.rerun()

sources_df = pd.DataFrame(st.session_state.sources)
if not sources_df.empty:
    sources_df.index = range(1, len(sources_df) + 1)
    sources_df.index.name = "#"
    sources_df = sources_df.rename(columns={"type": "Source Type", "weight": "Weight"})
    total_weight = float(sources_df["Weight"].sum())
else:
    sources_df = pd.DataFrame(columns=["Source Type", "Weight"])
    total_weight = 0.0

source_count = len(st.session_state.sources)
naive_label, naive_numeric = score_naive(source_count)
weighted_label = score_weighted(total_weight)

st.markdown('<div class="section-title">Current Sources</div>', unsafe_allow_html=True)
if sources_df.empty:
    st.markdown(
        '<div class="callout">No sources yet. Add a source from the sidebar or load a scenario preset to start the comparison.</div>',
        unsafe_allow_html=True,
    )
else:
    table_view = sources_df.copy()
    table_view["Weight"] = table_view["Weight"].map(lambda value: f"{value:.1f}")
    st.dataframe(table_view, use_container_width=True, hide_index=False)

st.write("")

left, right = st.columns(2)
with left:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Naive Score</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{source_count} sources</div>', unsafe_allow_html=True)
    st.markdown(badge_html(naive_label), unsafe_allow_html=True)
    st.caption("Counts sources only, regardless of quality.")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Weighted Score</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{total_weight:.1f} points</div>', unsafe_allow_html=True)
    st.markdown(badge_html(weighted_label), unsafe_allow_html=True)
    st.caption("Rewards higher-trust sources more heavily.")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

chart_df = pd.DataFrame(
    {
        "System": ["Naive", "Weighted"],
        "Value": [naive_numeric, total_weight],
        "Display": [source_count, round(total_weight, 1)],
    }
)

chart = (
    alt.Chart(chart_df)
    .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x=alt.X("System:N", axis=alt.Axis(labelColor="#d7fdf8", titleColor="#d7fdf8")),
        y=alt.Y("Value:Q", axis=alt.Axis(labelColor="#d7fdf8", titleColor="#d7fdf8", gridColor="rgba(45, 212, 191, 0.15)")),
        color=alt.value("#2dd4bf"),
        tooltip=["System:N", "Value:Q", "Display:Q"],
    )
    .properties(height=320, background="#08161c")
)

text = chart.mark_text(dy=-12, color="#e9fffd", fontSize=14, fontWeight="bold").encode(
    text=alt.Text("Display:Q")
)

st.markdown('<div class="section-title">Score Comparison</div>', unsafe_allow_html=True)
st.altair_chart(chart + text, use_container_width=True)

st.markdown('<div class="section-title">Why the scores differ</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="callout">{explain_difference(source_count, total_weight, naive_label, weighted_label)}</div>',
    unsafe_allow_html=True,
)
