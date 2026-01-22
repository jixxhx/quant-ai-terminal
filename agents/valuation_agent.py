import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

class ValuationAgent:
    def __init__(self):
        pass

    def get_fundamentals(self, ticker):
        """
        Fetch key fundamental metrics from Yahoo Finance.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Safe extraction with default values
            metrics = {
                "Market Cap": info.get("marketCap", 0),
                "Trailing P/E": info.get("trailingPE", 0),
                "Forward P/E": info.get("forwardPE", 0),
                "PEG Ratio": info.get("pegRatio", 0),
                "Price/Book": info.get("priceToBook", 0),
                "ROE": info.get("returnOnEquity", 0),
                "Profit Margin": info.get("profitMargins", 0),
                "Target Price (Analyst)": info.get("targetMeanPrice", 0),
                "Current Price": info.get("currentPrice", 0),
                "EPS": info.get("trailingEps", 0),
                "Growth Rate": info.get("revenueGrowth", 0.10) # Default 10%
            }
            return metrics
        except Exception as e:
            print(f"Error fetching fundamentals: {e}")
            return None

    def calculate_fair_value(self, metrics):
        """
        Calculate Intrinsic Value using a simplified Growth Model.
        """
        if not metrics:
            return 0

        eps = metrics['EPS']
        growth = metrics['Growth Rate'] * 100 
        
        # Cap growth rate at 20% for conservative estimate
        adjusted_growth = min(growth, 20)
        
        # Graham's Formula
        intrinsic_value = eps * (8.5 + 2 * adjusted_growth)
        
        return intrinsic_value

    def plot_valuation_gauge(self, current_price, fair_value):
        """
        Visualize Undervalued vs Overvalued status (Fixed Clipping Issue)
        """
        if fair_value <= 0:
            return go.Figure()

        max_val = max(current_price, fair_value) * 1.5
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current_price,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {
                'text': "⚖️ Fair Value Analysis", 
                'font': {'size': 20, 'color': "white"}
            },
            delta = {'reference': fair_value, 'increasing': {'color': "#EF553B"}, 'decreasing': {'color': "#00CC96"}},
            gauge = {
                'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "white", 'tickfont': {'color': 'white'}},
                'bar': {'color': "white", 'thickness': 0.3},
                'bgcolor': "#161920",
                'borderwidth': 2,
                'bordercolor': "#333",
                'steps': [
                    {'range': [0, fair_value * 0.9], 'color': "rgba(0, 204, 150, 0.3)"},
                    {'range': [fair_value * 0.9, fair_value * 1.1], 'color': "rgba(254, 203, 82, 0.3)"},
                    {'range': [fair_value * 1.1, max_val], 'color': "rgba(239, 85, 59, 0.3)"}
                ],
                'threshold': {
                    'line': {'color': "#FECB52", 'width': 4},
                    'thickness': 0.8,
                    'value': fair_value
                }
            }
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "white", 'family': "Arial"},
            # [FIX] Adjusted Position (y=-0.15) and Increased Bottom Margin (b=120)
            annotations=[dict(
                x=0.5, y=-0.15, 
                xref='paper', yref='paper',
                text=f"🎯 Target Intrinsic Value: ${fair_value:.2f}",
                showarrow=False,
                font=dict(size=18, color="#FECB52", weight="bold"),
                xanchor='center',
                yanchor='top'
            )],
            margin=dict(l=30, r=30, t=50, b=120) # Increased bottom margin to prevent clipping
        )
        
        return fig
