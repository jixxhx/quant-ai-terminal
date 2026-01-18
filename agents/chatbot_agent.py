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

    def _build_messages(self, ticker, query, technical_summary, history):
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
            "사용자가 어떤 질문을 하든 자연스럽고 사람처럼 한국어로 답하세요. "
            "금융/자산 관련 질문에는 제공된 컨텍스트를 활용하고, "
            "관련 없는 질문에는 일반 대화처럼 답하세요. "
            "실시간 정보는 추측하지 말고 한계를 투명하게 말하세요. "
            "개인 투자 자문이나 확정적 수익 보장은 피하세요."
        )
        messages = [{"role": "system", "content": system_prompt}]
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

        # --- 0. Premium LLM (if configured) ---
        llm_response = self._llm_chat(ticker, query, technical_summary, history)
        if llm_response:
            return llm_response

        # --- 1. Math (Priority) ---
        math_result = self._solve_math(query_lower)
        if math_result: return math_result

        # --- 2. Definitions ---
        term_def = self._explain_term(query_lower)
        if term_def: return term_def

        # --- 3. The "Give me everything" Intent ---
        comprehensive_triggers = ["everything", "all", "summary", "report", "overview", "tell me about", "brief", "analysis", "is it good", "buy or sell", "outlook"]
        if any(x in query_lower for x in comprehensive_triggers) or query_lower == ticker.lower():
            return self._get_comprehensive_summary(ticker, technical_summary)

        # --- 4. Specific Intents ---

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

        # --- 5. Smart Fallback ---
        curr_price = technical_summary.get('current_price', 0)
        trend = technical_summary.get('sentiment', 'Neutral')
        
        return (f"🤖 That's an interesting question regarding **{query}**.\n\n"
                f"While my specialized modules focus on quantitative analysis, I *can* tell you that **{ticker}** is currently trading at **${curr_price:.2f}** with a **{trend}** trend.\n\n"
                f"Would you like a **full summary** or a **valuation check** instead?")
