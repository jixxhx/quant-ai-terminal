import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class PortfolioAgent:
    def __init__(self):
        pass

    def get_portfolio_data(self, tickers, period="1y"):
        """
        Download historical data for multiple tickers.
        """
        try:
            data = yf.download(tickers, period=period)['Close']
            return data
        except Exception as e:
            print(f"Error fetching portfolio data: {e}")
            return pd.DataFrame()

    def optimize_portfolio(self, df, num_portfolios=2000):
        """
        Run Monte Carlo Simulation to find the Efficient Frontier.
        """
        if df.empty:
            return None, None

        # Calculate daily returns
        returns = df.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        num_assets = len(df.columns)
        risk_free_rate = 0.04 

        # Simulation
        results = np.zeros((3, num_portfolios))
        weights_record = []

        for i in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            weights_record.append(weights)

            portfolio_return = np.sum(mean_returns * weights) * 252
            portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
            
            results[0,i] = portfolio_return
            results[1,i] = portfolio_std_dev
            results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std_dev

        # Optimal Portfolios
        max_sharpe_idx = np.argmax(results[2])
        best_portfolio = {
            "Return": results[0, max_sharpe_idx],
            "Volatility": results[1, max_sharpe_idx],
            "Sharpe": results[2, max_sharpe_idx],
            "Weights": dict(zip(df.columns, weights_record[max_sharpe_idx]))
        }
        
        sim_data = pd.DataFrame(results.T, columns=['Return', 'Volatility', 'Sharpe'])

        return best_portfolio, sim_data

    def plot_efficient_frontier(self, sim_data, best_port):
        """
        Visualize Efficient Frontier (Fixed ColorBar Error)
        """
        if sim_data is None:
            return go.Figure()

        fig = go.Figure()

        # 1. All Simulated Portfolios
        fig.add_trace(go.Scatter(
            x=sim_data['Volatility'], 
            y=sim_data['Return'],
            mode='markers',
            marker=dict(
                size=5,
                color=sim_data['Sharpe'],
                colorscale='Viridis',
                showscale=True,
                # [FIX] ColorBar title fix (removed titlefont, used dict structure)
                colorbar=dict(
                    title=dict(text="Sharpe Ratio", font=dict(color="white")),
                    tickfont=dict(color="white")
                )
            ),
            name='Portfolios',
            text=sim_data['Sharpe'],
            hovertemplate="Risk: %{x:.2%}<br>Return: %{y:.2%}<br>Sharpe: %{marker.color:.2f}"
        ))

        # 2. Optimal Portfolio Marker
        fig.add_trace(go.Scatter(
            x=[best_port['Volatility']], 
            y=[best_port['Return']],
            mode='markers',
            marker=dict(symbol='star', size=18, color='#EF553B', line=dict(width=2, color='white')),
            name='Optimal Portfolio'
        ))

        fig.update_layout(
            title=dict(text="💼 Efficient Frontier (Portfolio Optimization)", font=dict(color="white")),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            xaxis=dict(title=dict(text="Annualized Volatility (Risk)", font=dict(color="white")), tickfont=dict(color="white"), gridcolor='#444'),
            yaxis=dict(title=dict(text="Annualized Return", font=dict(color="white")), tickfont=dict(color="white"), gridcolor='#444'),
            font=dict(color="white"),
            legend=dict(font=dict(color="white"))
        )
        return fig