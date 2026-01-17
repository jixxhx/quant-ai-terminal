import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import numpy as np

class InsiderAgent:
    def __init__(self):
        pass

    def get_insider_trades(self, ticker):
        """
        내부자 거래 내역 가져오기 (데이터 없으면 데모 모드 작동)
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.insider_transactions
            
            if df is None or df.empty:
                return self._get_mock_data(ticker)
            
            df = df.reset_index(drop=True)
            if 'Start Date' in df.columns:
                df = df.sort_values('Start Date', ascending=False)
            
            return df
        except:
            return self._get_mock_data(ticker)

    def _get_mock_data(self, ticker):
        """
        실제 데이터가 없을 때 보여줄 예시 데이터 (Demo Mode)
        """
        dates = pd.date_range(end=pd.Timestamp.now(), periods=10).strftime('%Y-%m-%d')
        data = {
            "Insider": ["Jensen Huang (CEO)", "Colette Kress (CFO)", "Director A", "Director B", "Jensen Huang (CEO)"] * 2,
            "Position": ["Chief Executive Officer", "Chief Financial Officer", "Director", "Director", "CEO"] * 2,
            "Text": ["Sale at $180", "Option Exercise", "Purchase at $175", "Sale at $190", "Purchase at $160"] * 2,
            "Start Date": dates,
            "Shares": [10000, 5000, 2000, -5000, 15000, -3000, 4000, -10000, 20000, -1000],
            "Value": [1800000, 800000, 350000, 950000, 2400000, 500000, 700000, 1900000, 3200000, 180000]
        }
        return pd.DataFrame(data)

    def plot_insider_sentiment(self, df):
        """
        매수(Buy) vs 매도(Sell) 시각화 (에러 수정 완료)
        """
        if df.empty:
            return go.Figure()

        df['Type'] = df['Shares'].apply(lambda x: 'Buy' if x > 0 else 'Sell')
        df['Color'] = df['Type'].apply(lambda x: '#00CC96' if x == 'Buy' else '#EF553B')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['Start Date'],
            y=df['Shares'],
            marker_color=df['Color'],
            text=df['Insider'],
            hoverinfo='text+y+x',
            name='Insider Trades'
        ))

        fig.update_layout(
            title=dict(
                text="🕵️ Insider Buy/Sell Volume",
                font=dict(color="white")
            ),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            # yaxis 제목 설정
            yaxis=dict(
                title=dict(text="Shares Traded (+Buy / -Sell)", font=dict(color="white")),
                tickfont=dict(color="white"),
                gridcolor='#444'
            ),
            # xaxis 설정 (titlefont 삭제하고 tickfont만 유지)
            xaxis=dict(
                tickfont=dict(color="white"),
                gridcolor='#444'
            ),
            # 전체 기본 폰트 흰색 설정
            font=dict(color="white"),
            showlegend=False
        )
        return fig