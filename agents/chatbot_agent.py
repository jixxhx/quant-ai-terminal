import os
import re
import datetime
import pandas as pd
from .technical_agent import TechnicalAnalyst
from .valuation_agent import ValuationAgent
from .news_agent import NewsAgent
from .macro_agent import MacroAgent
from .ownership_agent import OwnershipAgent
from .financial_agent import FinancialAgent
from .peer_agent import PeerAgent
from .supply_chain_agent import SupplyChainAgent
from .insider_agent import InsiderAgent

class ChatbotAgent:
    def __init__(self):
        # Initialize ALL Intelligence Modules
        self.val_agent = ValuationAgent()
        self.news_agent = NewsAgent()
        self.macro_agent = MacroAgent()
        self.owner_agent = OwnershipAgent()
        self.fin_agent = FinancialAgent()
        self.peer_agent = PeerAgent()
        self.sc_agent = SupplyChainAgent()
        self.insider_agent = InsiderAgent()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI()
            except Exception:
                try:
                    import openai
                    self.client = openai
                except Exception:
                    self.client = None

    def _detect_language(self, text):
        if re.search(r"[가-힣]", text or ""):
            return "Korean"
        return "English"

    def _is_news_query(self, query_lower):
        keywords = [
            "news", "headline", "headlines", "latest", "happen", "what news", "smart news",
            "뉴스", "헤드라인", "이슈", "최근", "무슨 소식", "무슨 일", "소식"
        ]
        return any(k in query_lower for k in keywords)

    def _is_chart_query(self, query_lower):
        keywords = [
            "chart", "pro chart", "prochart", "technical", "indicator", "price",
            "차트", "프로차트", "그래프", "기술적", "지표", "캔들"
        ]
        return any(k in query_lower for k in keywords)

    def _is_feature_query(self, query_lower):
        keywords = [
            "what can you do", "features", "capabilities", "modules", "how to use",
            "기능", "할 수", "사용법", "모듈", "어떤 기능", "소개"
        ]
        return any(k in query_lower for k in keywords)

    def _match_features(self, query_lower):
        feature_map = {
            "news": ["news", "smart news", "headline", "headlines", "latest", "뉴스", "헤드라인", "이슈", "소식"],
            "pro_chart": ["chart", "pro chart", "prochart", "technical", "indicator", "차트", "프로차트", "그래프", "기술적", "지표"],
            "deep_research": ["deep research", "research", "thesis", "리서치", "투자", "분석", "보고서"],
            "wall_st": ["wall st", "analyst", "consensus", "월가", "애널리스트", "목표가", "컨센서스"],
            "financial": ["financial health", "financials", "재무", "실적", "손익", "대차", "cashflow"],
            "peer": ["peer", "comparison", "동종", "경쟁", "피어", "sector"],
            "portfolio": ["portfolio", "optimizer", "asset allocation", "포트폴리오", "자산배분", "최적화"],
            "strategy": ["strategy", "backtest", "알고리즘", "전략", "백테스트"],
            "supply_chain": ["supply chain", "공급망", "밸류체인", "네트워크"],
            "valuation": ["valuation", "fair value", "intrinsic", "밸류에이션", "가치", "내재가치"],
            "monte_carlo": ["monte carlo", "simulation", "시뮬레이션"],
            "insider": ["insider", "내부자", "인사이더"],
            "volatility": ["volatility", "implied vol", "변동성", "iv"],
            "correlation": ["correlation", "상관", "상관관계"],
            "macro": ["macro", "fed", "금리", "거시", "fomc"],
            "what_if": ["what-if", "what if", "시나리오", "충격", "민감도", "가정"]
        }
        matched = []
        for feature_id, keys in feature_map.items():
            if any(k in query_lower for k in keys):
                matched.append(feature_id)
        return matched

    def _build_messages(self, ticker, query, technical_summary, history):
        user_lang = self._detect_language(query)
        today = datetime.date.today().strftime("%Y-%m-%d")
        context = {
            "ticker": ticker,
            "date": today,
            "current_price": technical_summary.get("current_price"),
            "rsi": technical_summary.get("rsi"),
            "sma_200": technical_summary.get("sma_200"),
            "sentiment": technical_summary.get("sentiment"),
        }
        system_prompt = (
            "당신은 퀀트 터미널 안의 프리미엄 금융 어시스턴트입니다. "
            "사용자의 언어(한국어/영어)에 맞춰 동일한 언어로 자연스럽게 답하세요. "
            "이전 대화의 언어는 무시하고, 가장 최근 사용자 질문의 언어만 따르세요. "
            "금융/자산 관련 질문에는 제공된 컨텍스트를 활용하고, "
            "관련 없는 질문에는 일반 대화처럼 답하세요. "
            "실시간 정보는 추측하지 말고 한계를 투명하게 말하세요. "
            "개인 투자 자문이나 확정적 수익 보장은 피하세요."
        )
        messages = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "system", "content": f"Respond strictly in {user_lang}."})
        messages.append({"role": "user", "content": f"Context: {context}"})
        if history:
            for msg in history[-8:]:
                role = msg.get("role")
                content = msg.get("content")
                if role in {"user", "assistant"} and content:
                    messages.append({"role": role, "content": content})
        else:
            messages.append({"role": "user", "content": query})
        return messages

    def _format_news_response(self, ticker, news_items, sentiment_score, user_lang):
        if not news_items:
            if user_lang == "Korean":
                return f"### 📰 Smart News Briefing\n현재 {ticker}에 대한 최근 뉴스가 없습니다."
            return f"### 📰 Smart News Briefing\nNo recent news found for {ticker}."

        sentiment_label = "BULLISH" if sentiment_score > 0 else "BEARISH" if sentiment_score < 0 else "NEUTRAL"
        top_headline = news_items[0]["title"].replace("`", "").replace("**", "")
        if user_lang == "Korean":
            res = (
                f"### 📰 Smart News Briefing ({ticker})\n"
                f"- 감성 스코어: **{sentiment_score}** ({sentiment_label})\n"
                f"- 헤드라인 수: **{len(news_items)}**\n"
                f"- Top Headline: **{top_headline}**\n\n"
                f"아래에 Smart News 패널을 표시했습니다.\n"
            )
        else:
            res = (
                f"### 📰 Smart News Briefing ({ticker})\n"
                f"- Sentiment Score: **{sentiment_score}** ({sentiment_label})\n"
                f"- Headlines: **{len(news_items)}**\n"
                f"- Top Headline: **{top_headline}**\n\n"
                f"I've displayed the Smart News panel below.\n"
            )

        return f"{res}[[SHOW_FEATURE:news]]"

    def _format_chart_response(self, ticker, technical_summary, user_lang):
        trend = technical_summary.get("sentiment", "Neutral")
        rsi = technical_summary.get("rsi", 50)
        price = technical_summary.get("current_price", 0)
        if user_lang == "Korean":
            return (
                f"### 📈 Pro Charting\n"
                f"- 현재가: **${price:.2f}**\n"
                f"- 트렌드: **{trend}**\n"
                f"- RSI: **{rsi:.2f}**\n\n"
                f"요청하신 프로 차트를 아래에 표시했습니다.\n"
                f"[[SHOW_FEATURE:pro_chart]]"
            )
        return (
            f"### 📈 Pro Charting\n"
            f"- Price: **${price:.2f}**\n"
            f"- Trend: **{trend}**\n"
            f"- RSI: **{rsi:.2f}**\n\n"
            f"I've displayed the pro chart below.\n"
            f"[[SHOW_FEATURE:pro_chart]]"
        )

    def _format_feature_response(self, user_lang):
        if user_lang == "Korean":
            return (
                "### 🧩 Quant AI Terminal 기능 요약\n"
                "- **Smart News**: 최신 헤드라인 + 감성 스코어 요약\n"
                "- **Pro Charting**: 멀티 지표 프리셋 기반 차트\n"
                "- **AI Assistant**: 자연어 질문/요약/분석\n"
                "- **PDF 리포트**: 월가 스타일 보고서 자동 생성\n"
                "- **What-If 시뮬레이터**: 거시 변수 충격 시나리오 분석\n"
            )
        return (
            "### 🧩 Quant AI Terminal Features\n"
            "- **Smart News**: headline scan + sentiment score\n"
            "- **Pro Charting**: multi-indicator presets\n"
            "- **AI Assistant**: natural-language Q&A\n"
            "- **PDF Report**: Wall Street-style report\n"
            "- **What-If Simulator**: macro shock scenarios\n"
        )

    def _format_feature_showcase(self, feature_ids, user_lang):
        labels = {
            "news": "Smart News",
            "pro_chart": "Pro Charting",
            "deep_research": "Deep Research",
            "wall_st": "Wall St. Insights",
            "financial": "Financial Health",
            "peer": "Peer Comparison",
            "portfolio": "Portfolio Optimizer",
            "strategy": "AI Strategy",
            "supply_chain": "Supply Chain",
            "valuation": "Fundamental Valuation",
            "monte_carlo": "Monte Carlo",
            "insider": "Insider Tracker",
            "volatility": "3D Volatility",
            "correlation": "Correlation",
            "macro": "Macro Analysis",
            "what_if": "What-If Simulator"
        }
        title = "요청하신 기능을 바로 보여드릴게요." if user_lang == "Korean" else "Here are the features you asked for."
        lines = [f"### ✅ {title}"]
        for feature_id in feature_ids:
            label = labels.get(feature_id, feature_id)
            lines.append(f"- **{label}**")
        token_block = "".join([f"[[SHOW_FEATURE:{fid}]]" for fid in feature_ids])
        return "\n".join(lines) + f"\n{token_block}"

    def _llm_chat(self, ticker, query, technical_summary, history):
        if not self.api_key or self.client is None:
            return None
        messages = self._build_messages(ticker, query, technical_summary, history)
        try:
            if hasattr(self.client, "chat"):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=700,
                )
                return response.choices[0].message.content.strip()
            if hasattr(self.client, "ChatCompletion"):
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=700,
                )
                return response.choices[0].message["content"].strip()
        except Exception:
            return None

    def _solve_math(self, query):
        """
        Extracts and solves math expressions accurately.
        """
        cleaned = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', query)
        if not any(op in cleaned for op in ['+', '-', '*', '/']):
            return None
        try:
            result = eval(cleaned)
            return f"🧮 **Calculation:** {cleaned.strip()} = **{result}**"
        except:
            return None

    def _explain_term(self, query):
        """
        Financial Dictionary.
        """
        glossary = {
            "rsi": "**RSI (Relative Strength Index)**: Momentum indicator. >70 Overbought, <30 Oversold.",
            "pe ratio": "**P/E Ratio**: Price-to-Earnings ratio. Valuation metric.",
            "eps": "**EPS**: Earnings Per Share. Profit divided by outstanding shares.",
            "market cap": "**Market Cap**: Total value of company shares.",
            "beta": "**Beta**: Volatility measure relative to the market.",
            "moving average": "**MA**: Average price over a specific period (e.g., 200 days).",
            "short": "**Short Selling**: Betting that a stock price will decline.",
            "long": "**Long Position**: Buying a stock expecting it to rise."
        }
        for term, definition in glossary.items():
            if term in query:
                return f"📖 **Term Definition:**\n\n{definition}"
        return None

    def _get_comprehensive_summary(self, ticker, technical_summary):
        """
        Generates a 'Give me everything' report.
        """
        # 1. Valuation
        metrics = self.val_agent.get_fundamentals(ticker)
        val_status = "N/A"
        if metrics:
            fair = self.val_agent.calculate_fair_value(metrics)
            curr = metrics.get('Current Price', 0)
            upside = ((fair - curr) / curr) * 100
            val_status = f"Fair Value ${fair:.2f} ({upside:+.1f}% Upside)"

        # 2. Wall St
        targets, _ = self.owner_agent.get_analyst_consensus(ticker)
        wall_st = "N/A"
        if targets:
            wall_st = f"{targets['recommendation']} (Target: ${targets['target_mean']})"

        # 3. News
        _, score = self.news_agent.get_news(ticker)
        news_sentiment = "Positive 🔥" if score > 0 else "Negative ❄️"

        return (f"### 🦅 Executive Briefing: {ticker}\n\n"
                f"Here is the comprehensive analysis you requested:\n\n"
                f"**1. Valuation:** {val_status}\n"
                f"**2. Technicals:** Trend is **{technical_summary.get('sentiment', 'N/A')}**, RSI is {technical_summary.get('rsi', 0):.1f}.\n"
                f"**3. Wall St:** Analysts rate it as **{wall_st}**.\n"
                f"**4. Sentiment:** Market news is currently **{news_sentiment}**.\n\n"
                f"💡 *Overall, {ticker} shows a interesting mix of technical momentum and fundamental value.*")

    def generate_response(self, ticker, query, technical_summary, history=None):
        """
        Super-Intelligent Router.
        """
        query_lower = query.lower().strip()
        user_lang = self._detect_language(query)

        # --- 0. Internal Intents (always prefer internal data) ---
        if self._is_news_query(query_lower):
            news_items, sentiment_score = self.news_agent.get_news(ticker)
            return self._format_news_response(ticker, news_items, sentiment_score, user_lang)

        if self._is_chart_query(query_lower):
            return self._format_chart_response(ticker, technical_summary, user_lang)

        if self._is_feature_query(query_lower):
            return self._format_feature_response(user_lang)

        matched_features = self._match_features(query_lower)
        if matched_features:
            return self._format_feature_showcase(matched_features, user_lang)

        # --- 1. Premium LLM (if configured) ---
        llm_response = self._llm_chat(ticker, query, technical_summary, history)
        if llm_response:
            return llm_response

        # --- 2. Math (Priority) ---
        math_result = self._solve_math(query_lower)
        if math_result: return math_result

        # --- 3. Definitions ---
        term_def = self._explain_term(query_lower)
        if term_def: return term_def

        # --- 4. The "Give me everything" Intent ---
        comprehensive_triggers = ["everything", "all", "summary", "report", "overview", "tell me about", "brief", "analysis", "is it good", "buy or sell", "outlook"]
        if any(x in query_lower for x in comprehensive_triggers) or query_lower == ticker.lower():
            return self._get_comprehensive_summary(ticker, technical_summary)

        # --- 5. Specific Intents ---

        # Valuation
        if any(x in query_lower for x in ["value", "fair", "price", "target", "cheap", "expensive"]):
            metrics = self.val_agent.get_fundamentals(ticker)
            if metrics:
                fair = self.val_agent.calculate_fair_value(metrics)
                curr = metrics.get('Current Price', 0)
                upside = ((fair - curr) / curr) * 100
                return f"### 💰 Valuation\n**{ticker}** Fair Value: **${fair:.2f}** (Upside: {upside:+.2f}%).\nCurrent Price: ${curr:.2f}."

        # Technicals
        elif any(x in query_lower for x in ["trend", "rsi", "chart", "tech", "mov", "momentum"]):
            rsi = technical_summary.get('rsi', 50)
            sent = technical_summary.get('sentiment', 'Neutral')
            sma = technical_summary.get('sma_200', 0)
            price = technical_summary.get('current_price', 0)
            return f"### 📈 Technicals\nTrend: **{sent}**\nRSI: **{rsi:.2f}**\nPrice is {'above' if price > sma else 'below'} the 200-day SMA."

        # News
        elif any(x in query_lower for x in ["news", "head", "sentim", "happen", "latest"]):
            news, score = self.news_agent.get_news(ticker)
            sentiment = "Bullish" if score > 0 else "Bearish"
            res = f"### 📰 News ({sentiment})\n"
            for item in news[:3]:
                res += f"- [{item['title'].replace('`','').replace('**','')}]({item['link']})\n"
            return res

        # Wall St
        elif any(x in query_lower for x in ["wall", "analyst", "instit", "consens"]):
            targets, _ = self.owner_agent.get_analyst_consensus(ticker)
            if targets:
                return f"### 🎯 Consensus\nRating: **{targets['recommendation']}**\nAvg Target: **${targets['target_mean']}**"

        # General Chat
        greetings = ["hi", "hello", "hey", "how are you", "greeting", "morning", "afternoon"]
        if any(x in query_lower for x in greetings):
            return f"👋 Hello! I am fully analyzing **{ticker}** in real-time. Ask me for a summary, valuation, or news!"

        # --- 6. Smart Fallback ---
        curr_price = technical_summary.get('current_price', 0)
        trend = technical_summary.get('sentiment', 'Neutral')
        
        return (f"🤖 That's an interesting question regarding **{query}**.\n\n"
                f"While my specialized modules focus on quantitative analysis, I *can* tell you that **{ticker}** is currently trading at **${curr_price:.2f}** with a **{trend}** trend.\n\n"
                f"Would you like a **full summary** or a **valuation check** instead?")
