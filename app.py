import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
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
    initial_sidebar_state="collapsed"  # 사이드바 닫음 (모바일 최적화)
)

# 2. 스타일 설정 (헤더 + 가로 스크롤 메뉴 + 기존 스타일)
st.markdown("""
<style>
    /* 기본 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 폰트 및 다크모드 기본 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0E1117; }
    
    /* [Custom Header] 상단 고정바 */
    .custom-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background-color: #161920;
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        border-bottom: 1px solid #262730;
    }
    .header-logo { font-size: 1.1rem; font-weight: 700; color: #F0F2F6; display: flex; align-items: center; gap: 8px;}
    .header-profile { font-size: 0.85rem; color: #888; display: flex; flex-direction: column; align-items: flex-end; line-height: 1.2; }
    .profile-name { color: #4B6CB7; font-weight: 600; }
    
    /* 컨텐츠가 헤더에 가리지 않게 여백 추가 */
    .block-container { padding-top: 80px !important; }

    /* [Mobile Menu] 가로 스크롤 버튼 컨테이너 */
    div.stRadio > div[role="radiogroup"] {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        gap: 8px;
        padding-bottom: 5px;
        scrollbar-width: none;
    }
    div.stRadio > div[role="radiogroup"]::-webkit-scrollbar { display: none; }
    
    /* 버튼 스타일 */
    div.stRadio > div[role="radiogroup"] > label {
        background-color: #262730 !important;
        border: 1px solid #363945 !important;
        border-radius: 18px !important;
        padding: 6px 14px !important;
        color: #BDC1C6 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s;
        min-width: max-content;
    }
    div.stRadio > div[role="radiogroup"] > label:hover {
        border-color: #4B6CB7 !important;
        color: white !important;
    }
    div.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: #4B6CB7 !important;
        color: white !important;
        border-color: #4B6CB7 !important;
    }

    /* 기타 컴포넌트 스타일 (채팅창 등 기존 유지) */
    .stTextInput > div > div > input { border-radius: 10px; background-color: #262730; color: #FFFFFF; border: 1px solid #363945; }
    .stTextArea textarea { background-color: #1C1F26 !important; color: #FFFFFF !important; border: 1px solid #2E3440 !important; border-radius: 10px; }
    .stChatInput textarea { background-color: #262730 !important; color: #FFFFFF !important; border: 1px solid #4B6CB7 !important; border-radius: 12px !important; }
    [data-testid="stChatMessage"] { background-color: #161920 !important; border: 1px solid #2E3440 !important; border-radius: 10px !important; }
    .metric-card { background-color: #1D2028; border-radius: 12px; padding: 24px; border: 1px solid #31333F; text-align: center; }
    .news-card { background-color: #1C1F26; padding: 15px; border-radius: 10px; border: 1px solid #2E3440; margin-bottom: 10px; transition: transform 0.2s; }
    .news-title { font-weight: 600; color: #FFFFFF !important; font-size: 1.05rem; text-decoration: none; display: block; margin-bottom: 5px; }
    .sentiment-badge { font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-left: 10px; }
    .verdict-box { background-color: #161920; border-left: 4px solid #4B6CB7; padding: 15px; border-radius: 0 10px 10px 0; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# 3. [Custom Header] 상단 고정 헤더 (사이드바 대체)
st.markdown("""
    <div class="custom-header">
        <div class="header-logo">🦅 QUANT AI</div>
        <div class="header-profile">
            <span class="profile-name">Jihu Park 👨‍💻</span>
            <span style="font-size: 0.75rem;">Lead Quant Architect</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. [Main Control] 검색창 & 메뉴 (메인 화면 상단 배치)
c1, c2 = st.columns([2, 1])
with c1:
    selected_asset_name = st.selectbox("Search Asset", options=list(ASSET_DATABASE.keys()), index=0, label_visibility="collapsed")
    ticker = ASSET_DATABASE[selected_asset_name]
with c2:
    st.caption(f"📅 {datetime.date.today().strftime('%Y-%m-%d')}")

# [핵심] 가로 스크롤 메뉴 버튼 (엄지손가락 친화적)
module = st.radio("Menu", [
    "💬 AI Assistant", "📊 Pro Charting", "📑 Deep Research", "🎯 Wall St. Insights", 
    "📊 Financial Health", "👥 Peer Comparison", "📰 Smart News", "🤖 AI Strategy", 
    "🕸️ Supply Chain", "⚖️ Fundamental Valuation", "🔮 Monte Carlo", "💼 Portfolio Optimizer", 
    "🕵️ Insider Tracker", "🧊 3D Volatility", "🔗 Correlation", "🏛️ Macro Analysis"
], index=0, horizontal=True, label_visibility="collapsed")

# 5. Data Logic (여기서부턴 기존 로직 100% 동일)
if module == "💼 Portfolio Optimizer":
    st.info("Configuring Portfolio...")
    summary = "No Data" 
    df = pd.DataFrame() # 빈 데이터프레임
else:
    analyst = TechnicalAnalyst(ticker)
    df = analyst.fetch_data()
    summary = "No Data"
    if not df.empty and 'Close' in df.columns:
        df = analyst.calculate_indicators()
        summary = analyst.get_summary()

# 6. Main Dashboard & Content (기존 코드 유지)
if module != "💼 Portfolio Optimizer":
    st.markdown(f"### {ticker} Dashboard") # 타이틀 간소화

# PDF Export Button
if module != "💼 Portfolio Optimizer" and module != "💬 AI Assistant" and not df.empty and isinstance(summary, dict):
    if st.button("📥 Export PDF Report", use_container_width=True): # 버튼 너비 꽉 차게
        with st.spinner("Generating..."):
            try:
                researcher = ResearchAgent()
                report_data = researcher.run_research(ticker, summary)
                pdf_file = create_pdf(ticker, summary, report_data['full_text'], filename=f"{ticker}_Report.pdf")
                if pdf_file:
                    with open(pdf_file, "rb") as f: st.download_button("⬇️ Download PDF", f, file_name=f"{ticker}_Report.pdf", use_container_width=True)
            except: st.error("Error creating PDF.")

# --- Content Modules (기존 코드 그대로 붙임) ---
if module != "💼 Portfolio Optimizer" and isinstance(summary, dict) and summary != "No Data":
    st.markdown("---")
    # 모바일 가독성을 위해 2열 배치로 변경
    m1, m2 = st.columns(2)
    m3, m4 = st.columns(2)
    
    def metric_card(label, value, delta):
        delta_color = '#00CC96' if '+' in str(delta) or 'BULLISH' in str(delta) else '#EF553B'
        if 'NEUTRAL' in str(delta): delta_color = '#FECB52'
        return f"""<div class="metric-card" style="padding: 15px; margin-bottom: 10px;"><p style="font-size: 0.8rem; margin-bottom: 5px; color: #AAA;">{label}</p><h3 style="margin: 0; font-size: 1.5rem; color: #FFFFFF;">
