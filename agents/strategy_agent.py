import pandas as pd
import numpy as np
import plotly.graph_objects as go

class StrategyAgent:
    def __init__(self):
        pass

    def run_backtest(self, df):
        """
        RSI Mean Reversion Strategy Backtest
        """
        # 1. Basic Data Check
        if df.empty or len(df) < 50:
            return None, "Not enough data for strategy simulation."

        data = df.copy()
        
        # [FIX] Check for 'RSI' instead of 'RSI_14'
        # The TechnicalAnalyst now saves it simply as 'RSI'
        rsi_col = 'RSI'
        if rsi_col not in data.columns:
            return None, "RSI indicator missing."

        # 2. Strategy Logic
        data['Signal'] = 0
        # Buy Signal (Oversold)
        data.loc[data[rsi_col] < 30, 'Signal'] = 1
        # Sell Signal (Overbought)
        data.loc[data[rsi_col] > 70, 'Signal'] = -1

        # 3. Calculate Returns
        data['Daily_Return'] = data['Close'].pct_change()
        data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']
        
        data['Cumulative_Market'] = (1 + data['Daily_Return']).cumprod()
        data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod()

        # 4. Metrics
        total_return = (data['Cumulative_Strategy'].iloc[-1] - 1) * 100
        market_return = (data['Cumulative_Market'].iloc[-1] - 1) * 100
        
        trades = data[data['Strategy_Return'] != 0]
        win_rate = 0
        if len(trades) > 0:
            win_rate = len(trades[trades['Strategy_Return'] > 0]) / len(trades) * 100

        metrics = {
            "Total Return": f"{total_return:.2f}%",
            "Market Return": f"{market_return:.2f}%",
            "Win Rate": f"{win_rate:.1f}%",
            "Alpha": f"{total_return - market_return:.2f}%"
        }

        return data, metrics

    def plot_performance(self, data):
        """
        Plot Strategy vs Market Performance (White Text Enforced)
        """
        if data is None:
            return go.Figure()

        fig = go.Figure()

        # AI Strategy Line
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Cumulative_Strategy'],
            mode='lines', name='AI Strategy',
            line=dict(color='#00CC96', width=2)
        ))

        # Market Benchmark Line
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Cumulative_Market'],
            mode='lines', name='Buy & Hold',
            line=dict(color='#636EFA', width=2, dash='dot')
        ))

        fig.update_layout(
            title=dict(
                text="💰 Strategy Performance vs Market",
                font=dict(color="white")
            ),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500,
            xaxis=dict(
                title=dict(text="Date", font=dict(color="white")),
                tickfont=dict(color="white"),
                gridcolor='#444'
            ),
            yaxis=dict(
                title=dict(text="Growth Factor (1.0 = Start)", font=dict(color="white")),
                tickfont=dict(color="white"),
                gridcolor='#444'
            ),
            hovermode="x unified",
            legend=dict(font=dict(color="white")),
            font=dict(color="white")
        )
        return fig