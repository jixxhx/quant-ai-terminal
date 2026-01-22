import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
# Removed unused seaborn import

class CorrelationAgent:
    def __init__(self):
        # Asset classes for comparison
        self.benchmarks = {
            'SPY': 'S&P 500',
            'QQQ': 'Nasdaq 100',
            'BTC-USD': 'Bitcoin',
            'GC=F': 'Gold',
            'CL=F': 'Crude Oil'
        }

    def get_correlations(self, ticker):
        """
        Calculate asset correlation matrix.
        """
        # 1. Download data (Last 1 year)
        tickers = [ticker] + list(self.benchmarks.keys())
        try:
            data = yf.download(tickers, period="1y", interval="1d")['Close']
            
            # 2. Data cleaning
            data = data.dropna()
            
            # 3. Rename columns
            data.rename(columns=self.benchmarks, inplace=True)
            
            # 4. Calculate correlation
            corr_matrix = data.corr()
            return corr_matrix
            
        except Exception as e:
            print(f"Error fetching correlation data: {e}")
            return pd.DataFrame()

    def plot_heatmap(self, corr_df):
        """
        Draw Correlation Heatmap (Dark Mode Optimized)
        """
        if corr_df.empty:
            return go.Figure()

        # [수정] 다크 모드 전용 컬러 스케일 정의
        # -1 (빨강) -> 0 (어두운 배경색) -> 1 (파랑)
        dark_colorscale = [
            [0.0, '#EF553B'], # Negative (Red)
            [0.5, '#1C1F26'], # Neutral (Dark Grey - Background color)
            [1.0, '#636EFA']  # Positive (Blue)
        ]

        fig = go.Figure(data=go.Heatmap(
            z=corr_df.values,
            x=corr_df.columns,
            y=corr_df.index,
            colorscale=dark_colorscale, # [적용] 커스텀 다크 테마
            zmin=-1, zmax=1,
            text=corr_df.values.round(2),
            texttemplate="%{text}",
            textfont={"color": "white"} # 이제 배경이 어두우니 흰색 글씨가 잘 보입니다!
        ))

        fig.update_layout(
            title=dict(
                text="🔗 Asset Correlation Matrix (1 Year)",
                font=dict(color="white")
            ),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            xaxis=dict(tickfont=dict(color="white"), side="bottom"),
            yaxis=dict(tickfont=dict(color="white"), autorange="reversed"),
            font=dict(color="white")
        )
        
        return fig
