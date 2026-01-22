import numpy as np
import pandas as pd
import plotly.graph_objects as go

class MonteCarloAgent:
    def __init__(self):
        pass

    def run_simulation(self, df, days=30, simulations=1000):
        if df.empty or len(df) < 50:
            return None, None

        returns = df['Close'].pct_change().dropna()
        mu = returns.mean()
        sigma = returns.std()
        
        start_price = df['Close'].iloc[-1]
        
        simulation_df = pd.DataFrame()
        
        for i in range(simulations):
            prices = [start_price]
            for d in range(days):
                drift = mu - 0.5 * sigma**2
                shock = sigma * np.random.normal()
                price = prices[-1] * np.exp(drift + shock)
                prices.append(price)
            
            simulation_df[f'Sim_{i}'] = prices

        final_prices = simulation_df.iloc[-1]
        mean_price = final_prices.mean()
        upside = final_prices.quantile(0.95)
        downside = final_prices.quantile(0.05)
        
        metrics = {
            "Expected Price": f"${mean_price:.2f}",
            "Bull Case (95%)": f"${upside:.2f}",
            "Bear Case (5%)": f"${downside:.2f}",
            "Volatility": f"{sigma*100:.2f}%"
        }

        return simulation_df, metrics

    def plot_simulation(self, sim_df):
        """
        스파게티 차트 그리기 (제목 및 축 글자색 흰색 강제 적용)
        """
        fig = go.Figure()
        
        sample_cols = sim_df.columns[:50] 
        
        for col in sample_cols:
            fig.add_trace(go.Scatter(
                y=sim_df[col],
                mode='lines',
                line=dict(width=1, color='rgba(0, 204, 150, 0.3)'),
                showlegend=False,
                hoverinfo='none'
            ))

        mean_line = sim_df.mean(axis=1)
        fig.add_trace(go.Scatter(
            y=mean_line,
            mode='lines',
            name='Average Path',
            line=dict(width=3, color='#FFFFFF', dash='dash')
        ))

        fig.update_layout(
            # [수정] 제목 흰색 강제
            title=dict(
                text="🔮 1,000 Possible Futures (Next 30 Days)",
                font=dict(color="white")
            ),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            # [수정] 축 제목 및 눈금 흰색 강제
            xaxis=dict(
                title=dict(text="Days into Future", font=dict(color="white")),
                tickfont=dict(color="white"),
                gridcolor='#444'
            ),
            yaxis=dict(
                title=dict(text="Projected Price ($)", font=dict(color="white")),
                tickfont=dict(color="white"),
                gridcolor='#444'
            ),
            font=dict(color="white"),
            showlegend=True,
            legend=dict(font=dict(color="white"))
        )
        
        return fig
