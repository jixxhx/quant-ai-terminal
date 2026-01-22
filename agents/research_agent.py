import datetime
import pandas as pd
from .technical_agent import TechnicalAnalyst
from .valuation_agent import ValuationAgent
from .macro_agent import MacroAgent
from .insider_agent import InsiderAgent

class ResearchAgent:
    def __init__(self):
        pass

    def run_research(self, ticker, technical_summary):
        """
        Returns a STRUCTURED dictionary containing analysis data + full text report.
        """
        # 1. Gather Intelligence
        val_agent = ValuationAgent()
        macro_agent = MacroAgent()
        insider_agent = InsiderAgent()

        # Fundamentals
        fund_metrics = val_agent.get_fundamentals(ticker)
        fair_value = 0
        valuation_status = "N/A"
        upside = 0
        
        if fund_metrics:
            fair_value = val_agent.calculate_fair_value(fund_metrics)
            current_price = fund_metrics.get('Current Price', 0)
            if current_price > 0:
                upside = ((fair_value - current_price) / current_price) * 100
                if upside > 15: valuation_status = "Undervalued"
                elif upside > 5: valuation_status = "Slightly Undervalued"
                elif upside > -5: valuation_status = "Fairly Valued"
                else: valuation_status = "Overvalued"

        # Macro
        macro_sentiment, _ = macro_agent.analyze_minutes()
        macro_outlook = "Hawkish" if macro_sentiment > 0 else "Dovish"

        # Insider
        insider_df = insider_agent.get_insider_trades(ticker)
        insider_score = 0
        if not insider_df.empty:
            if 'Box' in insider_df.columns:
                buys = len(insider_df[insider_df['Box'] == 'P'])
                sells = len(insider_df[insider_df['Box'] == 'S'])
            elif 'Transaction' in insider_df.columns: # Fallback
                trans = insider_df['Transaction'].astype(str)
                buys = len(insider_df[trans.str.contains('Buy', case=False, na=False)])
                sells = len(insider_df[trans.str.contains('Sale', case=False, na=False)])
            else:
                buys, sells = 0, 0
            
            if buys > sells: insider_score = 1
            elif sells > buys: insider_score = -1

        # 2. Scoring & Rating
        score = 0
        if technical_summary['sentiment'] == "BULLISH": score += 2
        elif technical_summary['sentiment'] == "BEARISH": score -= 2
        
        if upside > 15: score += 3
        elif upside > 5: score += 1
        elif upside < -10: score -= 2
        
        if macro_sentiment < 0: score += 1
        score += insider_score

        if score >= 4: rating = "STRONG BUY"
        elif score >= 1: rating = "BUY"
        elif score >= -1: rating = "HOLD"
        else: rating = "SELL"

        # 3. Generate Full Text Report (For PDF)
        full_report = f"""
EQUITY RESEARCH: {ticker}
Date: {datetime.date.today().strftime('%Y-%m-%d')}
Rating: {rating}
Target: ${fair_value:.2f} ({upside:+.1f}%)

1. VALUATION: {valuation_status.upper()}
The stock is trading at a P/E of {fund_metrics.get('Trailing P/E', 'N/A')}x. Our intrinsic value model suggests a target of ${fair_value:.2f}.

2. TECHNICALS: {technical_summary['sentiment']}
RSI is at {technical_summary['rsi']:.1f}. Price is trading {'above' if technical_summary['current_price'] > technical_summary['sma_200'] else 'below'} the 200-day moving average.

3. MACRO & INSIDER
Fed Stance: {macro_outlook}
Insider Activity: {'Net Buying' if insider_score > 0 else 'Net Selling' if insider_score < 0 else 'Neutral'}
"""
        
        # Return Structured Data for UI
        return {
            "ticker": ticker,
            "rating": rating,
            "target_price": fair_value,
            "upside": upside,
            "risk_score": score,
            "valuation_status": valuation_status,
            "macro_view": macro_outlook,
            "insider_view": 'Accumulation' if insider_score > 0 else 'Distribution' if insider_score < 0 else 'Neutral',
            "full_text": full_report.strip()
        }

    def generate_analysis(self, ticker, summary):
        # Wrapper for backward compatibility if needed, but we prefer run_research
        data = self.run_research(ticker, summary)
        return data['full_text']
