import html as html_lib
import re
import unicodedata

import altair as alt
import duckdb
import joblib
import numpy as np
import pandas as pd
import streamlit as st


# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Football IQ | Transfer Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# THEME
# =====================================================
NIGHT = "#0B1B2B"
SURFACE = "#12263A"
LINE = "#24415C"
CHALK = "#EAF1F7"
MUTED = "#8FA6BA"
GOLD = "#F5B83D"
BLUE = "#5BB0FF"
CORAL = "#FF7A66"
FIELD = "#0E2033"


# =====================================================
# CUSTOM CSS
# =====================================================
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=DM+Sans:wght@400;500;700&display=swap');

html, body, .stApp, [class*="css"] {{ font-family:'DM Sans',sans-serif; }}
h1,h2,h3,h4 {{ font-family:'Barlow Condensed',sans-serif !important; color:{CHALK} !important; }}
h2 {{ font-size:2.1rem !important; font-weight:700 !important; }}
h3 {{ font-size:1.5rem !important; font-weight:700 !important; }}
h4 {{ font-size:1.2rem !important; font-weight:600 !important; color:{MUTED} !important; }}
p,label,li {{ color:#B9C9D8; }}
#MainMenu,footer {{ visibility:hidden; }}
header[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stToolbar"],[data-testid="stAppDeployButton"],.stDeployButton {{ display:none !important; }}
.stApp {{ background:radial-gradient(ellipse 70% 40% at 85% -5%,rgba(91,176,255,.13),transparent 60%),radial-gradient(ellipse 50% 35% at 0% 0%,rgba(245,184,61,.07),transparent 60%),{NIGHT}; }}
.block-container {{ max-width:1280px; padding-top:1.6rem; padding-bottom:3rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background:#091624; border-right:1px solid {LINE}; }}
.brand {{ font-family:'Barlow Condensed'; font-size:30px; font-weight:800; color:{CHALK}; line-height:1; }}
.brand b {{ color:{GOLD}; }}
.brand-sub {{ color:{MUTED}; font-size:13px; margin-top:4px; }}
.side-row {{ display:flex; justify-content:space-between; padding:9px 0; border-bottom:1px solid {LINE}55; font-size:14px; }}
.side-row span:first-child {{ color:{MUTED}; }}
.side-row span:last-child {{ color:{CHALK}; font-weight:500; text-align:right; }}
.side-stat {{ background:{SURFACE}; border:1px solid {LINE}; border-radius:12px; padding:14px 16px; margin-bottom:10px; }}
.side-stat .v {{ font-family:'Barlow Condensed'; font-size:32px; font-weight:700; color:{GOLD}; line-height:1.05; }}
.side-stat .l {{ font-size:13px; color:{MUTED}; }}

/* Hero with floating football */
.hero {{ position:relative; overflow:hidden; background:linear-gradient(115deg,#0F2A40 0%,#0C2236 60%,#0B2A33 100%); border:1px solid {LINE}; border-radius:20px; padding:44px 48px; margin-bottom:26px; }}
.hero::before {{ content:""; position:absolute; top:0; bottom:0; right:170px; width:2px; background:rgba(234,241,247,.10); }}
.hero::after {{ content:"⚽"; position:absolute; top:50%; right:170px; width:300px; height:300px; transform:translate(50%,-50%); display:flex; align-items:center; justify-content:center; font-size:180px; background:radial-gradient(circle at 40% 35%,rgba(245,184,61,.16),rgba(91,176,255,.08) 55%,transparent 78%); border:2px solid rgba(245,184,61,.25); border-radius:50%; box-shadow:0 0 30px rgba(245,184,61,.08),inset 0 0 35px rgba(91,176,255,.10); animation:footballFloat 4s ease-in-out infinite; z-index:0; pointer-events:none; }}
@keyframes footballFloat {{ 0%,100% {{ transform:translate(50%,-50%) translateY(0); }} 50% {{ transform:translate(50%,-50%) translateY(-12px); }} }}
.hero > * {{ position:relative; z-index:1; }}
.hero-title {{ font-family:'Barlow Condensed'; font-weight:800; font-size:clamp(40px,5.4vw,68px); line-height:.98; color:#fff; margin:0; }}
.hero-title em {{ font-style:normal; color:{GOLD}; }}
.hero-sub {{ color:#A9BDCD; font-size:17px; line-height:1.65; max-width:560px; margin-top:16px; }}
.hero-stats {{ display:flex; gap:34px; margin-top:28px; flex-wrap:wrap; }}
.hero-stats div {{ font-size:13px; color:{MUTED}; }}
.hero-stats b {{ display:block; font-family:'Barlow Condensed'; font-size:30px; color:{CHALK}; font-weight:700; line-height:1.1; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap:10px; border-bottom:none !important; padding:6px 0 14px; }}
.stTabs button[role="tab"] {{ height:52px; padding:0 26px; background:{SURFACE} !important; border:1px solid {LINE} !important; border-radius:14px !important; cursor:pointer; }}
.stTabs button[role="tab"] * {{ color:{MUTED} !important; font-family:'Barlow Condensed',sans-serif !important; font-size:20px !important; font-weight:700 !important; }}
.stTabs button[role="tab"]:hover {{ border-color:{GOLD} !important; }}
.stTabs button[role="tab"][aria-selected="true"] {{ background:{GOLD} !important; border-color:{GOLD} !important; }}
.stTabs button[role="tab"][aria-selected="true"] * {{ color:#1A1203 !important; }}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"] {{ display:none !important; }}
.lede {{ color:{MUTED}; font-size:15px; margin:-6px 0 20px; max-width:640px; }}

/* Forms and fields */
div[data-testid="stForm"] {{ background:{SURFACE}; border:1px solid {LINE}; border-radius:18px; padding:26px 28px; }}
label p {{ font-size:13.5px !important; font-weight:500; color:{MUTED} !important; }}
div[data-baseweb="input"],div[data-baseweb="input"]>div,div[data-baseweb="base-input"],div[data-baseweb="select"]>div,div[data-baseweb="textarea"],div[data-testid="stNumberInputContainer"] {{ background-color:{FIELD} !important; border-color:{LINE} !important; }}
div[data-baseweb="input"],div[data-baseweb="select"]>div,div[data-testid="stNumberInputContainer"] {{ border-radius:10px !important; }}
div[data-baseweb="input"] input,div[data-baseweb="base-input"] input {{ background:transparent !important; color:{CHALK} !important; }}
div[data-baseweb="select"] * {{ color:{CHALK} !important; }}
div[data-baseweb="input"]:focus-within,div[data-baseweb="select"]:focus-within>div,div[data-testid="stNumberInputContainer"]:focus-within {{ border-color:{GOLD} !important; box-shadow:0 0 0 1px {GOLD} !important; }}

/* Submit buttons */
button[data-testid^="stBaseButton"],div[data-testid="stFormSubmitButton"] button,.stButton>button {{ background:linear-gradient(180deg,#FFCB52 0%,#F5B83D 55%,#E9A61F 100%) !important; border:1px solid #FFD97A !important; border-radius:14px !important; min-height:58px !important; padding:12px 24px !important; box-shadow:0 6px 20px rgba(245,184,61,.28),inset 0 1px 0 rgba(255,255,255,.45) !important; transition:transform .15s ease,box-shadow .15s ease,filter .15s ease; }}
button[data-testid^="stBaseButton"] *,div[data-testid="stFormSubmitButton"] button *,.stButton>button * {{ color:#1A1203 !important; -webkit-text-fill-color:#1A1203 !important; font-family:'Barlow Condensed',sans-serif !important; font-size:23px !important; font-weight:800 !important; letter-spacing:.6px; }}
button[data-testid^="stBaseButton"]:hover,div[data-testid="stFormSubmitButton"] button:hover,.stButton>button:hover {{ transform:translateY(-2px); filter:brightness(1.06); box-shadow:0 12px 28px rgba(245,184,61,.42) !important; }}
button[data-testid^="stBaseButton"]:focus-visible {{ outline:2px solid {CHALK} !important; outline-offset:3px; }}

/* Number-input step buttons keep the dark field style */
div[data-testid="stNumberInput"] button[data-testid^="stBaseButton"],div[data-testid="stNumberInput"] button {{ background:{FIELD} !important; border:none !important; box-shadow:none !important; min-height:0 !important; padding:0 8px !important; transform:none !important; filter:none !important; }}
div[data-testid="stNumberInput"] button * {{ color:{CHALK} !important; -webkit-text-fill-color:{CHALK} !important; font-size:16px !important; }}

/* Metrics */
div[data-testid="stMetric"] {{ background:{SURFACE}; border:1px solid {LINE}; border-radius:14px; padding:18px 20px; }}
div[data-testid="stMetricLabel"] p {{ color:{MUTED} !important; font-size:13.5px; }}
div[data-testid="stMetricValue"] {{ font-family:'Barlow Condensed'; color:{CHALK}; font-weight:700; font-size:2.3rem; }}

/* Avatars (photo or initials) */
.avatar,.avatar-fallback {{ flex:0 0 auto; object-fit:cover; object-position:top center; border-radius:14px; border:1px solid {LINE}; background:#0A1826; }}
.avatar-fallback {{ display:flex; align-items:center; justify-content:center; color:{GOLD}; font-family:'Barlow Condensed'; font-weight:800; background:linear-gradient(145deg,#12304A,#0A1826); border-color:rgba(245,184,61,.45); }}
.avatar.lg,.avatar-fallback.lg {{ width:96px; height:112px; font-size:38px; }}
.avatar.md,.avatar-fallback.md {{ width:84px; height:98px; font-size:32px; }}
.avatar.sm,.avatar-fallback.sm {{ width:64px; height:76px; font-size:26px; }}

/* Name styling (always visible) */
.pname {{ font-family:'Barlow Condensed',sans-serif; font-weight:800; color:#FFFFFF !important; line-height:1.05; overflow-wrap:anywhere; }}
.pname.lg {{ font-size:36px; }}
.pname.md {{ font-size:28px; }}
.pname.sm {{ font-size:25px; }}
.match-chip {{ display:inline-block; margin-top:8px; padding:3px 10px; border-radius:20px; font-size:11.5px; font-weight:700; }}
.match-chip.ok {{ background:rgba(110,214,140,.12); color:#7FE0A0; border:1px solid rgba(110,214,140,.35); }}
.match-chip.no {{ background:rgba(143,166,186,.12); color:{MUTED}; border:1px solid {LINE}; }}

/* Valuation report */
.report {{ background:linear-gradient(135deg,#14304A,#0F2438); border:1px solid {LINE}; border-radius:20px; padding:30px 34px; margin-top:8px; }}
.report-top {{ display:flex; justify-content:space-between; align-items:flex-start; gap:20px; flex-wrap:wrap; }}
.report-player {{ display:flex; align-items:center; gap:18px; min-width:0; }}
.report-meta {{ color:{MUTED}; font-size:14px; margin-top:6px; }}
.report-club {{ color:{GOLD}; font-size:15px; font-weight:700; margin-top:4px; }}
.chip {{ display:inline-block; padding:5px 13px; border-radius:20px; font-size:13px; font-weight:700; background:rgba(245,184,61,.14); color:{GOLD}; border:1px solid rgba(245,184,61,.35); }}
.report-value {{ font-family:'Barlow Condensed'; font-weight:800; font-size:clamp(64px,9vw,104px); color:{GOLD}; line-height:1; margin:14px 0 4px; }}
.report-exact,.note {{ color:{MUTED}; font-size:13.5px; }}
.track {{ position:relative; height:10px; background:#0A1826; border-radius:8px; margin:22px 0 8px; overflow:hidden; }}
.track-fill {{ height:100%; border-radius:8px; background:linear-gradient(90deg,{BLUE},{GOLD}); }}
.track-legend {{ display:flex; justify-content:space-between; font-size:12.5px; color:{MUTED}; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:12px; margin-top:22px; }}
.tile {{ background:#0B1D2F; border:1px solid {LINE}; border-radius:12px; padding:14px 16px; }}
.tile .l {{ font-size:12.5px; color:{MUTED}; }}
.tile .v {{ font-family:'Barlow Condensed'; font-size:26px; font-weight:700; color:{CHALK}; }}

/* Head-to-head */
.h2h-broadcast {{ display:grid; grid-template-columns:minmax(0,1fr) 76px minmax(0,1fr); gap:12px; align-items:stretch; margin-top:18px; }}
.broadcast-card {{ min-width:0; border-radius:18px; padding:22px; background:linear-gradient(145deg,#142F49,#0C2032); border:1px solid {LINE}; }}
.broadcast-card.a {{ border-top:4px solid {BLUE}; }}
.broadcast-card.b {{ border-top:4px solid {CORAL}; }}
.broadcast-card.win {{ border:2px solid {GOLD}; background:linear-gradient(145deg,#1A3B50,#10283B); box-shadow:0 0 26px rgba(245,184,61,.13); }}
.side-tag {{ font-size:12.5px; font-weight:700; margin-bottom:14px; }}
.broadcast-card.a .side-tag {{ color:{BLUE}; }}
.broadcast-card.b .side-tag {{ color:{CORAL}; }}
.side-profile {{ display:flex; align-items:center; gap:16px; margin-bottom:18px; min-width:0; }}
.side-player-meta {{ min-width:0; flex:1; }}
.club-line {{ display:flex; align-items:center; gap:9px; margin-top:10px; }}
.club-monogram {{ width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:50%; background:{NIGHT}; border:1px solid {GOLD}; color:{GOLD}; font-family:'Barlow Condensed'; font-weight:800; font-size:12px; flex-shrink:0; }}
.club-name {{ color:#AFC0CE; font-size:13px; overflow-wrap:anywhere; }}
.broadcast-value {{ font-family:'Barlow Condensed'; font-size:clamp(40px,5vw,64px); font-weight:800; line-height:1.05; }}
.broadcast-card.a .broadcast-value {{ color:{BLUE}; }}
.broadcast-card.b .broadcast-value {{ color:{CORAL}; }}
.vs-wrap {{ display:flex; align-items:center; justify-content:center; }}
.vs-mark {{ width:66px; height:66px; display:flex; align-items:center; justify-content:center; border-radius:50%; background:linear-gradient(145deg,#FFD66B,#E9A61F); color:#1A1203; border:5px solid {NIGHT}; outline:1px solid rgba(245,184,61,.5); font-family:'Barlow Condensed'; font-size:30px; font-weight:800; box-shadow:0 0 25px rgba(245,184,61,.2); }}
.higher-badge {{ display:inline-block; margin-top:12px; background:rgba(245,184,61,.15); color:{GOLD}; border:1px solid rgba(245,184,61,.4); padding:5px 11px; border-radius:20px; font-size:12px; font-weight:800; }}

/* Winner spotlight */
.winner-spotlight {{ margin-top:22px; padding:23px 26px; border-radius:18px; background:linear-gradient(110deg,#263D43,#142D3B); border:1px solid rgba(245,184,61,.4); box-shadow:0 8px 30px rgba(0,0,0,.16); }}
.winner-kicker {{ font-size:13px; font-weight:800; color:{GOLD}; margin-bottom:16px; }}
.winner-main {{ display:flex; align-items:center; gap:17px; flex-wrap:wrap; }}
.winner-sub {{ font-size:14px; color:#AFC0CE; margin-top:4px; }}
.winner-value {{ margin-left:auto; font-family:'Barlow Condensed'; font-size:42px; font-weight:800; color:{GOLD}; }}
.winner-note {{ font-size:14px; color:#AFC0CE; margin-top:13px; }}
.winner-note b {{ color:{CHALK}; }}

/* Stat breakdown */
.srow-head {{ display:flex; justify-content:space-between; gap:16px; margin:6px 0 4px; }}
.srow-head .nm {{ font-family:'Barlow Condensed'; font-size:24px; font-weight:800; overflow-wrap:anywhere; }}
.srow-head .nm.a {{ color:{BLUE}; }}
.srow-head .nm.b {{ color:{CORAL}; text-align:right; }}
.srow {{ margin:14px 0; }}
.srow .t {{ display:flex; justify-content:space-between; font-size:13.5px; color:{MUTED}; margin-bottom:6px; }}
.srow .t b {{ color:{CHALK}; font-family:'Barlow Condensed'; font-size:19px; }}
.bars {{ display:grid; grid-template-columns:1fr 1fr; gap:4px; }}
.bar-l,.bar-r {{ height:9px; background:#0A1826; border-radius:6px; display:flex; }}
.bar-l {{ justify-content:flex-end; }}
.bar-l i {{ background:{BLUE}; border-radius:6px; }}
.bar-r i {{ background:{CORAL}; border-radius:6px; }}

/* EXTRA ANALYTICS AND REPORT DETAILS */
.analytics-filter-note {{ color:{MUTED}; font-size:12px; }}
.detail-pill {{ display:inline-block; padding:6px 10px; margin:4px 5px 0 0; border:1px solid {LINE}; border-radius:20px; color:{MUTED}; background:#0B1D2F; font-size:12px; }}
.history-heading {{ font-family:'Barlow Condensed'; font-size:24px; color:{CHALK}; font-weight:700; margin:20px 0 8px; }}
.leader-name {{ color:{CHALK}; font-weight:700; }}

hr {{ border-color:{LINE} !important; }}
.foot {{ text-align:center; color:#5E768A; font-size:13px; padding:26px 0 4px; }}

@media(max-width:760px) {{
    .hero {{ padding:30px 24px; }}
    .hero::after {{ width:140px; height:140px; font-size:85px; right:70px; opacity:.55; }}
    .h2h-broadcast {{ grid-template-columns:1fr; }}
    .vs-wrap {{ min-height:54px; }}
    .vs-mark {{ width:55px; height:55px; }}
    .winner-value {{ margin-left:0; width:100%; }}
    .pname.lg {{ font-size:30px; }}
}}
@media(prefers-reduced-motion:reduce) {{ .hero::after {{ animation:none; }} }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================
def h(markup: str) -> str:
    """Collapse HTML so Markdown never treats indents as code blocks."""
    return " ".join(line.strip() for line in markup.splitlines() if line.strip())


def esc(value) -> str:
    return html_lib.escape(str(value))


def fmt_eur(value: float) -> str:
    if value >= 1e6:
        return f"€{value / 1e6:.1f}M"
    if value >= 1e3:
        return f"€{value / 1e3:.0f}K"
    return f"€{value:,.0f}"


def value_tier(value: float) -> str:
    if value < 1e6:
        return "Emerging talent"
    if value < 5e6:
        return "Squad player"
    if value < 20e6:
        return "First-team starter"
    if value < 50e6:
        return "Star player"
    return "World-class"


def plain_text(name: str) -> str:
    """Lowercase, strip accents, keep only letters and digits separated by single spaces."""
    decomposed = unicodedata.normalize("NFKD", str(name).casefold())
    no_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", no_accents).strip()


def clean_profile_value(value, fallback: str) -> str:
    if value is None or pd.isna(value) or not str(value).strip():
        return fallback
    return str(value).strip()


def initials(name: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", str(name))
    if not words:
        return "FC"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[-1][0]).upper()


def avatar_html(image_url: str, name: str, size: str) -> str:
    """Player photo if available, otherwise a gold initials badge."""
    if image_url.startswith("https://"):
        return (
            f'<img class="avatar {size}" src="{esc(image_url)}" '
            f'alt="{esc(name)}" loading="lazy" referrerpolicy="no-referrer">'
        )
    return f'<div class="avatar-fallback {size}">{esc(initials(name))}</div>'


def stat_row(label: str, v1: float, v2: float) -> str:
    total = (v1 + v2) or 1
    p1, p2 = v1 / total * 100, v2 / total * 100
    return h(f"""
    <div class="srow">
      <div class="t"><b>{v1:g}</b><span>{esc(label)}</span><b>{v2:g}</b></div>
      <div class="bars">
        <div class="bar-l"><i style="width:{p1}%"></i></div>
        <div class="bar-r"><i style="width:{p2}%"></i></div>
      </div>
    </div>
    """)


def show_chart(chart: alt.Chart, height: int = 300):
    styled = (
        chart.properties(height=height, background="transparent")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=MUTED,
            titleColor=MUTED,
            gridColor=LINE,
            domainColor=LINE,
            tickColor=LINE,
            labelFont="DM Sans",
            titleFont="DM Sans",
            labelFontSize=13,
        )
        .configure_legend(labelColor=MUTED, titleColor=MUTED)
    )
    st.altair_chart(styled, use_container_width=True, theme=None)


# =====================================================
# LOAD MODEL AND DATA
# =====================================================
@st.cache_resource
def load_model():
    return joblib.load("models/best_model.pkl")


@st.cache_data
def load_analytics_data():
    return pd.read_csv("dataset/training_data.csv")


@st.cache_data
def load_player_profiles():
    connection = duckdb.connect(
        "dataset/transfermarkt-datasets.duckdb",
        read_only=True,
    )
    try:
        profiles = connection.execute("""
            SELECT player_id, name, image_url, current_club_name, last_season
            FROM players
            WHERE name IS NOT NULL
            ORDER BY last_season DESC NULLS LAST
        """).df()
    finally:
        connection.close()

    profiles["plain_name"] = profiles["name"].map(plain_text)
    profiles["squashed_name"] = profiles["plain_name"].str.replace(" ", "", regex=False)
    return profiles


def find_player_profile(player_name: str):
    """Exact match first, then every typed word must appear in the player's name.
    Players are sorted by most recent season, so active players win ties."""
    typed = plain_text(player_name)
    if not typed:
        return None

    profiles = load_player_profiles()
    squashed = typed.replace(" ", "")

    exact = profiles[profiles["squashed_name"] == squashed]
    exact_match = not exact.empty
    matches = exact

    if not exact_match:
        mask = pd.Series(True, index=profiles.index)
        for token in typed.split():
            mask &= profiles["plain_name"].str.contains(token, regex=False)
        matches = profiles[mask]

    if matches.empty:
        return None

    row = matches.iloc[0]
    return {
        "player_id": int(row.get("player_id")),
        "name": clean_profile_value(row.get("name"), player_name),
        "image_url": clean_profile_value(row.get("image_url"), ""),
        "club": clean_profile_value(row.get("current_club_name"), "Club not listed"),
        "exact": exact_match,
    }


@st.cache_data
def load_player_value_history(player_id: int):
    """Return a player's historical Transfermarkt valuation timeline."""
    connection = duckdb.connect(
        "dataset/transfermarkt-datasets.duckdb",
        read_only=True,
    )
    try:
        history = connection.execute(
            """
            SELECT date, market_value_in_eur
            FROM player_valuations
            WHERE player_id = ?
              AND market_value_in_eur IS NOT NULL
              AND market_value_in_eur > 0
            ORDER BY date
            """,
            [int(player_id)],
        ).df()
    finally:
        connection.close()

    if not history.empty:
        history["date"] = pd.to_datetime(history["date"], errors="coerce")
        history = history.dropna(subset=["date"])
        history["value_millions"] = history["market_value_in_eur"] / 1_000_000
    return history


@st.cache_data
def load_reference_values():
    return load_analytics_data()["market_value_eur"].dropna().to_numpy()


try:
    model = load_model()
except Exception as error:
    st.error(f"Unable to load the trained model: {error}")
    st.stop()

try:
    ref_values = load_reference_values()
except Exception:
    ref_values = None


# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown(
        h("""
        <div class="brand">FOOTBALL <b>IQ</b></div>
        <div class="brand-sub">Transfer intelligence platform</div>
        """),
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("#### How it works")
    st.markdown(
        h("""
        <div class="side-row"><span>Algorithm</span><span>Gradient Boosting</span></div>
        <div class="side-row"><span>Data</span><span>Transfermarkt history</span></div>
        <div class="side-row"><span>Predicts</span><span>Market value (EUR)</span></div>
        """),
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("#### Model performance")
    st.markdown(
        h("""
        <div class="side-stat"><div class="v">0.445</div><div class="l">Test R² score</div></div>
        <div class="side-stat"><div class="v">€2.33M</div><div class="l">Test mean absolute error</div></div>
        """),
        unsafe_allow_html=True,
    )
    st.caption("Baseline performance. Individual predictions can be off by a wide margin.")
    st.divider()
    st.markdown("#### Included tools")
    st.caption("Player valuation · Head-to-head comparison · Historical trends · CSV exports")
    st.caption("Dataset is historical, not a live transfer-market feed.")
    st.divider()
    st.caption("Built with Python, scikit-learn, DuckDB and Streamlit")


# =====================================================
# HERO AND NAVIGATION
# =====================================================
st.markdown(
    h("""
    <div class="hero">
      <div class="hero-title">What is a player<br>really <em>worth?</em></div>
      <div class="hero-sub">
        Enter a player's profile and recent form. Football IQ estimates a market value
        from historical Transfermarkt data, compares two players, and shows how the
        market is distributed.
      </div>
      <div class="hero-stats">
        <div><b>3</b>tools in one place</div>
        <div><b>11</b>inputs per player</div>
        <div><b>EUR</b>values in euros</div>
      </div>
    </div>
    """),
    unsafe_allow_html=True,
)

tab_predict, tab_compare, tab_analytics = st.tabs([
    "⚡ Value a player",
    "⚔️ Compare players",
    "📊 Market trends",
])


# =====================================================
# TAB 1: PLAYER PREDICTION
# =====================================================
with tab_predict:
    st.header("Estimate a player's market value")
    st.markdown(
        '<div class="lede">Type a player name to pull their photo and club, '
        "then enter their last 12 months of stats.</div>",
        unsafe_allow_html=True,
    )

    with st.form("prediction_form"):
        st.markdown("#### Player profile")
        player_name = st.text_input("Player name", "Kylian Mbappe")

        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Age", 15, 45, 23)
        height = c2.number_input("Height (cm)", 140, 220, 180)
        foot = c3.selectbox("Preferred foot", ["right", "left", "both"])

        c1, c2 = st.columns(2)
        position = c1.selectbox("Position", ["Attack", "Midfield", "Defender", "Goalkeeper"])
        sub_position = c2.text_input("Sub-position", "Centre-Forward")

        st.markdown("#### Form in the last 365 days")
        c1, c2, c3 = st.columns(3)
        goals = c1.number_input("Goals", 0, 100, 20)
        assists = c2.number_input("Assists", 0, 100, 10)
        minutes = c3.number_input("Minutes played", 0, 10000, 2500)

        c1, c2 = st.columns(2)
        yellow_cards = c1.number_input("Yellow cards", 0, 30, 3)
        red_cards = c2.number_input("Red cards", 0, 10, 0)

        st.write("")
        predict_button = st.form_submit_button(
            "Estimate market value",
            use_container_width=True,
        )

    if predict_button:
        if not player_name.strip():
            st.error("Enter a player name to continue.")
        else:
            player_data = pd.DataFrame([{
                "age": age,
                "height_in_cm": height,
                "goals_last_365_days": goals,
                "assists_last_365_days": assists,
                "minutes_last_365_days": minutes,
                "yellow_cards_last_365_days": yellow_cards,
                "red_cards_last_365_days": red_cards,
                "valuation_year": 2026,
                "position": position,
                "sub_position": sub_position,
                "foot": foot,
            }])
            try:
                predicted_value = max(0, np.expm1(model.predict(player_data)[0]))

                try:
                    found_profile = find_player_profile(player_name)
                    lookup_failed = False
                except Exception:
                    found_profile = None
                    lookup_failed = True

                st.session_state["prediction_result"] = {
                    "name": player_name.strip(),
                    "value": float(predicted_value),
                    "age": age,
                    "height": height,
                    "position": position,
                    "sub_position": sub_position,
                    "foot": foot,
                    "goals": goals,
                    "assists": assists,
                    "minutes": minutes,
                    "yellow_cards": yellow_cards,
                    "red_cards": red_cards,
                    "profile": found_profile,
                    "lookup_failed": lookup_failed,
                }
            except Exception as error:
                st.error(f"Prediction failed: {error}")

    if "prediction_result" in st.session_state:
        r = st.session_state["prediction_result"]
        profile = r.get("profile")

        pct = None
        if ref_values is not None and len(ref_values):
            pct = float((ref_values < r["value"]).mean() * 100)
        pct_w = 50 if pct is None else min(max(pct, 2), 98)
        context = (
            f"Valued above <b>{pct:.0f}%</b> of historical records in the dataset."
            if pct is not None else ""
        )
        per90 = (r["goals"] + r["assists"]) / max(r["minutes"], 1) * 90

        if profile:
            display_name = clean_profile_value(profile.get("name"), r["name"])
            club = clean_profile_value(profile.get("club"), "Club not listed")
            image_url = clean_profile_value(profile.get("image_url"), "")
            match_chip = '<span class="match-chip ok">✓ Matched on Transfermarkt</span>'
        else:
            display_name = r["name"]
            club = "No club on record"
            image_url = ""
            match_chip = '<span class="match-chip no">No Transfermarkt match</span>'

        st.markdown(
            h(f"""
            <div class="report">
              <div class="report-top">
                <div class="report-player">
                  {avatar_html(image_url, display_name, "lg")}
                  <div>
                    <div class="pname lg">{esc(display_name)}</div>
                    <div class="report-meta">{esc(r['position'])} · {r['age']} years old</div>
                    <div class="report-club">{esc(club)}</div>
                    {match_chip}
                  </div>
                </div>
                <span class="chip">{value_tier(r['value'])}</span>
              </div>
              <div class="report-value">{fmt_eur(r['value'])}</div>
              <div class="report-exact">Estimated market value (€{r['value']:,.0f}). {context}</div>
              <div class="track"><div class="track-fill" style="width:{pct_w}%"></div></div>
              <div class="track-legend"><span>Lowest valued</span><span>Highest valued</span></div>
              <div class="tiles">
                <div class="tile"><div class="l">Goals</div><div class="v">{r['goals']}</div></div>
                <div class="tile"><div class="l">Assists</div><div class="v">{r['assists']}</div></div>
                <div class="tile"><div class="l">Minutes</div><div class="v">{r['minutes']:,}</div></div>
                <div class="tile"><div class="l">Goal contributions / 90</div><div class="v">{per90:.2f}</div></div>
              </div>
              <div class="note">This is a machine learning estimate, not an official market value or transfer fee.</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        if r.get("lookup_failed"):
            st.caption(
                "Valuation worked, but the player database could not be read. "
                "Check that dataset/transfermarkt-datasets.duckdb exists."
            )
        elif not profile:
            st.caption(
                "No player with that name was found. Try the full name, "
                "for example 'Erling Haaland'."
            )

        # Downloadable prediction summary
        prediction_export = pd.DataFrame([{
            "player_name": r["name"],
            "estimated_market_value_eur": round(r["value"], 2),
            "age": r["age"],
            "height_cm": r["height"],
            "position": r["position"],
            "sub_position": r["sub_position"],
            "preferred_foot": r["foot"],
            "goals_last_365_days": r["goals"],
            "assists_last_365_days": r["assists"],
            "minutes_last_365_days": r["minutes"],
            "yellow_cards_last_365_days": r["yellow_cards"],
            "red_cards_last_365_days": r["red_cards"],
        }])
        st.download_button(
            "Download this valuation (CSV)",
            data=prediction_export.to_csv(index=False).encode("utf-8"),
            file_name="football_iq_player_valuation.csv",
            mime="text/csv",
            key="download_prediction_csv",
        )

        # Historical value timeline, when the local profile matched a player ID
        if profile and profile.get("player_id") is not None:
            try:
                history = load_player_value_history(profile["player_id"])
                if not history.empty:
                    st.markdown('<div class="history-heading">Historical market value</div>', unsafe_allow_html=True)
                    history_chart = alt.Chart(history).mark_line(
                        color=GOLD,
                        strokeWidth=3,
                        point=alt.OverlayMarkDef(color=BLUE, size=45),
                    ).encode(
                        x=alt.X("date:T", title=None),
                        y=alt.Y("value_millions:Q", title="Market value (€M)"),
                        tooltip=[
                            alt.Tooltip("date:T", title="Valuation date"),
                            alt.Tooltip("market_value_in_eur:Q", title="Market value (€)", format=",.0f"),
                        ],
                    )
                    show_chart(history_chart, height=250)
            except Exception as history_error:
                st.caption(f"Historical valuation timeline is unavailable: {history_error}")


# =====================================================
# TAB 2: PLAYER COMPARISON
# =====================================================
with tab_compare:
    st.header("Head-to-head comparison")
    st.markdown(
        '<div class="lede">Compare two players based on their recent attacking performance.</div>',
        unsafe_allow_html=True,
    )

    with st.form("comparison_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f'<h3 style="color:{BLUE} !important">🔵 Player one</h3>',
                unsafe_allow_html=True,
            )
            name1 = st.text_input("Name", "Kylian Mbappe", key="n1")
            age1 = st.number_input("Age", 15, 45, 27, key="a1")
            height1 = st.number_input("Height (cm)", 140, 220, 178, key="h1")
            position1 = st.selectbox(
                "Position", ["Attack", "Midfield", "Defender", "Goalkeeper"], key="pos1"
            )
            sub_position1 = st.text_input("Sub-position", "Centre-Forward", key="sub1")
            foot1 = st.selectbox("Preferred foot", ["right", "left", "both"], key="foot1")
            goals1 = st.number_input("Goals (last 365 days)", 0, 100, 30, key="g1")
            assists1 = st.number_input("Assists (last 365 days)", 0, 100, 17, key="as1")
            minutes1 = st.number_input("Minutes played", 0, 10000, 2500, key="m1")
            yellow1 = st.number_input("Yellow cards", 0, 30, 3, key="y1")
            red1 = st.number_input("Red cards", 0, 10, 0, key="r1")

        with col2:
            st.markdown(
                f'<h3 style="color:{CORAL} !important">🔴 Player two</h3>',
                unsafe_allow_html=True,
            )
            name2 = st.text_input("Name", "Erling Haaland", key="n2")
            age2 = st.number_input("Age", 15, 45, 25, key="a2")
            height2 = st.number_input("Height (cm)", 140, 220, 194, key="h2")
            position2 = st.selectbox(
                "Position", ["Attack", "Midfield", "Defender", "Goalkeeper"], key="pos2"
            )
            sub_position2 = st.text_input("Sub-position", "Centre-Forward", key="sub2")
            foot2 = st.selectbox("Preferred foot", ["right", "left", "both"], key="foot2")
            goals2 = st.number_input("Goals (last 365 days)", 0, 100, 30, key="g2")
            assists2 = st.number_input("Assists (last 365 days)", 0, 100, 10, key="as2")
            minutes2 = st.number_input("Minutes played", 0, 10000, 2500, key="m2")
            yellow2 = st.number_input("Yellow cards", 0, 30, 2, key="y2")
            red2 = st.number_input("Red cards", 0, 10, 0, key="r2")

        st.caption("Enter each player's own attributes. The model uses these inputs separately for each estimate.")
        st.write("")
        compare_button = st.form_submit_button(
            "Compare players",
            use_container_width=True,
        )

    if compare_button:
        if not name1.strip() or not name2.strip():
            st.error("Enter both player names to compare.")
        else:
            comparison_data = pd.DataFrame([
                {
                    "age": age1,
                    "height_in_cm": height1,
                    "goals_last_365_days": goals1,
                    "assists_last_365_days": assists1,
                    "minutes_last_365_days": minutes1,
                    "yellow_cards_last_365_days": yellow1,
                    "red_cards_last_365_days": red1,
                    "valuation_year": 2026,
                    "position": position1,
                    "sub_position": sub_position1,
                    "foot": foot1,
                },
                {
                    "age": age2,
                    "height_in_cm": height2,
                    "goals_last_365_days": goals2,
                    "assists_last_365_days": assists2,
                    "minutes_last_365_days": minutes2,
                    "yellow_cards_last_365_days": yellow2,
                    "red_cards_last_365_days": red2,
                    "valuation_year": 2026,
                    "position": position2,
                    "sub_position": sub_position2,
                    "foot": foot2,
                },
            ])

            try:
                preds = np.maximum(0, np.expm1(model.predict(comparison_data)))

                try:
                    profile1 = find_player_profile(name1) or {}
                except Exception:
                    profile1 = {}

                try:
                    profile2 = find_player_profile(name2) or {}
                except Exception:
                    profile2 = {}

                st.session_state["comparison_result"] = {
                    "name1": name1.strip(),
                    "name2": name2.strip(),
                    "value1": float(preds[0]),
                    "value2": float(preds[1]),
                    "age1": age1,
                    "age2": age2,
                    "height1": height1,
                    "height2": height2,
                    "position1": position1,
                    "position2": position2,
                    "sub_position1": sub_position1,
                    "sub_position2": sub_position2,
                    "foot1": foot1,
                    "foot2": foot2,
                    "goals1": goals1,
                    "goals2": goals2,
                    "assists1": assists1,
                    "assists2": assists2,
                    "minutes1": minutes1,
                    "minutes2": minutes2,
                    "yellow1": yellow1,
                    "yellow2": yellow2,
                    "red1": red1,
                    "red2": red2,
                    "profile1": profile1,
                    "profile2": profile2,
                }
            except Exception as error:
                st.error(f"Comparison failed: {error}")

    if "comparison_result" in st.session_state:
        r = st.session_state["comparison_result"]
        v1, v2 = r["value1"], r["value2"]
        win1, win2 = v1 > v2, v2 > v1
        profiles = {1: r.get("profile1") or {}, 2: r.get("profile2") or {}}

        # Display names: prefer the database spelling, fall back to what was typed
        names = {
            i: clean_profile_value(profiles[i].get("name"), r[f"name{i}"])
            for i in (1, 2)
        }
        clubs = {
            i: clean_profile_value(profiles[i].get("club"), "No club on record")
            for i in (1, 2)
        }
        photos = {
            i: clean_profile_value(profiles[i].get("image_url"), "")
            for i in (1, 2)
        }

        cards = []
        for idx in (1, 2):
            value = r[f"value{idx}"]
            is_winner = win1 if idx == 1 else win2
            side = "a" if idx == 1 else "b"
            side_label = "Player one" if idx == 1 else "Player two"
            badge = '<span class="higher-badge">★ Higher value</span>' if is_winner else ""

            cards.append(h(f"""
            <div class="broadcast-card {side} {'win' if is_winner else ''}">
              <div class="side-tag">{side_label}</div>
              <div class="side-profile">
                {avatar_html(photos[idx], names[idx], "md")}
                <div class="side-player-meta">
                  <div class="pname md">{esc(names[idx])}</div>
                  <div class="club-line">
                    <div class="club-monogram">{esc(initials(clubs[idx]))}</div>
                    <div>
                      <div class="club-name">{esc(clubs[idx])}</div>
                      <div class="report-meta" style="margin-top:2px">Age {r[f'age{idx}']}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="broadcast-value">{fmt_eur(value)}</div>
              <div class="report-meta">Predicted market value</div>
              {badge}
            </div>
            """))

        st.markdown(
            h(
                '<div class="h2h-broadcast">'
                + cards[0]
                + '<div class="vs-wrap"><div class="vs-mark">VS</div></div>'
                + cards[1]
                + "</div>"
            ),
            unsafe_allow_html=True,
        )

        for idx in (1, 2):
            if not profiles[idx]:
                st.caption(
                    f"No player named “{r[f'name{idx}']}” was found in the database. "
                    "The prediction still works. Try the full name for a photo."
                )

        if win1 or win2:
            w = 1 if win1 else 2
            loser = 2 if win1 else 1
            difference = abs(v1 - v2)
            lo = min(v1, v2)
            gap = f"{(difference / lo) * 100:.0f}% more" if lo > 0 else "far more"

            st.markdown(
                h(f"""
                <div class="winner-spotlight">
                  <div class="winner-kicker">★ Model value leader</div>
                  <div class="winner-main">
                    {avatar_html(photos[w], names[w], "sm")}
                    <div>
                      <div class="pname sm">{esc(names[w])}</div>
                      <div class="winner-sub">{esc(clubs[w])}</div>
                    </div>
                    <div class="winner-value">{fmt_eur(r[f'value{w}'])}</div>
                  </div>
                  <div class="winner-note">
                    <b>{esc(names[w])}</b> is valued <b>{fmt_eur(difference)}</b> higher than
                    {esc(names[loser])} ({gap}).
                  </div>
                </div>
                """),
                unsafe_allow_html=True,
            )
        else:
            st.info("Both players have the same predicted value.")

        st.markdown("#### Stat breakdown")

        per90_1 = (r["goals1"] + r["assists1"]) / max(r["minutes1"], 1) * 90
        per90_2 = (r["goals2"] + r["assists2"]) / max(r["minutes2"], 1) * 90

        st.markdown(
            h(
                f'<div class="srow-head"><span class="nm a">{esc(names[1])}</span>'
                f'<span class="nm b">{esc(names[2])}</span></div>'
                + stat_row("Goals", r["goals1"], r["goals2"])
                + stat_row("Assists", r["assists1"], r["assists2"])
                + stat_row("Minutes", r["minutes1"], r["minutes2"])
                + stat_row("Goal contributions / 90", round(per90_1, 2), round(per90_2, 2))
                + stat_row("Yellow cards", r["yellow1"], r["yellow2"])
                + stat_row("Red cards", r["red1"], r["red2"])
                + stat_row("Age", r["age1"], r["age2"])
                + stat_row("Height (cm)", r["height1"], r["height2"])
            ),
            unsafe_allow_html=True,
        )

        detail_col1, detail_col2 = st.columns(2)
        with detail_col1:
            st.markdown(
                f'<span class="detail-pill">{esc(r["position1"])}</span>'
                f'<span class="detail-pill">{esc(r["sub_position1"])}</span>'
                f'<span class="detail-pill">Foot: {esc(r["foot1"])}</span>',
                unsafe_allow_html=True,
            )
        with detail_col2:
            st.markdown(
                f'<span class="detail-pill">{esc(r["position2"])}</span>'
                f'<span class="detail-pill">{esc(r["sub_position2"])}</span>'
                f'<span class="detail-pill">Foot: {esc(r["foot2"])}</span>',
                unsafe_allow_html=True,
            )

        label1, label2 = names[1], names[2]
        if label1 == label2:
            label1, label2 = f"{label1} (1)", f"{label2} (2)"

        chart_df = pd.DataFrame({
            "Player": [label1, label2],
            "Value (€M)": [v1 / 1e6, v2 / 1e6],
        })

        bars = alt.Chart(chart_df).mark_bar(
            cornerRadiusEnd=6,
            size=34,
        ).encode(
            y=alt.Y("Player:N", sort=None, title=None),
            x=alt.X("Value (€M):Q", title="Predicted value (€M)"),
            color=alt.Color(
                "Player:N",
                scale=alt.Scale(domain=[label1, label2], range=[BLUE, CORAL]),
                legend=None,
            ),
            tooltip=[
                "Player",
                alt.Tooltip("Value (€M):Q", format=".2f"),
            ],
        )
        show_chart(bars, height=170)

        comparison_export = pd.DataFrame([
            {
                "player": r["name1"], "predicted_value_eur": r["value1"],
                "age": r["age1"], "height_cm": r["height1"],
                "position": r["position1"], "sub_position": r["sub_position1"],
                "foot": r["foot1"], "goals": r["goals1"], "assists": r["assists1"],
                "minutes": r["minutes1"], "yellow_cards": r["yellow1"], "red_cards": r["red1"],
            },
            {
                "player": r["name2"], "predicted_value_eur": r["value2"],
                "age": r["age2"], "height_cm": r["height2"],
                "position": r["position2"], "sub_position": r["sub_position2"],
                "foot": r["foot2"], "goals": r["goals2"], "assists": r["assists2"],
                "minutes": r["minutes2"], "yellow_cards": r["yellow2"], "red_cards": r["red2"],
            },
        ])
        st.download_button(
            "Download comparison report (CSV)",
            data=comparison_export.to_csv(index=False).encode("utf-8"),
            file_name="football_iq_player_comparison.csv",
            mime="text/csv",
            key="download_comparison_csv",
        )
        st.caption(
            "Each player's prediction uses their separately entered age, height, position, "
            "sub-position, foot, performance statistics and card counts. "
            "Predictions remain model estimates, not official valuations."
        )


# =====================================================
# TAB 3: MARKET ANALYTICS
# =====================================================
with tab_analytics:
    st.header("Football market trends")
    st.markdown(
        '<div class="lede">Explore valuation patterns in the historical Transfermarkt data used by the model.</div>',
        unsafe_allow_html=True,
    )

    try:
        df = load_analytics_data().copy()
        df["valuation_date"] = pd.to_datetime(df["valuation_date"], errors="coerce")
        df = df.dropna(subset=["market_value_eur", "valuation_date", "age"])
        df["market_value_millions"] = df["market_value_eur"] / 1_000_000
        df["valuation_year"] = df["valuation_date"].dt.year

        # Interactive filters
        st.markdown("### Filter the dataset")
        filter1, filter2, filter3 = st.columns([1.2, 1, 1.2])

        positions = ["All positions"] + sorted(
            df["position"].dropna().astype(str).unique().tolist()
        )
        selected_position = filter1.selectbox(
            "Position", positions, key="analytics_position_filter"
        )

        years = sorted(
            df["valuation_year"].dropna().astype(int).unique().tolist()
        )
        year_options = ["All years"] + [str(y) for y in years]
        selected_year = filter2.selectbox(
            "Valuation year", year_options,
            index=0, key="analytics_year_filter"
        )

        age_min, age_max = int(df["age"].min()), int(df["age"].max())
        age_min = max(15, age_min)
        age_max = min(45, age_max)
        selected_ages = filter3.slider(
            "Player age range",
            min_value=age_min,
            max_value=age_max,
            value=(age_min, age_max),
            key="analytics_age_filter",
        )

        filtered = df.copy()
        if selected_position != "All positions":
            filtered = filtered[filtered["position"] == selected_position]
        if selected_year != "All years":
            filtered = filtered[filtered["valuation_year"] == int(selected_year)]
        filtered = filtered[filtered["age"].between(*selected_ages)]

        if filtered.empty:
            st.warning("No valuation records match these filters. Try a wider age range or another year.")
        else:
            # Summary metrics
            st.markdown("### Dataset overview")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Filtered records", f"{len(filtered):,}")
            c2.metric("Average value", f"€{filtered['market_value_millions'].mean():.2f}M")
            c3.metric("Median value", f"€{filtered['market_value_millions'].median():.2f}M")
            c4.metric("Unique players", f"{filtered['player_id'].nunique():,}" if "player_id" in filtered.columns else f"{filtered['player_name'].nunique():,}")

            st.divider()

            # Market value distribution
            st.markdown("### Where most values sit")
            st.caption("Number of historical valuation records in each range, up to €100M.")
            capped = filtered[filtered["market_value_millions"].between(0, 100)]
            labels = ["€0–1M", "€1–5M", "€5–10M", "€10–20M", "€20–30M", "€30–50M", "€50–75M", "€75–100M"]
            ranges = pd.cut(
                capped["market_value_millions"],
                bins=[0, 1, 5, 10, 20, 30, 50, 75, 100],
                labels=labels,
                include_lowest=True,
            ).value_counts(sort=False)
            dist_df = pd.DataFrame({
                "Range": [str(item) for item in ranges.index],
                "Records": ranges.values,
            })
            dist = alt.Chart(dist_df).mark_bar(
                cornerRadiusTopLeft=6,
                cornerRadiusTopRight=6,
                color=BLUE,
            ).encode(
                x=alt.X("Range:N", sort=labels, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Records:Q", title=None),
                tooltip=["Range", alt.Tooltip("Records:Q", format=",")],
            )
            show_chart(dist, height=300)

            # Position and age charts
            left, right = st.columns(2)
            with left:
                st.markdown("### Average value by position")
                pos_df = (
                    filtered.groupby("position")["market_value_millions"]
                    .mean().sort_values(ascending=False).reset_index()
                )
                pos_df.columns = ["Position", "Avg value (€M)"]
                if not pos_df.empty:
                    top_pos = pos_df.iloc[0]["Position"]
                    pos_chart = alt.Chart(pos_df).mark_bar(
                        cornerRadiusEnd=6, size=28
                    ).encode(
                        y=alt.Y("Position:N", sort="-x", title=None),
                        x=alt.X("Avg value (€M):Q", title=None),
                        color=alt.condition(
                            alt.datum.Position == top_pos,
                            alt.value(GOLD), alt.value(BLUE)
                        ),
                        tooltip=["Position", alt.Tooltip("Avg value (€M):Q", format=".2f")],
                    )
                    show_chart(pos_chart, height=260)

            with right:
                st.markdown("### Average value by age group")
                age_labels = ["15–18", "19–21", "22–25", "26–30", "31–35", "36–45"]
                age_df_source = filtered.copy()
                age_df_source["age_group"] = pd.cut(
                    age_df_source["age"],
                    bins=[14, 18, 21, 25, 30, 35, 45],
                    labels=age_labels,
                )
                age_df = (
                    age_df_source.groupby("age_group", observed=False)["market_value_millions"]
                    .mean().reset_index()
                )
                age_df.columns = ["Age group", "Avg value (€M)"]
                age_df["Age group"] = age_df["Age group"].astype(str)
                age_peak = age_df["Avg value (€M)"].idxmax() if age_df["Avg value (€M)"].notna().any() else None
                peak = age_df.loc[age_peak, "Age group"] if age_peak is not None else None
                age_chart = alt.Chart(age_df).mark_bar(
                    cornerRadiusTopLeft=6, cornerRadiusTopRight=6
                ).encode(
                    x=alt.X("Age group:N", sort=age_labels, title=None, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Avg value (€M):Q", title=None),
                    color=alt.condition(
                        alt.datum["Age group"] == peak,
                        alt.value(GOLD), alt.value(BLUE)
                    ),
                    tooltip=["Age group", alt.Tooltip("Avg value (€M):Q", format=".2f")],
                )
                show_chart(age_chart, height=260)

            # Yearly market trend
            st.divider()
            st.markdown("### Market value trend over time")
            yearly = (
                filtered.groupby("valuation_year")["market_value_millions"]
                .mean().reset_index()
            )
            yearly["valuation_year"] = yearly["valuation_year"].astype(int)
            trend = alt.Chart(yearly).mark_line(
                color=GOLD,
                strokeWidth=3,
                point=alt.OverlayMarkDef(color=BLUE, size=45),
            ).encode(
                x=alt.X("valuation_year:O", title="Valuation year"),
                y=alt.Y("market_value_millions:Q", title="Average market value (€M)"),
                tooltip=[
                    alt.Tooltip("valuation_year:O", title="Year"),
                    alt.Tooltip("market_value_millions:Q", title="Average value (€M)", format=".2f"),
                ],
            )
            show_chart(trend, height=260)

            # Latest valuation leaderboard. One latest row per player.
            st.divider()
            st.markdown("### Highest-valued players in the filtered records")
            group_key = "player_id" if "player_id" in filtered.columns else "player_name"
            latest_rows = (
                filtered.sort_values("valuation_date")
                .groupby(group_key, as_index=False)
                .tail(1)
                .sort_values("market_value_eur", ascending=False)
                .head(10)
            )
            display_cols = [c for c in ["player_name", "current_club_name", "position", "age", "market_value_eur", "valuation_date"] if c in latest_rows.columns]
            leaderboard = latest_rows[display_cols].copy()
            if "market_value_eur" in leaderboard.columns:
                leaderboard["market_value_eur"] = leaderboard["market_value_eur"].map(lambda x: f"€{x:,.0f}")
            if "valuation_date" in leaderboard.columns:
                leaderboard["valuation_date"] = pd.to_datetime(leaderboard["valuation_date"]).dt.strftime("%d %b %Y")
            st.dataframe(leaderboard, use_container_width=True, hide_index=True)

            # Export the current filtered data
            st.download_button(
                "Download filtered analytics (CSV)",
                data=filtered.to_csv(index=False).encode("utf-8"),
                file_name="football_iq_filtered_market_data.csv",
                mime="text/csv",
                key="download_analytics_csv",
            )

            st.caption(
                "The charts use historical valuation records. One player can appear in several records; "
                "the leaderboard keeps only each player's latest record within the selected filters."
            )

    except Exception as error:
        st.error(f"Unable to display analytics: {error}")


# =====================================================
# FOOTER
# =====================================================
st.divider()
st.markdown(
    '<div class="foot">Football IQ · Built with Python, Pandas, '
    "scikit-learn, DuckDB and Streamlit</div>",
    unsafe_allow_html=True,
)