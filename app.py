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
    initial_sidebar_state="expanded"
)

# 2. Streamlit 기본 스타일 숨기기 + [모바일 버튼 강제 성형]
hide_st_style = """
            <style>
            /* 기본 메뉴 숨김 */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}

            /* 🚀 [PC 화면] 사이드바 열기 버튼 커스텀 */
            [data-testid="stSidebarCollapsedControl"] {
                border: 1px solid #4B6CB7 !important;
                background-color: #161920 !important;
                border-radius: 8px !important;
                width: auto !important;
                padding: 0.5rem 1rem !important;
                margin-top: 5px;
            }
            [data-testid="stSidebarCollapsedControl"] > svg { display: none !important; }
            [data-testid="stSidebarCollapsedControl"]::after {
                content: "고급 기능 >>";
                color: #FFFFFF !important;
                font-weight: 600;
                font-size: 14px;
                white-space: nowrap;
            }

            /* 🚀 [모바일 화면] 헤더 안의 햄버거 버튼 강제 성형 */
            @media (max-width: 768px) {
                /* 헤더 높이 확보 (버튼 들어갈 공간) */
                header[data-testid="stHeader"] {
                    background-color: transparent !important;
                    height: 60px !important;
                }
                
                /* 모바일 메뉴 버튼(햄버거) 찾아서 바꾸기 */
                header[data-testid="stHeader"] button[title="View sidebar"] {
                    border: 1px solid #4B6CB7 !important;
                    background-color: #161920 !important;
                    border-radius: 8px !important;
                    width: auto !important;
                    height: auto !important;
                    padding: 8px 12px !important;
                    margin-left: 10px !important;
                    opacity: 1 !important;
                    visibility: visible !important;
                }

                /* 기존 아이콘(SVG) 숨기기 */
                header[data-testid="stHeader"] button[title="View sidebar"] svg {
                    display: none !important;
                }

                /* 새로운 텍스트 심기 */
                header[data-testid="stHeader"] button[title="View sidebar"]::after {
                    content: "고급 기능 >>";
                    color: white !important;
                    font-size: 14px !important;
                    font-weight: bold !important;
                    white-space: nowrap !important;
                }
            }
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
        border: 1px solid #4B6CB7 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        outline: none !important;
    }
    .stChatInput textarea::placeholder { color: #E0E0E0 !important; opacity: 1 !important; -webkit-text-fill-color: #E0E0E0 !important; }
    .stChatInput textarea:focus { border: 2px solid #4B6CB7 !important; box-shadow: none !important; outline: none !important; }
    
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
</style>
""", unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("🦅 QUANT AI")
    st.caption("Institutional Terminal v11.0 MEMORY")
    st.markdown("---")
    st.markdown("""<div style="text-align: left; padding: 10px; background-color: #1C1F26; border-radius: 10px; border: 1px solid #2E3440;"><p class="profile-name">👨‍💻 Jihu Park</p><p class="profile-role">Lead Quant Architect</p></div>""", unsafe_allow_html=True)
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

# 4. Data Logic
analyst = TechnicalAnalyst(ticker)
df = analyst.fetch_data()
summary = "No Data"
if not df.empty and 'Close' in df.columns:
    df = analyst.calculate_indicators()
    summary = analyst.get_summary()

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
                    pdf_file = create_pdf(ticker, summary, report_data['full_text'], filename=f"{ticker}_Report.pdf")
                    if pdf_file:
                        with open(pdf_file, "rb") as f: st.download_button("⬇️ Download PDF", f, file_name=f"{ticker}_Report.pdf")
                except: st.error("Error creating PDF.")

# --- Content ---
if module != "💼 Portfolio Optimizer" and isinstance(summary, dict) and summary != "No Data":
    st.markdown("### ⚡ Market Pulse")
    m1, m2, m3, m4 = st.columns(4)
    def metric_card(label, value, delta):
        delta_color = '#00CC96' if '+' in str(delta) or 'BULLISH' in str(delta) else '#EF553B'
        if 'NEUTRAL' in str(delta): delta_color = '#FECB52'
        return f"""<div class="metric-card"><p style="font-size: 0.85rem; margin-bottom: 8px;">{label}</p><h2 style="margin: 0; font-size: 2rem; color: #FFFFFF;">{value}</h2><p style="color: {delta_color}; font-weight: 600;">{delta}</p></div>"""
    with m1: st.markdown(metric_card("Price", f"${summary.get('current_price',0):.2f}", "Live"), unsafe_allow_html=True)
    with m2: st.markdown(metric_card("RSI (14)", f"{summary.get('rsi',0):.2f}", summary.get('sentiment','N/A')), unsafe_allow_html=True)
    with m3: st.markdown(metric_card("200 SMA", f"${summary.get('sma_200',0):.2f}", "Trend"), unsafe_allow_html=True)
    with m4: st.markdown(metric_card("AI Signal", summary.get('sentiment','N/A'), "Action"), unsafe_allow_html=True)
    st.markdown("---")

# --- Modules Logic ---
if module == "💬 AI Assistant":
    st.subheader("💬 AI Financial Assistant")
    
    # [LOGIC UPDATE] Session State per Ticker
    # 1. Initialize Global Chat History Dict if not present
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}
    
    # 2. If this specific ticker has no history, create the greeting
    if ticker not in st.session_state.chat_histories:
        st.session_state.chat_histories[ticker] = [
            {"role": "assistant", "content": f"👋 Hello! I am ready to analyze **{ticker}**. I maintain separate memories for each asset. Ask me anything about {ticker}!"}
        ]
    
    # 3. Render ONLY the history for the CURRENT ticker
    for message in st.session_state.chat_histories[ticker]:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    
    # 4. Handle Input
    if prompt := st.chat_input(f"Ask about {ticker}..."):
        # Add User Message to History
        st.session_state.chat_histories[ticker].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Generate Response
        with st.chat_message("assistant"):
            bot = ChatbotAgent()
            response = bot.generate_response(ticker, prompt, summary)
            st.markdown(response)
        
        # Add Bot Message to History
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
    indicators = st.multiselect("🛠️ Overlay Indicators:", ["SMA 20", "SMA 50", "SMA 200", "EMA 20", "EMA 50", "EMA 200", "Bollinger Bands", "Parabolic SAR", "Donchian Channels", "VWAP"], default=["SMA 20", "SMA 50", "Bollinger Bands"])
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
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#636EFA'), row=2, col=1)
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=750, xaxis_rangeslider_visible=False, font=dict(color="white"), legend=dict(font=dict(color="white")))
        st.plotly_chart(fig, use_container_width=True)
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
