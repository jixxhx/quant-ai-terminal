import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
# [FIX] Removed sklearn dependency to avoid installation errors

class PeerAgent:
    def __init__(self):
        # Define Competitor Groups (Simple Database)
        self.peers_db = {
            "NVDA": ["AMD", "INTC", "TSM", "AVGO", "QCOM"],
            "AAPL": ["MSFT", "GOOGL", "AMZN", "META", "TSLA"],
            "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL", "IBM"],
            "GOOGL": ["MSFT", "META", "AMZN", "AAPL", "SNAP"],
            "AMZN": ["WMT", "BABA", "EBAY", "TGT", "COST"],
            "TSLA": ["F", "GM", "TM", "RIVN", "LCID"],
            "AMD": ["NVDA", "INTC", "TSM", "QCOM", "MU"],
            "NFLX": ["DIS", "WBD", "CMCSA", "PARA"],
            "JPM": ["BAC", "WFC", "C", "GS", "MS"],
            "KO": ["PEP", "MNST", "KDP", "SBUX"],
            "BTC-USD": ["ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"],
            "SPY": ["QQQ", "IWM", "DIA", "TLT"]
        }

    def get_peers(self, ticker):
        """Returns a list of peers. Defaults to Big Tech if unknown."""
        return self.peers_db.get(ticker, ["AAPL", "MSFT", "GOOGL", "AMZN"])

    def fetch_peer_data(self, main_ticker):
        """
        Fetches comparison data for the target ticker and its peers.
        """
        tickers = [main_ticker] + self.get_peers(main_ticker)
        data = []

        for t in tickers:
            try:
                stock = yf.Ticker(t)
                info = stock.info
                
                # Extract Key Metrics (Safe extraction)
                metrics = {
                    "Ticker": t,
                    "Price": info.get('currentPrice', 0),
                    "Market Cap (B)": info.get('marketCap', 0) / 1e9,
                    "P/E Ratio": info.get('trailingPE', 0),
                    "Forward P/E": info.get('forwardPE', 0),
                    "PEG Ratio": info.get('pegRatio', 0),
                    "ROE (%)": info.get('returnOnEquity', 0) * 100,
                    "Profit Margin (%)": info.get('profitMargins', 0) * 100,
                    "Rev Growth (%)": info.get('revenueGrowth', 0) * 100
                }
                data.append(metrics)
            except:
                continue
        
        return pd.DataFrame(data)

    def fetch_price_history(self, main_ticker):
        """
        Fetches 6-month normalized price history for relative performance chart.
        """
        tickers = [main_ticker] + self.get_peers(main_ticker)
        try:
            # Fetch data
            df = yf.download(tickers, period="6mo")['Close']
            
            # Formatting check for MultiIndex columns (common in new yfinance)
            if isinstance(df.columns, pd.MultiIndex):
                # Try to flatten if possible, or just proceed if simple
                pass 

            # Fill missing
            df = df.fillna(method='ffill').fillna(method='bfill')
            
            # Normalize to percentage change (Start at 0%)
            # Avoid division by zero
            if not df.empty:
                normalized_df = (df / df.iloc[0] - 1) * 100
                return normalized_df
            return pd.DataFrame()
        except:
            return pd.DataFrame()

    def plot_radar_chart(self, df, main_ticker):
        """
        Creates a Spider (Radar) Chart comparing financial health.
        Uses manual Min-Max normalization to remove sklearn dependency.
        """
        if df.empty: return go.Figure()

        # Select comparative metrics
        radar_cols = ["P/E Ratio", "ROE (%)", "Profit Margin (%)", "Rev Growth (%)", "PEG Ratio"]
        
        # Prepare Data
        plot_df = df.set_index('Ticker')[radar_cols].fillna(0)
        
        # [FIX] Manual Normalization (0 to 1 scale) without sklearn
        # Formula: (x - min) / (max - min)
        scaled_df = (plot_df - plot_df.min()) / (plot_df.max() - plot_df.min())
        
        # Handle division by zero (if max == min, set to 0.5)
        scaled_df = scaled_df.fillna(0.5)

        fig = go.Figure()

        # Add Peers (Faint Lines)
        for peer in scaled_df.index:
            if peer == main_ticker: continue
            fig.add_trace(go.Scatterpolar(
                r=scaled_df.loc[peer],
                theta=radar_cols,
                fill='toself',
                name=peer,
                line=dict(color='rgba(100, 100, 100, 0.5)', width=1),
                fillcolor='rgba(100, 100, 100, 0.1)'
            ))

        # Add Main Ticker (Strong Highlight)
        if main_ticker in scaled_df.index:
            fig.add_trace(go.Scatterpolar(
                r=scaled_df.loc[main_ticker],
                theta=radar_cols,
                fill='toself',
                name=main_ticker,
                line=dict(color='#00CC96', width=4),
                fillcolor='rgba(0, 204, 150, 0.3)'
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, linecolor='#555'),
                bgcolor='rgba(0,0,0,0)'
            ),
            title=dict(text=f"🕸️ Financial Health Radar: {main_ticker} vs Peers", font=dict(color="white")),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            showlegend=True
        )
        return fig