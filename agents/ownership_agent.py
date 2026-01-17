import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

class OwnershipAgent:
    def __init__(self):
        pass

    def get_ownership_data(self, ticker):
        """
        Fetches Major Holders and Institutional Holders.
        """
        try:
            stock = yf.Ticker(ticker)
            
            # 1. Major Holders (Inside vs Inst)
            major = stock.major_holders
            # 2. Institutional Holders (Specific Funds)
            inst = stock.institutional_holders
            
            return major, inst
        except Exception as e:
            print(f"Ownership Data Error: {e}")
            return None, None

    def get_analyst_consensus(self, ticker):
        """
        Fetches Analyst Recommendations and Price Targets.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Target Prices
            targets = {
                "current": info.get('currentPrice', 0),
                "target_mean": info.get('targetMeanPrice', 0),
                "target_high": info.get('targetHighPrice', 0),
                "target_low": info.get('targetLowPrice', 0),
                "recommendation": info.get('recommendationKey', 'none').upper(),
                "num_analysts": info.get('numberOfAnalystOpinions', 0)
            }
            
            # Rec trends (Strong Buy, Buy, Hold, etc.)
            recs = stock.recommendations
            if recs is not None and not recs.empty:
                # Keep latest period only
                recs = recs.iloc[-1:] # Usually contains the summary of 'period' 0m
            
            return targets, recs
            
        except Exception as e:
            print(f"Analyst Data Error: {e}")
            return None, None

    def plot_price_target(self, targets):
        """
        Visualizes Current Price vs Analyst Target Range using a Gauge Chart.
        """
        current = targets.get('current', 0)
        mean_target = targets.get('target_mean', 0)
        
        if mean_target == 0 or current == 0:
            return go.Figure()

        fig = go.Figure(go.Indicator(
            mode = "number+gauge+delta",
            value = current,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Current vs Target (${mean_target})", 'font': {'size': 20, 'color': 'white'}},
            delta = {'reference': mean_target, 'increasing': {'color': "#EF553B"}, 'decreasing': {'color': "#00CC96"}, 'relative': True},
            gauge = {
                'axis': {'range': [targets.get('target_low', current*0.5), targets.get('target_high', current*1.5)], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#4B6CB7"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#333",
                'steps': [
                    {'range': [targets.get('target_low', 0), mean_target], 'color': 'rgba(100, 100, 100, 0.3)'},
                    {'range': [mean_target, targets.get('target_high', 0)], 'color': 'rgba(0, 204, 150, 0.1)'}],
                'threshold': {
                    'line': {'color': "#00CC96", 'width': 4},
                    'thickness': 0.75,
                    'value': mean_target}
            }
        ))
        
        fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Inter"})
        return fig