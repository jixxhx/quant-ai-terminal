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
    initial_sidebar_state="collapsed" # 사이드바 기본 닫힘 (모바일 최적화)
)

# 2. 스타일 숨기기 & 모바일 최적화 스타일 (헤더 커스텀 + 가로 스크롤 메뉴)
hide_st_style = """
    <style>
    /* 기본 Streamlit 헤더 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* [Custom Header] 상단 고정바 스타일 */
    .custom-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background-color: #161920;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        border-bottom: 1px solid #262730;
    }
    .header-logo { font-size: 1.2rem; font-weight: 700; color: #F0F2F6; }
    .header-profile { font-size: 0.9rem; color: #888; display: flex; align-items: center; gap: 10px; }
    .profile-name { color: #4B6CB7; font-weight: 600; }
    
    /* 컨텐츠가 헤더에 가리지 않게 상단 여백 추가 */
    .block-container { padding-top: 80px !important; }

    /* [Mobile Menu] 가로 스크롤 버튼 컨테이너 */
    div.stRadio > div[role="radiogroup"] {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        gap: 10px;
        padding-bottom: 5px;
        scrollbar-width: none; /* Firefox 스크롤바 숨김 */
    }
    div.stRadio > div[role="radiogroup"]::-webkit-scrollbar { display: none; } /* Chrome 스크롤바 숨김 */
    
    /* 버튼 스타일 커스텀 */
    div.stRadio > div[role="radiogroup"] > label {
        background-color: #262730 !important;
        border: 1px solid #363945 !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        color: #BDC1C6 !important;
        transition: all 0.2s;
        min-width: max-content; /* 텍스트 길이에 맞게 */
    }
    div.stRadio > div[role="radiogroup"] > label:hover {
        border-color: #4B6CB7 !important;
        color: white !important;
    }
    /* 선택된 버튼 스타일 */
    div.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: #4B6CB7 !important;
        color: white !important;
        border-color: #4B6CB7 !important;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. [Custom Header] 상단 헤더 HTML 삽입 (Jihu Park 명패)
st.markdown("""
    <div class="custom-header">
        <div class="header-logo">🦅 QUANT AI</div>
        <div class="header-profile">
            <span class="profile-role">Lead Architect</span>
            <span class="profile-name">Jihu Park 👨‍💻</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. [Main Layout] 사이드바 대신 메인 화면 상단 배치
# (1) 자산 검색창 (헤더 바로 아래)
c_search, c_date = st.columns([2, 1])
with c_search:
    selected_asset_name = st.selectbox("🔍 Search Symbol", options=list(ASSET_DATABASE.keys()), index=0, label_visibility="collapsed")
    ticker = ASSET_DATABASE[selected_asset_name]
with c_date:
    st.caption(f"📅 {datetime.date.today().strftime('%Y-%m-%d')}")

# (2) 가로 스크롤 메뉴 (핵심 기능 버튼)
module = st.radio("Navigation", [
    "💬 AI Assistant", "📊 Pro Charting", "📑 Deep Research", "🎯 Wall St. Insights", 
    "📊 Financial Health", "👥 Peer Comparison", "📰 Smart News", "🤖 AI Strategy", 
    "🕸️ Supply Chain", "⚖️ Fundamental Valuation", "🔮 Monte Carlo", "💼 Portfolio Optimizer", 
    "🕵️ Insider Tracker", "🧊 3D Volatility", "🔗 Correlation", "🏛️ Macro Analysis"
], index=0, label_visibility="collapsed", horizontal=True)

# 5. Data Logic (데이터 로딩)
if module == "💼 Portfolio Optimizer":
    st.info("Configuring Portfolio...")
    summary = "No Data" # 포트폴리오 모드에선 개별 데이터 불필요
    df = pd.DataFrame()
else:
    analyst = TechnicalAnalyst(ticker)
    df = analyst.fetch_data()
    summary = "No Data"
    if not df.empty and 'Close' in df.columns:
        df = analyst.calculate_indicators()
        summary = analyst.get_summary()

# --- Content Modules (이하 로직은 기존과 동일, UI만 모바일 최적화) ---

if module != "💼 Portfolio Optimizer" and isinstance(summary, dict) and summary != "No Data":
    # Market Pulse (모바일에서는 2열로 배치하여 가독성 확보)
    st.markdown("### ⚡ Market Pulse")
    m1, m2 = st.columns(2)
    m3, m4 = st.columns(2)
    
    def metric_card(label, value, delta):
        delta_color = '#00CC96' if '+' in str(delta) or 'BULLISH' in str(delta) else '#EF553B'
        if 'NEUTRAL' in str(delta): delta_color = '#FECB52'
        return f"""<div class="metric-card" style="padding: 15px; margin-bottom: 10px;"><p style="font-size: 0.8rem; margin-bottom: 5px; color:#888;">{label}</p><h3 style="margin: 0; font-size: 1.5rem; color: #FFFFFF;">{value}</h3><p style="color: {delta_color}; font-weight: 600; font-size: 0.9rem;">{delta}</p></div>"""
    
    with m1: st.markdown(metric_card("Price", f"${summary.get('current_price',0):.2f}", "Live"), unsafe_allow_html=True)
    with m2: st.markdown(metric_card("RSI (14)", f"{summary.get('rsi',0):.2f}", summary.get('sentiment','N/A')), unsafe_allow_html=True)
    with m3: st.markdown(metric_card("200 SMA", f"${summary.get('sma_200',0):.2f}", "Trend"), unsafe_allow_html=True)
    with m4: st.markdown(metric_card("AI Signal", summary.get('sentiment','N/A'), "Action"), unsafe_allow_html=True)
    st.markdown("---")

# --- Modules Logic (기능별 화면) ---
if module == "💬 AI Assistant":
    st.subheader(f"💬 {ticker} AI Assistant")
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}
    if ticker not in st.session_state.chat_histories:
        st.session_state.chat_histories[ticker] = [
            {"role": "assistant", "content": f"👋 Hello! I am ready to analyze **{ticker}**. Ask me anything!"}
        ]
    for message in st.session_state.chat_histories[ticker]:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    if prompt := st.chat_input(f"Ask about {ticker}..."):
        st.session_state.chat_histories[ticker].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            bot = ChatbotAgent()
            response = bot.generate_response(ticker, prompt, summary)
            st.markdown(response)
        st.session_state.chat_histories[ticker].append({"role": "assistant", "content": response})

elif module == "📑 Deep Research":
    st.subheader("📑 AI Investment Thesis")
    researcher = ResearchAgent()
    data = researcher.run_research(ticker, summary)
    
    # PDF 다운로드 버튼 (리서치 탭에 통합)
    if st.button("📥 Download PDF Report", use_container_width=True):
        with st.spinner("Generating PDF..."):
            pdf_file = create_pdf(ticker, summary, data['full_text'], filename=f"{ticker}_Report.pdf")
            if pdf_file:
                with open(pdf_file, "rb") as f: st.download_button("⬇️ Save PDF", f, file_name=f"{ticker}_Report.pdf", use_container_width=True)

    c1, c2 = st.columns(2) # 모바일 최적화: 3열 -> 2열
    rating_color = "#00CC96" if "BUY" in data['rating'] else "#EF553B" if "SELL" in data['rating'] else "#FECB52"
    with c1: st.markdown(f"""<div style="text-align: center; padding: 15px; background-color: #262730; border-radius: 10px; border: 1px solid {rating_color}; margin-bottom: 10px;"><h5 style="color: #888; margin: 0;">RATING</h5><h2 style="color: {rating_color}; margin: 5px 0;">{data['rating']}</h2></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div style="text-align: center; padding: 15px; background-color: #262730; border-radius: 10px; border: 1px solid #4B6CB7; margin-bottom: 10px;"><h5 style="color: #888; margin: 0;">TARGET</h5><h2 style="color: white; margin: 5px 0;">${data['target_price']:.0f}</h2></div>""", unsafe_allow_html=True)
    
    st.info(f"**Executive Verdict:** {data['rating']} based on {data['valuation_status']} valuation and {summary['sentiment']} momentum.")
    with st.expander("📄 View Full Analysis"): st.markdown(data['full_text'])

elif module == "🎯 Wall St. Insights":
    st.subheader("🎯 Analyst Consensus")
    owner_agent = OwnershipAgent()
    targets, _ = owner_agent.get_analyst_consensus(ticker)
    major, inst = owner_agent.get_ownership_data(ticker)
    if targets:
        st.plotly_chart(owner_agent.plot_price_target(targets), use_container_width=True)
        st.info(f"**Consensus:** {targets['recommendation']} (${targets['target_mean']})")
        
        if inst is not None and not inst.empty:
            st.markdown("#### 🏦 Top Holders")
            st.dataframe(inst.head(5)[['Holder', '% Out', 'Value']], use_container_width=True)
    else: st.warning("Data unavailable.")

elif module == "📊 Financial Health":
    st.subheader("📊 Financial Health")
    fin_agent = FinancialAgent()
    income, balance, cash = fin_agent.get_financials(ticker)
    if income is not None:
        st.plotly_chart(fin_agent.plot_revenue_vs_income(income), use_container_width=True)
        t1, t2 = st.tabs(["💰 Income", "🏛️ Balance"])
        with t1: st.dataframe(income, use_container_width=True)
        with t2: st.dataframe(balance, use_container_width=True)
    else: st.warning("Data unavailable.")

elif module == "👥 Peer Comparison":
    st.subheader("👥 Peer Comparison")
    peer_agent = PeerAgent()
    peer_df = peer_agent.fetch_peer_data(ticker)
    if not peer_df.empty:
        st.dataframe(peer_df[['Ticker', 'P/E Ratio', 'Rev Growth (%)']], use_container_width=True)
        st.plotly_chart(peer_agent.plot_radar_chart(peer_df, ticker), use_container_width=True)
    else: st.warning("Data unavailable.")

elif module == "📰 Smart News":
    st.subheader("📰 AI News Sentiment")
    news_agent = NewsAgent()
    news_items, sentiment_score = news_agent.get_news(ticker)
    if news_items:
        color = '#00CC96' if sentiment_score > 0 else '#EF553B' if sentiment_score < 0 else '#FECB52'
        st.markdown(f"""<div style="padding:15px; background-color:#262730; border-radius:10px; text-align:center; border:1px solid {color}; margin-bottom:15px;"><h2 style="color:{color}; margin:0;">Score: {sentiment_score}</h2></div>""", unsafe_allow_html=True)
        for item in news_items[:5]: # 모바일은 5개만 표시
            clean_title = item['title'].replace("`", "").replace("**", "")
            st.markdown(f"""<div class="news-card"><a href="{item['link']}" style="color:white; text-decoration:none; font-weight:600;">{clean_title}</a><br><span style="font-size:0.8rem; color:#888;">{item['publisher']} • {item['date']}</span></div>""", unsafe_allow_html=True)

elif module == "📊 Pro Charting":
    st.subheader("📈 Technical Chart")
    # 차트 지표 선택 (간소화)
    indicators = st.multiselect("Indicators", ["SMA 20", "Bollinger Bands", "RSI"], default=["SMA 20", "Bollinger Bands"])
    try:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.7])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC'), row=1, col=1)
        # (기본 차트 로직 유지 - 코드 길이상 생략된 부분은 위와 동일하게 작동)
        if "SMA 20" in indicators and 'SMA_20' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#FFA15A', width=1), name='SMA 20'), row=1, col=1)
        if "Bollinger Bands" in indicators and 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1), name='BB Upper', showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1), fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)', name='Bollinger Bands'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=500, xaxis_rangeslider_visible=False, font=dict(color="white"), margin=dict(l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    except: st.error("Chart Error")

elif module == "💼 Portfolio Optimizer":
    st.subheader("🛠️ Portfolio Tool")
    assets = st.multiselect("Select Assets", list(ASSET_DATABASE.keys()), default=["Apple (AAPL)", "Tesla (TSLA)"])
    if st.button("🚀 Optimize", use_container_width=True):
        p_agent = PortfolioAgent()
        sel_tickers = [ASSET_DATABASE[a] for a in assets]
        p_data = p_agent.get_portfolio_data(sel_tickers)
        if not p_data.empty:
            best, sim = p_agent.optimize_portfolio(p_data)
            c1, c2 = st.columns(2)
            c1.metric("Return", f"{best['Return']:.1%}")
            c2.metric("Sharpe", f"{best['Sharpe']:.2f}")
            st.dataframe(pd.DataFrame.from_dict(best['Weights'], orient='index', columns=['Weight']), use_container_width=True)
            st.plotly_chart(p_agent.plot_efficient_frontier(sim, best), use_container_width=True)

elif module == "🤖 AI Strategy":
    st.subheader("🤖 Backtest")
    strategist = StrategyAgent()
    backtest_data, metrics = strategist.run_backtest(df)
    if backtest_data is not None:
        c1, c2 = st.columns(2)
        c1.metric("Total Return", metrics["Total Return"])
        c2.metric("Win Rate", metrics["Win Rate"])
        st.plotly_chart(strategist.plot_performance(backtest_data), use_container_width=True)

elif module == "🕸️ Supply Chain":
    st.subheader("🕸️ Supply Chain")
    sc_agent = SupplyChainAgent()
    st.plotly_chart(sc_agent.get_network_graph(ticker), use_container_width=True)

elif module == "⚖️ Fundamental Valuation":
    st.subheader("⚖️ Valuation")
    val_agent = ValuationAgent()
    metrics = val_agent.get_fundamentals(ticker)
    if metrics:
        fair_value = val_agent.calculate_fair_value(metrics)
        st.plotly_chart(val_agent.plot_valuation_gauge(metrics.get('Current Price',0), fair_value), use_container_width=True)
        st.dataframe(pd.DataFrame([metrics]), use_container_width=True)

elif module == "🔮 Monte Carlo":
    st.subheader("🔮 Monte Carlo")
    mc_agent = MonteCarloAgent()
    sim_df, metrics = mc_agent.run_simulation(df)
    if sim_df is not None:
        st.plotly_chart(mc_agent.plot_simulation(sim_df), use_container_width=True)
        st.info(f"Exp Price: ${metrics['Expected Price']}")

elif module == "🕵️ Insider Tracker":
    st.subheader("🕵️ Insider Trades")
    insider = InsiderAgent()
    insider_df = insider.get_insider_trades(ticker)
    if not insider_df.empty:
        fig = insider.plot_insider_sentiment(insider_df)
        fig.update_traces(width=86400000*3) # 모바일 두께 보정
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(insider_df[['Start Date', 'Insider', 'Position', 'Shares', 'Value']], use_container_width=True)

elif module == "🧊 3D Volatility":
    st.subheader("🧊 Volatility Surface")
    vol_agent = VolatilityAgent()
    st.plotly_chart(vol_agent.plot_surface(summary.get('current_price', 100)), use_container_width=True)

elif module == "🔗 Correlation":
    st.subheader("🔗 Correlations")
    corr_agent = CorrelationAgent()
    st.plotly_chart(corr_agent.plot_heatmap(corr_agent.get_correlations(ticker)), use_container_width=True)

elif module == "🏛️ Macro Analysis":
    st.subheader("🏛️ Fed Analysis")
    macro = MacroAgent()
    sentiment, _ = macro.analyze_minutes()
    st.plotly_chart(macro.plot_sentiment_gauge(sentiment), use_container_width=True)
    st.plotly_chart(macro.plot_dot_plot(), use_container_width=True)

else:
    if module != "💼 Portfolio Optimizer": st.info("Loading...")
