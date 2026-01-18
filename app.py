import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots
from agents.technical_agent import TechnicalAnalyst
from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAgent
from agents.supply_chain_agent import SupplyChainAgent
from agents.monte_carlo_agent import MonteCarloAgent
from agents.insider_agent import InsiderAgent
from agents.volatility_agent import VolatilityAgent
from agents.correlation_agent import CorrelationAgent
from agents.macro_agent import MacroAgent
from agents.valuation_agent import ValuationAgent
from agents.portfolio_agent import PortfolioAgent
from agents.news_agent import NewsAgent
from agents.peer_agent import PeerAgent
from agents.financial_agent import FinancialAgent
from agents.ownership_agent import OwnershipAgent
from agents.chatbot_agent import ChatbotAgent
from utils.pdf_generator import create_pdf
from utils.ticker_data import ASSET_DATABASE


# 1. Page Config (기본 설정)
st.set_page_config(
    page_title="Quant AI Terminal",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 2. Streamlit 기본 스타일 숨기기 (헤더는 살려서 모바일 버튼 복구)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# 2. Styling (Perfect Dark Mode: White Fonts for Charts, Clean Inputs)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0E1117; }
    [data-testid="stSidebar"] { background-color: #161920; border-right: 1px solid #262730; }
    
    .stTextInput > div > div > input { border-radius: 10px; background-color: #262730; color: #FFFFFF; border: 1px solid #363945; }
    .stTextArea textarea { background-color: #1C1F26 !important; color: #FFFFFF !important; border: 1px solid #2E3440 !important; border-radius: 10px; }


    /* --- [FIXED] Chat Input & Styling --- */
    ::selection { background-color: #4B6CB7 !important; color: #FFFFFF !important; }
    [data-testid="stBottom"], [data-testid="stBottom"] * { background-color: #0E1117 !important; }
    
    .stChatInput textarea {
        background-color: #262730 !important; 
        color: #FFFFFF !important;
        caret-color: #FFFFFF !important;
        border: 1px solid #363945 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        outline: none !important;
    }
    .stChatInput textarea::placeholder { color: #E0E0E0 !important; opacity: 1 !important; -webkit-text-fill-color: #E0E0E0 !important; }
    .stChatInput textarea:focus,
    .stChatInput textarea:focus-visible {
        border: 1px solid #363945 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    .stChatInput:focus-within { outline: none !important; box-shadow: none !important; }
    
    /* Remove White Box from Chat Numbers */
    code { background-color: transparent !important; color: #00CC96 !important; border: none !important; font-weight: bold !important; }


    /* Chat Messages */
    [data-testid="stChatMessage"] { background-color: #161920 !important; border: 1px solid #2E3440 !important; border-radius: 10px !important; }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { color: #FFFFFF !important; }
    [data-testid="stChatMessageAvatarUser"] { background-color: #4B6CB7 !important; }
    [data-testid="stChatMessageAvatarAssistant"] { background-color: #00CC96 !important; }
    
    /* --- [FIX] News Card Styling --- */
    .news-card { background-color: #1C1F26; padding: 15px; border-radius: 10px; border: 1px solid #2E3440; margin-bottom: 10px; transition: transform 0.2s; }
    .news-card:hover { transform: translateX(5px); border-color: #4B6CB7; }
    .news-title { font-weight: 600; color: #FFFFFF !important; font-size: 1.05rem; text-decoration: none; display: block; margin-bottom: 5px; }
    .news-title:hover { color: #4B6CB7 !important; text-decoration: underline; }
    .news-meta { font-size: 0.8rem; color: #888; }


    /* Common Components */
    .stMultiSelect span[data-baseweb="tag"] { background-color: #262730 !important; border: 1px solid #4B6CB7 !important; color: white !important; }
    .stMultiSelect div[data-baseweb="select"] > div { background-color: #262730 !important; color: white !important; }
    .stSelectbox > div > div { background-color: #262730; color: white; border-radius: 10px; }
    .stButton > button { border-radius: 10px; background: linear-gradient(90deg, #4B6CB7 0%, #182848 100%); color: white; border: none; font-weight: 500; }
    .metric-card { background-color: #1D2028; border-radius: 12px; padding: 24px; border: 1px solid #31333F; text-align: center; }
    h1, h2, h3 { color: #F0F2F6 !important; }
    p, span, label { color: #BDC1C6 !important; }
    table { width: 100%; border-collapse: collapse; background-color: #1C1F26 !important; color: #FFFFFF !important; border-radius: 10px; border: 1px solid #2E3440; }
    th { background-color: #262730 !important; color: #4B6CB7 !important; padding: 12px; text-align: left; font-weight: 600; }
    td { padding: 10px; border-bottom: 1px solid #2E3440; font-size: 0.9rem; }
    .sentiment-badge { font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-left: 10px; }
    .verdict-box { background-color: #161920; border-left: 4px solid #4B6CB7; padding: 15px; border-radius: 0 10px 10px 0; margin: 10px 0; }

    /* Top Header & Ticker Bar */
    .qa-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 18px;
        margin-bottom: 8px;
        border: 1px solid #262730;
        border-radius: 12px;
        background: linear-gradient(135deg, #0B0F14 0%, #121723 100%);
    }
    .qa-topbar-title {
        font-size: 18px;
        font-weight: 600;
        color: #E6EDF3;
        letter-spacing: 1px;
    }
    .qa-topbar-sub {
        font-size: 11px;
        color: #9AA4B2;
    }
    .qa-badge {
        padding: 4px 8px;
        font-size: 10px;
        border-radius: 999px;
        border: 1px solid #2E3440;
        color: #CFE7DF;
        background: #0B0F14;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .qa-tickerbar {
        overflow: hidden;
        border: 1px solid #262730;
        border-radius: 10px;
        background: #0B0F14;
        padding: 6px 0;
        margin-bottom: 14px;
    }
    .qa-ticker-track {
        display: inline-block;
        white-space: nowrap;
        animation: qa-scroll 22s linear infinite;
        color: #D7DEE6;
        font-size: 12px;
    }
    .qa-ticker-item {
        display: inline-flex;
        align-items: center;
        margin: 0 18px;
        gap: 8px;
    }
    .qa-ticker-up { color: #00CC96; }
    .qa-ticker-down { color: #EF553B; }
    @keyframes qa-scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* Widget Cards */
    .qa-widget-card {
        border: 1px solid #262730;
        border-radius: 12px;
        padding: 14px;
        background: #11151C;
    }
    .qa-widget-title {
        font-size: 12px;
        color: #9AA4B2;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .qa-pill {
        display: inline-block;
        padding: 3px 8px;
        font-size: 10px;
        border-radius: 999px;
        background: #1C1F26;
        border: 1px solid #2E3440;
        color: #BFC6D1;
    }
    .qa-flash-up {
        animation: qaFlashUp 0.9s ease;
        color: #00CC96 !important;
        text-shadow: 0 0 12px rgba(0, 204, 150, 0.5);
    }
    .qa-flash-down {
        animation: qaFlashDown 0.9s ease;
        color: #EF553B !important;
        text-shadow: 0 0 12px rgba(239, 85, 59, 0.5);
    }
    @keyframes qaFlashUp {
        0% { opacity: 0.2; transform: scale(0.98); }
        40% { opacity: 1; transform: scale(1.03); }
        100% { opacity: 1; transform: scale(1); }
    }
    @keyframes qaFlashDown {
        0% { opacity: 0.2; transform: scale(0.98); }
        40% { opacity: 1; transform: scale(1.03); }
        100% { opacity: 1; transform: scale(1); }
    }
    .qa-spark-card {
        border: 1px solid #262730;
        border-radius: 12px;
        padding: 8px 10px;
        background: #0F141C;
    }
    .qa-spark-title {
        font-size: 10px;
        color: #9AA4B2;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .qa-spark-price {
        font-size: 14px;
        font-weight: 600;
        color: #E6EDF3;
    }
    .qa-spark-change {
        font-size: 10px;
        margin-left: 6px;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .qa-topbar { padding: 10px 12px; flex-direction: column; align-items: flex-start; gap: 6px; }
        .qa-topbar-title { font-size: 16px; }
        .qa-topbar-sub { font-size: 10px; }
        .qa-badge { font-size: 9px; }
        .qa-tickerbar { padding: 4px 0; }
        .qa-ticker-track { font-size: 10px; }
        .qa-widget-card { padding: 10px; }
        .qa-widget-title { font-size: 10px; }
        .qa-spark-card { padding: 10px 12px; }
        .qa-spark-title { font-size: 11px; }
        .qa-spark-price { font-size: 15px; }
        .qa-spark-change { font-size: 11px; }
        /* Enlarge only snapshot sparklines on mobile */
        div:has(.qa-spark-card) + div [data-testid="stPlotlyChart"] {
            transform: scaleY(1.25);
            transform-origin: top;
        }
        h1 { font-size: 1.45rem !important; }
        h2 { font-size: 1.05rem !important; }
        h3 { font-size: 0.95rem !important; }
        .metric-card { padding: 12px; }
        .metric-card h2 { font-size: 1.3rem !important; }
        .metric-card p { font-size: 0.75rem !important; }
        .stButton > button { padding: 8px 12px; }
        [data-testid="stSidebar"] { width: 100% !important; }
    }

    /* Intro animation overlay */
    .qa-intro {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: grid;
        place-items: center;
        background-color: #0B0F14;
        background-image:
            radial-gradient(120% 120% at 50% 18%, rgba(0,230,168,0.18), rgba(7,10,16,0.98)),
            radial-gradient(90% 90% at 80% 10%, rgba(0,230,168,0.12), transparent 60%);
        animation: qa-intro-fade 3.0s ease forwards;
        overflow: hidden;
    }
    .qa-intro::before {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(70% 70% at 50% 50%, transparent 40%, rgba(0,0,0,0.55) 100%);
        opacity: 0.8;
        pointer-events: none;
    }
    .qa-intro::after {
        content: "";
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(
            180deg,
            rgba(255,255,255,0.03) 0px,
            rgba(255,255,255,0.03) 1px,
            transparent 2px,
            transparent 4px
        );
        opacity: 0.12;
        mix-blend-mode: screen;
        pointer-events: none;
    }
    .qa-intro-stars {
        position: absolute;
        inset: -30%;
        background-image:
            radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.25), transparent 60%),
            radial-gradient(1px 1px at 30% 80%, rgba(255,255,255,0.2), transparent 60%),
            radial-gradient(1px 1px at 70% 40%, rgba(255,255,255,0.2), transparent 60%),
            radial-gradient(1px 1px at 85% 70%, rgba(255,255,255,0.15), transparent 60%);
        animation: qa-stars-drift 6s linear infinite;
        opacity: 0.6;
    }
    .qa-intro-network {
        position: absolute;
        inset: 0;
        opacity: 0.45;
        pointer-events: none;
    }
    .qa-intro-network path {
        stroke: rgba(0,230,168,0.55);
        stroke-width: 1;
        fill: none;
        stroke-dasharray: 6 8;
        animation: qa-network-dash 2.8s linear infinite;
    }
    .qa-intro-network circle {
        fill: rgba(0,230,168,0.9);
        filter: drop-shadow(0 0 8px rgba(0,230,168,0.8));
        animation: qa-node-pulse 1.6s ease-in-out infinite;
    }
    .qa-intro-center {
        position: relative;
        display: grid;
        place-items: center;
        z-index: 2;
    }
    .qa-intro-core {
        width: 86px;
        height: 86px;
        border-radius: 50%;
        background: radial-gradient(circle, #00E6A8 0%, rgba(0,230,168,0.18) 70%);
        box-shadow: 0 0 40px rgba(0,230,168,0.9), 0 0 120px rgba(0,230,168,0.6);
        animation: qa-core-pulse 1.05s ease-in-out infinite;
        position: relative;
    }
    .qa-intro-ring {
        position: absolute;
        inset: -48px;
        border-radius: 50%;
        border: 1px solid rgba(0,230,168,0.55);
        animation: qa-orbit 1.9s linear infinite;
        box-shadow: 0 0 35px rgba(0,230,168,0.4);
    }
    .qa-intro-ring.r2 { inset: -92px; border-color: rgba(0,230,168,0.35); animation-duration: 2.5s; }
    .qa-intro-ring.r3 { inset: -140px; border-color: rgba(255,255,255,0.18); animation-duration: 3.1s; }
    .qa-intro-grid {
        position: absolute;
        width: 220%;
        height: 220%;
        background-image:
            linear-gradient(transparent 94%, rgba(0,230,168,0.35) 95%),
            linear-gradient(90deg, transparent 94%, rgba(0,230,168,0.35) 95%);
        background-size: 36px 36px;
        transform: rotateX(68deg) translateY(36%);
        animation: qa-grid-move 1.2s linear infinite;
        opacity: 0.8;
    }
    .qa-intro-beam {
        position: absolute;
        width: 420px;
        height: 6px;
        background: linear-gradient(90deg, transparent 0%, rgba(0,230,168,0.6) 50%, transparent 100%);
        filter: blur(0.5px);
        animation: qa-beam-scan 1.6s ease-in-out infinite;
        opacity: 0.8;
    }
    .qa-intro-particles {
        position: absolute;
        inset: 0;
        pointer-events: none;
    }
    .qa-intro-particle {
        position: absolute;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: #FFFFFF;
        box-shadow: 0 0 12px rgba(255,255,255,0.9);
        animation: qa-particle-float 1.6s ease-in-out infinite;
        opacity: 0.8;
    }
    .qa-intro-particle.p1 { top: 30%; left: 42%; animation-delay: 0.1s; }
    .qa-intro-particle.p2 { top: 55%; left: 30%; animation-delay: 0.3s; }
    .qa-intro-particle.p3 { top: 38%; left: 68%; animation-delay: 0.5s; }
    .qa-intro-particle.p4 { top: 70%; left: 58%; animation-delay: 0.7s; }
    .qa-intro-particle.p5 { top: 25%; left: 58%; animation-delay: 0.2s; }
    .qa-intro-particle.p6 { top: 62%; left: 72%; animation-delay: 0.4s; }
    .qa-intro-logo {
        margin-top: 26px;
        font-size: 40px;
        font-weight: 600;
        letter-spacing: 8px;
        color: #E9FFF6;
        text-shadow: 0 0 18px rgba(0,230,168,0.8);
        opacity: 0;
        animation: qa-logo-in 3.0s ease forwards;
        animation-delay: 0.3s;
    }
    .qa-intro-wordmark {
        margin-top: 8px;
        font-size: 12px;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #C9FBE7;
        opacity: 0;
        animation: qa-wordmark-in 3.0s ease forwards;
        animation-delay: 0.7s;
    }
    .qa-intro-sub {
        margin-top: 6px;
        font-size: 10px;
        letter-spacing: 1px;
        color: #9AA4B2;
        text-align: center;
        opacity: 0;
        animation: qa-sub-in 3.0s ease forwards;
        animation-delay: 1.0s;
    }
    @keyframes qa-intro-fade {
        0% { opacity: 0; }
        10% { opacity: 1; }
        85% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }
    @keyframes qa-app-fade {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes qa-logo-in {
        0% { transform: translateY(12px) scale(0.95); opacity: 0; }
        40% { transform: translateY(0) scale(1); opacity: 1; }
        100% { opacity: 1; }
    }
    @keyframes qa-wordmark-in {
        0% { transform: translateY(10px); opacity: 0; }
        45% { transform: translateY(0); opacity: 1; }
        100% { opacity: 1; }
    }
    @keyframes qa-sub-in {
        0% { transform: translateY(8px); opacity: 0; }
        50% { transform: translateY(0); opacity: 1; }
        100% { opacity: 1; }
    }
    @keyframes qa-stars-drift {
        from { transform: translateY(0); }
        to { transform: translateY(40px); }
    }
    @keyframes qa-network-dash {
        from { stroke-dashoffset: 0; }
        to { stroke-dashoffset: -80; }
    }
    @keyframes qa-node-pulse {
        0% { opacity: 0.5; transform: scale(0.9); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0.5; transform: scale(0.9); }
    }
    @keyframes qa-grid-move {
        from { transform: rotateX(68deg) translateY(36%); }
        to { transform: rotateX(68deg) translateY(42%); }
    }
    @keyframes qa-core-pulse {
        0% { transform: scale(0.9); opacity: 0.6; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.6; }
    }
    @keyframes qa-orbit {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes qa-beam-scan {
        0% { transform: translateX(-140px); opacity: 0.2; }
        50% { transform: translateX(140px); opacity: 0.8; }
        100% { transform: translateX(-140px); opacity: 0.2; }
    }
    @keyframes qa-particle-float {
        0% { transform: translateY(0); opacity: 0.6; }
        50% { transform: translateY(-8px); opacity: 1; }
        100% { transform: translateY(0); opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# Auto refresh (15–30s)
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 20

if st.session_state.auto_refresh:
    st.markdown(
        f"""
        <script>
        (function() {{
          if (!window.__qa_autorefresh) {{
            window.__qa_autorefresh = true;
            setInterval(function() {{
              window.location.reload();
            }}, {int(st.session_state.refresh_interval) * 1000});
          }}
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )

# Mobile swipe-to-close for sidebar (best-effort)
st.markdown(
    """
    <script>
    (function() {
      let startX = null;
      let startY = null;
      const threshold = 80;
      function findCollapseButton() {
        return document.querySelector(
          '[data-testid="stSidebarCollapseButton"],' +
          '[data-testid="collapsedControl"],' +
          'button[aria-label*="sidebar"],' +
          'button[title*="Collapse"],' +
          'button[title*="collapse"]'
        );
      }
      function onTouchStart(e) {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        if (!sidebar.contains(e.target)) return;
        const touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
      }
      function onTouchMove(e) {
        if (startX === null || startY === null) return;
        const touch = e.touches[0];
        const dx = touch.clientX - startX;
        const dy = touch.clientY - startY;
        if (Math.abs(dx) > Math.abs(dy) && dx < -threshold) {
          const btn = findCollapseButton();
          if (btn) btn.click();
          startX = null;
          startY = null;
        }
      }
      document.addEventListener('touchstart', onTouchStart, { passive: true });
      document.addEventListener('touchmove', onTouchMove, { passive: true });
    })();
    </script>
    """,
    unsafe_allow_html=True,
)


# 3. Sidebar
with st.sidebar:
    st.title("🦅 QUANT AI")
    st.caption("Institutional Terminal v11.0 MEMORY")
    st.markdown("---")
    st.markdown("""<div style="text-align: left; padding: 10px; background-color: #1C1F26; border-radius: 10px; border: 1px solid #2E3440;"><p class="profile-name">👨‍💻 Jihu Park</p><p class="profile-role">Lead Quant Architect</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 📌 Dock Panel")
    st.markdown(
        """
        <div class="qa-widget-card">
            <div class="qa-widget-title">Quick Views</div>
            <div class="qa-pill">Snapshot</div>
            <div class="qa-pill">Heatmap</div>
            <div class="qa-pill">News</div>
            <div class="qa-pill">Reports</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("#### ⏱️ Live Refresh")
    st.session_state.auto_refresh = st.toggle("Auto Refresh", value=st.session_state.auto_refresh)
    st.session_state.refresh_interval = st.selectbox(
        "Refresh Interval (sec)",
        [15, 20, 30],
        index=[15, 20, 30].index(st.session_state.refresh_interval),
    )
    st.markdown("---")
    selected_asset_name = st.selectbox("Search Symbol", options=list(ASSET_DATABASE.keys()), index=0)
    ticker = ASSET_DATABASE[selected_asset_name]
    module = st.radio("Select Analysis Mode:", [
        "💬 AI Assistant", "📊 Pro Charting", "📑 Deep Research", "🎯 Wall St. Insights", 
        "📊 Financial Health", "👥 Peer Comparison", "📰 Smart News", "🤖 AI Strategy", 
        "🕸️ Supply Chain", "⚖️ Fundamental Valuation", "🔮 Monte Carlo", "💼 Portfolio Optimizer", 
        "🕵️ Insider Tracker", "🧊 3D Volatility", "🔗 Correlation", "🏛️ Macro Analysis"
    ], index=0)
    if module == "💼 Portfolio Optimizer": st.info("Configuring Portfolio...")
    else: st.success(f"Target: {ticker}")


# 3.5 Intro Animation (first load per session)
if "intro_shown" not in st.session_state:
    st.session_state.intro_shown = False
if not st.session_state.intro_shown:
    st.markdown(
        """
        <style>
            .stApp {
                opacity: 0;
                animation: qa-app-fade 0.9s ease forwards;
                animation-delay: 2.1s;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="qa-intro">
            <div class="qa-intro-stars"></div>
            <svg class="qa-intro-network" viewBox="0 0 1000 600" preserveAspectRatio="none">
                <path d="M40,120 L260,80 L420,140 L620,110 L820,160 L960,120" />
                <path d="M80,420 L240,340 L420,360 L620,300 L820,380 L940,340" />
                <path d="M120,220 L300,260 L520,240 L700,280 L900,240" />
                <circle cx="260" cy="80" r="3" />
                <circle cx="420" cy="140" r="3" />
                <circle cx="620" cy="110" r="3" />
                <circle cx="820" cy="160" r="3" />
                <circle cx="240" cy="340" r="3" />
                <circle cx="420" cy="360" r="3" />
                <circle cx="620" cy="300" r="3" />
                <circle cx="820" cy="380" r="3" />
                <circle cx="300" cy="260" r="3" />
                <circle cx="520" cy="240" r="3" />
                <circle cx="700" cy="280" r="3" />
                <circle cx="900" cy="240" r="3" />
            </svg>
            <div class="qa-intro-center">
                <div class="qa-intro-grid"></div>
                <div class="qa-intro-beam"></div>
                <div class="qa-intro-core">
                    <div class="qa-intro-ring r1"></div>
                    <div class="qa-intro-ring r2"></div>
                    <div class="qa-intro-ring r3"></div>
                </div>
                <div class="qa-intro-particles">
                    <div class="qa-intro-particle p1"></div>
                    <div class="qa-intro-particle p2"></div>
                    <div class="qa-intro-particle p3"></div>
                    <div class="qa-intro-particle p4"></div>
                    <div class="qa-intro-particle p5"></div>
                    <div class="qa-intro-particle p6"></div>
                </div>
                <div class="qa-intro-logo">QA</div>
                <div class="qa-intro-wordmark">QUANT AI TERMINAL</div>
                <div class="qa-intro-sub">Emerald lattice online...</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.intro_shown = True


# 4. Data Logic
analyst = TechnicalAnalyst(ticker)
df = analyst.fetch_data()
summary = "No Data"
if not df.empty and 'Close' in df.columns:
    df = analyst.calculate_indicators()
    summary = analyst.get_summary()

# --- Multi-ticker sparkline snapshot ---
@st.cache_data(ttl=900)
def _fetch_sparkline(ticker_symbol):
    ta = TechnicalAnalyst(ticker_symbol)
    data = ta.fetch_data(period="1mo")
    if data is None or data.empty or "Close" not in data.columns:
        return None
    series = pd.to_numeric(data["Close"], errors="coerce").dropna()
    if series.empty:
        return None
    return series

def _spark_fig(series, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor="rgba(0,230,168,0.08)"
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=65,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig

# --- Top Header + Ticker Bar ---
last_price = summary.get("current_price", 0) if isinstance(summary, dict) else 0
prev_price = df["Close"].iloc[-2] if not df.empty and len(df) > 1 else last_price
chg = last_price - prev_price
chg_pct = (chg / prev_price * 100) if prev_price else 0
chg_class = "qa-ticker-up" if chg >= 0 else "qa-ticker-down"
prev_session_price = st.session_state.get("last_price")
if prev_session_price is None:
    price_flash_class = ""
elif last_price > prev_session_price:
    price_flash_class = "qa-flash-up"
elif last_price < prev_session_price:
    price_flash_class = "qa-flash-down"
else:
    price_flash_class = ""
st.session_state.last_price = last_price
market_status = "OPEN" if 9 <= datetime.datetime.now().hour <= 16 else "CLOSED"
st.markdown(
    f"""
    <div class="qa-topbar">
        <div>
            <div class="qa-topbar-title">Quant AI Terminal</div>
            <div class="qa-topbar-sub">Retail Pro Edition • {datetime.date.today().strftime('%Y-%m-%d')}</div>
        </div>
        <div class="qa-badge">Market {market_status}</div>
    </div>
    <div class="qa-tickerbar">
        <div class="qa-ticker-track">
            <span class="qa-ticker-item"><b>{ticker}</b> <span class="{chg_class} {price_flash_class}">{last_price:.2f} ({chg:+.2f}, {chg_pct:+.2f}%)</span></span>
            <span class="qa-ticker-item"><b>S&P 500</b> <span class="qa-ticker-up">+0.42%</span></span>
            <span class="qa-ticker-item"><b>NASDAQ</b> <span class="qa-ticker-down">-0.18%</span></span>
            <span class="qa-ticker-item"><b>VIX</b> <span class="qa-ticker-up">+1.02%</span></span>
            <span class="qa-ticker-item"><b>USD/KRW</b> <span class="qa-ticker-down">-0.12%</span></span>
            <span class="qa-ticker-item"><b>BTC</b> <span class="qa-ticker-up">+0.87%</span></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sparkline Cards Row ---
st.markdown("### 📌 Multi-Ticker Snapshot")
spark_tickers = [
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("NVDA", "NVIDIA"),
    ("TSLA", "Tesla"),
    ("SPY", "S&P 500"),
    ("BTC-USD", "Bitcoin"),
]
cols = st.columns(3)
for i, (sym, name) in enumerate(spark_tickers):
    series = _fetch_sparkline(sym)
    if series is None or series.empty:
        continue
    price = float(series.iloc[-1])
    base = float(series.iloc[0]) if len(series) > 0 else 0.0
    chg = price - base
    chg_pct = (chg / base * 100) if base != 0 else 0
    color = "#00E6A8" if chg >= 0 else "#EF553B"
    with cols[i % 3]:
        st.markdown(
            f"""
            <div class="qa-spark-card">
                <div class="qa-spark-title">{name}</div>
                <div>
                    <span class="qa-spark-price">{price:.2f}</span>
                    <span class="qa-spark-change" style="color:{color};">{chg_pct:+.2f}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(_spark_fig(series, color), use_container_width=True)

# --- Tabs ---
tab_main, tab_widgets, tab_reports = st.tabs(["Terminal", "Widgets", "Reports"])

# --- Widgets Tab ---
with tab_widgets:
    st.subheader("📌 Snapshot Cards")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='qa-widget-card'><div class='qa-widget-title'>Price</div><h2 style='margin:0;color:#E6EDF3;'>${last_price:.2f}</h2><div class='{chg_class}'>{chg_pct:+.2f}%</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='qa-widget-card'><div class='qa-widget-title'>RSI</div><h2 style='margin:0;color:#E6EDF3;'>{summary.get('rsi',0):.1f}</h2><div class='qa-pill'>{summary.get('sentiment','N/A')}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='qa-widget-card'><div class='qa-widget-title'>SMA 200</div><h2 style='margin:0;color:#E6EDF3;'>${summary.get('sma_200',0):.2f}</h2><div class='qa-pill'>Trend</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='qa-widget-card'><div class='qa-widget-title'>Signal</div><h2 style='margin:0;color:#E6EDF3;'>{summary.get('sentiment','N/A')}</h2><div class='qa-pill'>AI</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧭 Sector / Peer Heatmap")
    try:
        peer_agent = PeerAgent()
        peer_df = peer_agent.fetch_peer_data(ticker)
        if not peer_df.empty and "P/E Ratio" in peer_df.columns and "Rev Growth (%)" in peer_df.columns:
            heat = peer_df.set_index("Ticker")[["P/E Ratio", "Rev Growth (%)"]].head(10)
            fig_heat = go.Figure(data=go.Heatmap(
                z=heat.values,
                x=heat.columns,
                y=heat.index,
                colorscale="Viridis",
                showscale=True
            ))
            fig_heat.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF"),
                height=420
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Peer heatmap data not available for this ticker.")
    except Exception:
        st.info("Peer heatmap data not available.")

    st.markdown("---")
    st.subheader("🧾 Tape (최근 가격 흐름)")
    if not df.empty:
        tape_items = df.tail(12)
        tape_html = ""
        for idx, row in tape_items.iterrows():
            diff = row["Close"] - row["Open"]
            klass = "qa-ticker-up" if diff >= 0 else "qa-ticker-down"
            tape_html += f"<span class='qa-ticker-item'>{idx.strftime('%m-%d')} <b>{row['Close']:.2f}</b> <span class='{klass}'>{diff:+.2f}</span></span>"
        st.markdown(
            f"""
            <div class="qa-tickerbar">
                <div class="qa-ticker-track">{tape_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Tape data not available.")

# --- Reports Tab ---
with tab_reports:
    st.subheader("📑 Report Center")
    st.markdown("전문 리서치 리포트는 **Deep Research 모듈**에서 생성할 수 있습니다.")
    st.markdown("• 커버 + 목차 + 차트 + 동종 비교 + 밸류에이션 섹션 포함")
    st.markdown("• PDF 출력은 상단 ‘Export PDF Report’ 버튼을 사용하세요.")


# 5. Main Dashboard
col1, col2 = st.columns([3, 1])
with col1:
    if module == "💼 Portfolio Optimizer": st.title("💼 Portfolio Manager")
    else:
        st.title(f"{ticker} Dashboard")
        st.markdown(f"**{datetime.date.today().strftime('%Y-%m-%d')}** | Institutional Insights")


with col2:
    if module != "💼 Portfolio Optimizer" and module != "💬 AI Assistant" and not df.empty and isinstance(summary, dict):
        if st.button("📥 Export PDF Report"):
            with st.spinner("Generating..."):
                try:
                    researcher = ResearchAgent()
                    report_data = researcher.run_research(ticker, summary)
                    pdf_file = create_pdf(
                        ticker,
                        summary,
                        report_data['full_text'],
                        filename=f"{ticker}_Report.pdf",
                        price_df=df,
                    )
                    if pdf_file:
                        with open(pdf_file, "rb") as f: st.download_button("⬇️ Download PDF", f, file_name=f"{ticker}_Report.pdf")
                except: st.error("Error creating PDF.")


# --- Content ---
if module != "💼 Portfolio Optimizer" and isinstance(summary, dict) and summary != "No Data":
    st.markdown("### ⚡ Market Pulse")
    m1, m2, m3, m4 = st.columns(4)
    def metric_card(label, value, delta, value_class=""):
        delta_color = '#00CC96' if '+' in str(delta) or 'BULLISH' in str(delta) else '#EF553B'
        if 'NEUTRAL' in str(delta): delta_color = '#FECB52'
        return f"""<div class="metric-card"><p style="font-size: 0.85rem; margin-bottom: 8px;">{label}</p><h2 class="{value_class}" style="margin: 0; font-size: 2rem; color: #FFFFFF;">{value}</h2><p style="color: {delta_color}; font-weight: 600;">{delta}</p></div>"""
    with m1: st.markdown(metric_card("Price", f"${summary.get('current_price',0):.2f}", "Live", price_flash_class), unsafe_allow_html=True)
    with m2: st.markdown(metric_card("RSI (14)", f"{summary.get('rsi',0):.2f}", summary.get('sentiment','N/A')), unsafe_allow_html=True)
    with m3: st.markdown(metric_card("200 SMA", f"${summary.get('sma_200',0):.2f}", "Trend"), unsafe_allow_html=True)
    with m4: st.markdown(metric_card("AI Signal", summary.get('sentiment','N/A'), "Action"), unsafe_allow_html=True)
    st.markdown("---")


# --- Modules Logic ---
if module == "💬 AI Assistant":
    st.subheader("💬 AI Financial Assistant")
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}
    if ticker not in st.session_state.chat_histories:
        st.session_state.chat_histories[ticker] = [
            {"role": "assistant", "content": f"👋 Hello! I am ready to analyze **{ticker}**. I maintain separate memories for each asset. Ask me anything about {ticker}!"}
        ]
    for message in st.session_state.chat_histories[ticker]:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    if prompt := st.chat_input(f"Ask about {ticker}..."):
        st.session_state.chat_histories[ticker].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            bot = ChatbotAgent()
            response = bot.generate_response(ticker, prompt, summary, st.session_state.chat_histories[ticker])
            st.markdown(response)
        st.session_state.chat_histories[ticker].append({"role": "assistant", "content": response})


elif module == "📑 Deep Research":
    st.subheader("📑 AI Investment Thesis")
    researcher = ResearchAgent()
    data = researcher.run_research(ticker, summary)
    c1, c2, c3 = st.columns([1, 1, 2])
    rating_color = "#00CC96" if "BUY" in data['rating'] else "#EF553B" if "SELL" in data['rating'] else "#FECB52"
    with c1: st.markdown(f"""<div style="text-align: center; padding: 20px; background-color: #262730; border-radius: 10px; border: 1px solid {rating_color};"><h4 style="color: #888; margin: 0;">AI RATING</h4><h2 style="color: {rating_color}; margin: 10px 0; font-size: 2.2rem;">{data['rating']}</h2></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div style="text-align: center; padding: 20px; background-color: #262730; border-radius: 10px; border: 1px solid #4B6CB7;"><h4 style="color: #888; margin: 0;">TARGET PRICE</h4><h2 style="color: white; margin: 10px 0; font-size: 2.2rem;">${data['target_price']:.2f}</h2><p style="color: {'#00CC96' if data['upside'] > 0 else '#EF553B'}; font-weight: bold;">{data['upside']:+.2f}% Upside</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="verdict-box"><h4 style="color: #FFF; margin-top: 0;">🧐 Executive Verdict</h4><p style="color: #CCC; font-size: 0.95rem; line-height: 1.6;"><b>{ticker}</b> is currently analyzed as <b>{data['valuation_status']}</b>. The technical momentum is <b>{summary['sentiment']}</b>.<br><i>"{data['rating'].lower().capitalize()} based on current risk/reward."</i></p></div>""", unsafe_allow_html=True)
    st.markdown("### 🔍 Key Drivers Analysis")
    k1, k2, k3 = st.columns(3)
    k1.info(f"**Valuation:** {data['valuation_status']}"); k2.info(f"**Macro:** {data['macro_view']}"); k3.info(f"**Insiders:** {data['insider_view']}")
    st.markdown("---")

    # Sector comparison (template)
    st.markdown("### 🧭 Sector Comparison (Template)")
    try:
        peer_agent = PeerAgent()
        peer_df = peer_agent.fetch_peer_data(ticker)
        if not peer_df.empty:
            display_df = peer_df.copy()
            for col in ['Market Cap (B)']: display_df[col] = display_df[col].map('${:,.1f}B'.format)
            for col in ['P/E Ratio', 'Forward P/E']: display_df[col] = display_df[col].map('{:.1f}x'.format)
            for col in ['ROE (%)', 'Rev Growth (%)']: display_df[col] = display_df[col].map('{:.1f}%'.format)
            cols = [c for c in ['Ticker', 'Market Cap (B)', 'P/E Ratio', 'Forward P/E', 'ROE (%)', 'Rev Growth (%)'] if c in display_df.columns]
            st.markdown(display_df[cols].head(6).style.set_table_styles([{'selector': 'th', 'props': [('background-color', '#262730'), ('color', '#4B6CB7'), ('font-weight', 'bold'), ('border-bottom', '1px solid #4C566A')]}, {'selector': 'td', 'props': [('background-color', '#1C1F26'), ('color', 'white'), ('border-bottom', '1px solid #2E3440')]}, {'selector': 'tr:hover', 'props': [('background-color', '#3B4252')]}]).to_html(), unsafe_allow_html=True)
        else:
            st.info("Peer comparison data not available.")
    except Exception:
        st.info("Peer comparison data not available.")

    # Risk scenarios (template)
    st.markdown("### ⚠️ Risk Scenarios (Template)")
    st.info(
        "- **Base Case:** Gradual growth, valuation mean-reversion, stable margins.\n"
        "- **Bull Case:** Demand surprise + margin expansion, AI cycle accelerates.\n"
        "- **Bear Case:** Macro tightening + multiple compression, growth decelerates."
    )

    # Valuation rationale (template)
    st.markdown("### 🧾 Valuation Rationale (Template)")
    val_agent = ValuationAgent()
    metrics = val_agent.get_fundamentals(ticker)
    if metrics:
        fair = val_agent.calculate_fair_value(metrics)
        curr = metrics.get('Current Price', 0)
        upside = ((fair - curr) / curr) * 100 if curr else 0
        st.markdown(
            f"- **Intrinsic Value:** ${fair:.2f}\n"
            f"- **Current Price:** ${curr:.2f}\n"
            f"- **Upside/Downside:** {upside:+.1f}%\n"
            f"- **Multiples:** P/E {metrics.get('Trailing P/E', 0):.2f}x | Fwd P/E {metrics.get('Forward P/E', 0):.2f}x\n"
            f"- **Quality:** ROE {metrics.get('ROE', 0):.2%} | Margin {metrics.get('Profit Margin', 0):.2%}"
        )
    else:
        st.info("Valuation data not available.")

    with st.expander("📄 View Full Raw Report"): st.text_area("Raw Text", data['full_text'], height=400)


elif module == "🎯 Wall St. Insights":
    st.subheader("🎯 Analyst Consensus & Institutional Holdings")
    owner_agent = OwnershipAgent()
    targets, _ = owner_agent.get_analyst_consensus(ticker)
    major, inst = owner_agent.get_ownership_data(ticker)
    if targets:
        c1, c2 = st.columns([1, 2])
        with c1: 
            st.markdown("#### 🎯 Price Target Consensus")
            st.plotly_chart(owner_agent.plot_price_target(targets), use_container_width=True)
            st.info(f"**Consensus:** {targets['recommendation']}\n**Analyst Count:** {targets['num_analysts']}\n**Target Mean:** ${targets['target_mean']}")
        with c2:
            st.markdown("#### 🏦 Institutional Power")
            def render_dark_table(df): st.markdown(df.style.set_table_styles([{'selector': 'th', 'props': [('background-color', '#262730'), ('color', '#4B6CB7'), ('font-weight', 'bold'), ('border-bottom', '1px solid #4C566A')]}, {'selector': 'td', 'props': [('background-color', '#1C1F26'), ('color', 'white'), ('border-bottom', '1px solid #2E3440')]}, {'selector': 'tr:hover', 'props': [('background-color', '#3B4252')]}]).to_html(), unsafe_allow_html=True)
            if inst is not None and not inst.empty:
                st.markdown("**Top Institutional Holders:**")
                cols = [c for c in ['Holder', 'Shares', 'Date Reported', '% Out', 'Value'] if c in inst.columns]
                render_dark_table(inst.head(5)[cols] if cols else inst.head(5))
            else: st.info("Institutional holder data not available.")
        st.markdown("---")
        if major is not None and not major.empty:
             st.markdown("#### 📊 Ownership Structure")
             try:
                 major.columns = ['Percentage', 'Category'] if len(major.columns) == 2 else major.columns
                 render_dark_table(major)
             except: st.dataframe(major, use_container_width=True)
    else: st.warning("Could not fetch analyst data.")


elif module == "📊 Financial Health":
    st.subheader("📊 Financial Health & Statements")
    fin_agent = FinancialAgent()
    income, balance, cash = fin_agent.get_financials(ticker)
    if income is not None:
        st.markdown("#### 📈 Revenue vs Net Income Growth")
        st.plotly_chart(fin_agent.plot_revenue_vs_income(income), use_container_width=True)
        st.markdown("---")
        t1, t2, t3 = st.tabs(["💰 Income Statement", "🏛️ Balance Sheet", "💸 Cash Flow"])
        def format_large_numbers(x): return f"{x/1e9:,.2f}B" if isinstance(x, (int, float)) and abs(x) > 1e9 else f"{x/1e6:,.2f}M" if isinstance(x, (int, float)) else x
        def render_dark_table(df): st.markdown(df.style.format(format_large_numbers).set_table_styles([{'selector': 'th', 'props': [('background-color', '#262730'), ('color', '#4B6CB7'), ('font-weight', 'bold'), ('border-bottom', '1px solid #4C566A')]}, {'selector': 'td', 'props': [('background-color', '#1C1F26'), ('color', 'white'), ('border-bottom', '1px solid #2E3440')]}, {'selector': 'tr:hover', 'props': [('background-color', '#3B4252')]}]).to_html(), unsafe_allow_html=True)
        with t1: st.markdown("##### Annual Income Statement"); render_dark_table(income)
        with t2: st.markdown("##### Annual Balance Sheet"); render_dark_table(balance)
        with t3: st.markdown("##### Annual Cash Flow"); render_dark_table(cash)
    else: st.warning("Could not retrieve financial statements.")


elif module == "👥 Peer Comparison":
    st.subheader("👥 Peer Comparison & Sector Matrix")
    peer_agent = PeerAgent()
    with st.spinner(f"Analyzing Peers for {ticker}..."):
        peer_df = peer_agent.fetch_peer_data(ticker)
        if not peer_df.empty:
            st.markdown("#### 🔢 Valuation & Growth Matrix")
            display_df = peer_df.copy()
            for col in ['Market Cap (B)']: display_df[col] = display_df[col].map('${:,.1f}B'.format)
            for col in ['P/E Ratio', 'Forward P/E']: display_df[col] = display_df[col].map('{:.1f}x'.format)
            for col in ['ROE (%)', 'Rev Growth (%)']: display_df[col] = display_df[col].map('{:.1f}%'.format)
            st.markdown(display_df.style.apply(lambda x: ['background-color: #2E3440' if x.name == 0 else '' for i in x], axis=1).set_table_styles([{'selector': 'th', 'props': [('background-color', '#262730'), ('color', '#4B6CB7'), ('font-weight', 'bold'), ('border-bottom', '1px solid #4C566A')]}, {'selector': 'td', 'props': [('background-color', '#1C1F26'), ('color', 'white'), ('border-bottom', '1px solid #2E3440')]}, {'selector': 'tr:hover', 'props': [('background-color', '#3B4252')]}]).to_html(), unsafe_allow_html=True)
            st.markdown("---")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("#### 🕸️ Financial Health Radar")
                st.plotly_chart(peer_agent.plot_radar_chart(peer_df, ticker), use_container_width=True)
            with c2:
                st.markdown("#### 🏎️ Relative Performance (6 Months)")
                hist_df = peer_agent.fetch_price_history(ticker)
                if not hist_df.empty:
                    fig_rel = go.Figure()
                    for col in hist_df.columns:
                        width = 4 if col == ticker else 1
                        color = '#00CC96' if col == ticker else None
                        opacity = 1.0 if col == ticker else 0.5
                        fig_rel.add_trace(go.Scatter(x=hist_df.index, y=hist_df[col], mode='lines', name=col, line=dict(width=width, color=color), opacity=opacity))
                    
                    # [FIXED] Force White Font
                    fig_rel.update_layout(
                        template='plotly_dark', 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)', 
                        font=dict(color='#FFFFFF'), # Global White Font
                        xaxis=dict(showgrid=False, tickfont=dict(color='white'), title_font=dict(color='white')), 
                        yaxis=dict(title="Return (%)", gridcolor='#444', tickfont=dict(color='white'), title_font=dict(color='white')), 
                        legend=dict(orientation="h", y=1.1, font=dict(color='white'))
                    )
                    st.plotly_chart(fig_rel, use_container_width=True)
        else: st.warning("Could not fetch peer data.")


elif module == "📰 Smart News":
    st.subheader("📰 AI News Sentiment Analysis")
    news_agent = NewsAgent()
    news_items, sentiment_score = news_agent.get_news(ticker)
    # --- Events & Summary Cards ---
    try:
        stock = yf.Ticker(ticker)
        cal = stock.calendar
    except Exception:
        cal = None
    next_earnings = "N/A"
    if cal is not None and not cal.empty:
        try:
            if "Earnings Date" in cal.index:
                next_earnings = str(cal.loc["Earnings Date"].values[0])[:10]
            else:
                next_earnings = str(cal.iloc[0].values[0])[:10]
        except Exception:
            next_earnings = "N/A"
    last_dividend = "N/A"
    try:
        divs = stock.dividends if stock else None
        if divs is not None and not divs.empty:
            last_dividend = f"{divs.index[-1].date()} / ${divs.iloc[-1]:.2f}"
    except Exception:
        pass
    st.markdown("### 📌 Company Events")
    e1, e2, e3 = st.columns(3)
    with e1: st.markdown(f"<div class='qa-widget-card'><div class='qa-widget-title'>Earnings</div><h3 style='margin:0;color:#E6EDF3;'>{next_earnings}</h3></div>", unsafe_allow_html=True)
    with e2: st.markdown(f"<div class='qa-widget-card'><div class='qa-widget-title'>Dividend</div><h3 style='margin:0;color:#E6EDF3;'>{last_dividend}</h3></div>", unsafe_allow_html=True)
    with e3: st.markdown(f"<div class='qa-widget-card'><div class='qa-widget-title'>Conference</div><h3 style='margin:0;color:#E6EDF3;'>N/A</h3></div>", unsafe_allow_html=True)
    st.markdown("### 🧠 Key Summary")
    top_headline = news_items[0]['title'] if news_items else "No headline"
    st.markdown(
        f"<div class='qa-widget-card'>"
        f"<div class='qa-widget-title'>Highlights</div>"
        f"<p style='margin:0;color:#D7DEE6;'>Sentiment: <b>{sentiment_score}</b> • Headlines: <b>{len(news_items)}</b></p>"
        f"<p style='margin:6px 0 0 0;color:#BFC6D1;'>Top: {top_headline}</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    if news_items:
        c1, c2 = st.columns([1, 2])
        with c1: st.markdown(f"""<div style="background-color: #262730; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #464B5C;"><h3 style="margin:0; color: #AAA;">News Sentiment</h3><h1 style="font-size: 3rem; margin: 10px 0; color: {'#00CC96' if sentiment_score > 0 else '#EF553B' if sentiment_score < 0 else '#FECB52'};">{sentiment_score}</h1><p style="color: #FFF;">{'🔥 BULLISH' if sentiment_score > 0 else '❄️ BEARISH' if sentiment_score < 0 else '⚖️ NEUTRAL'}</p></div>""", unsafe_allow_html=True)
        with c2: st.info("**How it works:** The AI scans recent headlines for keywords like 'Growth', 'Beat', 'Loss', 'Plunge' to estimate market sentiment.")
        st.markdown("### 🗞️ Latest Headlines")
        for item in news_items:
            color = "#00CC96" if "POSITIVE" in item['sentiment'] else "#EF553B" if "NEGATIVE" in item['sentiment'] else "#888"
            clean_title = item['title'].replace("`", "").replace("**", "")
            # [FIXED] News Title Style
            st.markdown(f"""
            <a href="{item['link']}" target="_blank" style="text-decoration: none;">
                <div class="news-card">
                    <div class="news-title">{clean_title} <span class="sentiment-badge" style="border: 1px solid {color}; color: {color};">{item['sentiment']}</span></div>
                    <div class="news-meta">By {item['publisher']} • {item['date']}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
    else: st.warning("No recent news found.")


elif module == "📊 Pro Charting":
    st.subheader("📈 Technical Analysis Chart")
    preset_map = {
        "Momentum": ["EMA 20", "EMA 50", "VWAP"],
        "Trend": ["SMA 50", "SMA 200", "Donchian Channels"],
        "Volatility": ["Bollinger Bands", "Parabolic SAR"],
        "Institutional": ["SMA 20", "SMA 50", "VWAP", "Bollinger Bands"],
        "Custom": []
    }
    preset = st.selectbox("🎛️ Indicator Preset", list(preset_map.keys()), index=3)
    indicator_options = ["SMA 20", "SMA 50", "SMA 200", "EMA 20", "EMA 50", "EMA 200", "Bollinger Bands", "Parabolic SAR", "Donchian Channels", "VWAP"]
    default_indicators = preset_map[preset] if preset != "Custom" else ["SMA 20", "SMA 50", "Bollinger Bands"]
    default_indicators = [x for x in default_indicators if x in indicator_options]
    indicators = st.multiselect(
        "🛠️ Overlay Indicators:",
        indicator_options,
        default=default_indicators,
    )
    try:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.7])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC', increasing_line_color='#00CC96', decreasing_line_color='#EF553B'), row=1, col=1)
        if "SMA 20" in indicators and 'SMA_20' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#FFA15A', width=1), name='SMA 20'), row=1, col=1)
        if "SMA 50" in indicators and 'SMA_50' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#00B5F8', width=1), name='SMA 50'), row=1, col=1)
        if "SMA 200" in indicators and 'SMA_200' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='#AB63FA', width=1), name='SMA 200'), row=1, col=1)
        if "EMA 20" in indicators and 'EMA_20' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#FF6692', width=1, dash='dot'), name='EMA 20'), row=1, col=1)
        if "EMA 50" in indicators and 'EMA_50' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='#19D3F3', width=1, dash='dot'), name='EMA 50'), row=1, col=1)
        if "EMA 200" in indicators and 'EMA_200' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], line=dict(color='#FFFFFF', width=1, dash='dot'), name='EMA 200'), row=1, col=1)
        if "Bollinger Bands" in indicators and 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1), name='BB Upper', showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1), fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)', name='Bollinger Bands'), row=1, col=1)
        if "Parabolic SAR" in indicators and 'PSAR' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['PSAR'], mode='markers', marker=dict(color='white', size=4), name='Parabolic SAR'), row=1, col=1)
        if "Donchian Channels" in indicators and 'DC_Upper' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['DC_Upper'], line=dict(color='rgba(0, 204, 150, 0.5)', width=1, dash='dash'), name='Donchian High'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['DC_Lower'], line=dict(color='rgba(239, 85, 59, 0.5)', width=1, dash='dash'), name='Donchian Low'), row=1, col=1)
        if "VWAP" in indicators and 'VWAP' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='#FECB52', width=2), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#2E3440'), row=2, col=1)
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=720,
            xaxis_rangeslider_visible=False,
            font=dict(color="white"),
            legend=dict(font=dict(color="white")),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        fig.update_xaxes(showgrid=False, linecolor='#2E3440', tickfont=dict(color='white'))
        fig.update_yaxes(showgrid=True, gridcolor='rgba(46,52,64,0.4)', linecolor='#2E3440', tickfont=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Wall St. Style Theme • Preset: {preset} • {ticker} {datetime.date.today().strftime('%Y-%m-%d')}")
    except Exception as e: st.warning(f"Chart loading... {e}")


elif module == "💼 Portfolio Optimizer":
    st.subheader("🛠️ Build Your Portfolio")
    default_assets = [selected_asset_name, "S&P 500 ETF (SPY)", "Bitcoin (BTC-USD)"]
    default_options = [x for x in default_assets if x in ASSET_DATABASE]
    selected_items = st.multiselect("Select Assets to Optimize:", options=list(ASSET_DATABASE.keys()), default=default_options)
    selected_tickers = [ASSET_DATABASE[item] for item in selected_items]
    if len(selected_tickers) < 2: st.warning("⚠️ Please select at least 2 assets above to run optimization.")
    else:
        if st.button("🚀 Run Optimization Simulation"):
            with st.spinner(f"Simulating 2,000 Portfolios for {len(selected_tickers)} assets..."):
                p_agent = PortfolioAgent()
                p_data = p_agent.get_portfolio_data(selected_tickers)
                if not p_data.empty:
                    best_port, sim_data = p_agent.optimize_portfolio(p_data)
                    if best_port:
                        st.markdown("---")
                        st.subheader("🏆 Optimization Results")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("🔥 Max Sharpe Ratio", f"{best_port['Sharpe']:.2f}")
                        c2.metric("📈 Expected Return", f"{best_port['Return']:.2%}")
                        c3.metric("📉 Risk (Volatility)", f"{best_port['Volatility']:.2%}")
                        c_left, c_right = st.columns([1, 2])
                        with c_left:
                            st.markdown("#### ⚖️ Optimal Allocation")
                            weights_df = pd.DataFrame.from_dict(best_port['Weights'], orient='index', columns=['Weight']).sort_values(by='Weight', ascending=False)
                            st.markdown(weights_df.style.format("{:.2%}").set_table_styles([{'selector': 'th', 'props': [('background-color', '#262730'), ('color', '#4B6CB7'), ('font-weight', 'bold'), ('border-bottom', '1px solid #4C566A')]}, {'selector': 'td', 'props': [('background-color', '#1C1F26'), ('color', 'white'), ('border-bottom', '1px solid #2E3440')]}, {'selector': 'tr:hover', 'props': [('background-color', '#2E3440')]}]).to_html(), unsafe_allow_html=True)
                        with c_right:
                            st.markdown("#### 💼 Allocation Chart")
                            fig_alloc = go.Figure(go.Bar(x=weights_df.index, y=weights_df['Weight'], text=weights_df['Weight'].apply(lambda x: f"{x:.1%}"), textposition='auto', marker_color='#4B6CB7'))
                            fig_alloc.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0), height=300, xaxis=dict(tickfont=dict(color='white')), yaxis=dict(showgrid=False, showticklabels=False), font=dict(color='white'))
                            st.plotly_chart(fig_alloc, use_container_width=True)
                        st.markdown("---")
                        fig_ef = p_agent.plot_efficient_frontier(sim_data, best_port)
                        st.plotly_chart(fig_ef, use_container_width=True)
                else: st.error("Failed to download data for selected assets.")


elif module == "🤖 AI Strategy":
    st.subheader("🤖 Algorithmic Backtesting")
    strategist = StrategyAgent()
    backtest_data, metrics = strategist.run_backtest(df)
    if backtest_data is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Return", metrics["Total Return"], metrics["Alpha"])
        c2.metric("Win Rate", metrics["Win Rate"])
        c3.metric("Market Return", metrics["Market Return"])
        c4.metric("Alpha", metrics["Alpha"])
        fig_strategy = strategist.plot_performance(backtest_data)
        fig_strategy.update_layout(font=dict(color="white"), legend=dict(font=dict(color="white"))) 
        st.plotly_chart(fig_strategy, use_container_width=True)
    else: st.warning("Insufficient data.")
elif module == "🕸️ Supply Chain":
    st.subheader("🕸️ Global Supply Chain Network")
    sc_agent = SupplyChainAgent()
    fig_network = sc_agent.get_network_graph(ticker)
    fig_network.update_layout(font=dict(color="white"))
    st.plotly_chart(fig_network, use_container_width=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("🟢 **Suppliers**")
    c2.markdown("🔵 **Customers**")
    c3.markdown("🔴 **Competitors**")
elif module == "⚖️ Fundamental Valuation":
    st.subheader("⚖️ Fundamental Valuation Model")
    val_agent = ValuationAgent()
    metrics = val_agent.get_fundamentals(ticker)
    if metrics:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("P/E Ratio", f"{metrics.get('Trailing P/E', 'N/A')}")
        c2.metric("Forward P/E", f"{metrics.get('Forward P/E', 'N/A')}")
        c3.metric("PEG Ratio", f"{metrics.get('PEG Ratio', 'N/A')}")
        c4.metric("Price/Book", f"{metrics.get('Price/Book', 'N/A')}")
        st.markdown("---")
        fair_value = val_agent.calculate_fair_value(metrics)
        current_price = metrics.get('Current Price', 0)
        fig_val = val_agent.plot_valuation_gauge(current_price, fair_value)
        st.plotly_chart(fig_val, use_container_width=True)
        if current_price < fair_value: verdict = "🟢 UNDERVALUED"
        else: verdict = "🔴 OVERVALUED"
        st.info(f"**Verdict:** {verdict} (Upside Potential: {((fair_value - current_price) / current_price * 100):.1f}%)")
    else: st.warning("Could not fetch fundamental data.")
elif module == "🔮 Monte Carlo":
    st.subheader("🔮 Monte Carlo Forecasting")
    mc_agent = MonteCarloAgent()
    sim_df, metrics = mc_agent.run_simulation(df, days=30, simulations=1000)
    if sim_df is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Expected Price", metrics["Expected Price"])
        c2.metric("Bull Case", metrics["Bull Case (95%)"])
        c3.metric("Bear Case", metrics["Bear Case (5%)"])
        c4.metric("Volatility", metrics["Volatility"])
        fig_mc = mc_agent.plot_simulation(sim_df)
        st.plotly_chart(fig_mc, use_container_width=True)
    else: st.warning("Insufficient data.")
elif module == "🕵️ Insider Tracker":
    st.subheader("🕵️ Insider Trading Activity")
    insider = InsiderAgent()
    insider_df = insider.get_insider_trades(ticker)
    if not insider_df.empty:
        fig_insider = insider.plot_insider_sentiment(insider_df)
        
        # [MOBILE FIX] 막대 그래프 두께 강제 조정 (모바일 가시성 확보)
        # 날짜 기준 그래프에서 막대가 너무 얇게 나오는 현상을 방지하기 위해 
        # 막대 너비를 '3일' 치 시간(밀리초)으로 강제 설정합니다.
        fig_insider.update_traces(width=86400000 * 3) 
        fig_insider.update_layout(bargap=0.05)
        
        st.plotly_chart(fig_insider, use_container_width=True)
        st.markdown("### 📋 Transaction Details")
        display_df = insider_df[['Start Date', 'Insider', 'Position', 'Shares', 'Value', 'Text']]
        st.markdown(display_df.to_html(index=False, escape=False), unsafe_allow_html=True)
    else: st.info("No recent insider activity found.")
elif module == "🧊 3D Volatility":
    st.subheader("🧊 3D Implied Volatility Surface")
    current_price = summary.get('current_price', 0)
    if current_price > 0:
        vol_agent = VolatilityAgent()
        fig_vol = vol_agent.plot_surface(current_price)
        st.plotly_chart(fig_vol, use_container_width=True)
    else: st.warning("Invalid price data.")
elif module == "🔗 Correlation":
    st.subheader("🔗 Multi-Asset Correlation Matrix")
    with st.spinner("Calculating Correlations..."):
        corr_agent = CorrelationAgent()
        corr_matrix = corr_agent.get_correlations(ticker)
        if not corr_matrix.empty:
            fig_corr = corr_agent.plot_heatmap(corr_matrix)
            st.plotly_chart(fig_corr, use_container_width=True)
        else: st.warning("Could not fetch correlation data.")
elif module == "🏛️ Macro Analysis":
    st.subheader("🏛️ Fed Hawkish/Dovish Decoder")
    macro = MacroAgent()
    sentiment, text_snippet = macro.analyze_minutes()
    c1, c2 = st.columns([1, 1])
    with c1:
        fig_gauge = macro.plot_sentiment_gauge(sentiment)
        st.plotly_chart(fig_gauge, use_container_width=True)
    with c2:
        st.markdown("### 📝 AI Summary")
        st.info(f"""**Sentiment Score:** {int((sentiment+1)*50)}/100
        The AI analysis suggests a **{'HAWKISH (Tightening)' if sentiment > 0 else 'DOVISH (Easing)'}** stance.""")
        with st.expander("📄 Read Excerpt"): st.write(text_snippet)
    st.markdown("---")
    fig_dot = macro.plot_dot_plot()
    st.plotly_chart(fig_dot, use_container_width=True)
else:
    if module != "💼 Portfolio Optimizer":
        st.info(f"⏳ Waiting for data... (Ticker: {ticker})")



