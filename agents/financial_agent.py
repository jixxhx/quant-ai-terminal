import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

class FinancialAgent:
    def __init__(self):
        pass

    def get_financials(self, ticker):
        """
        Fetches Income Statement, Balance Sheet, and Cash Flow.
        Returns cleaned DataFrames.
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Fetch Data
            income = stock.financials
            balance = stock.balance_sheet
            cashflow = stock.cashflow
            
            # Helper to clean data (Reverse columns to be chronological: Old -> New)
            def clean_df(df):
                if df.empty: return pd.DataFrame()
                df = df.iloc[:, :4] # Keep last 4 years
                df.columns = [c.strftime('%Y') for c in df.columns] # Format years
                return df[df.columns[::-1]] # Reverse to Ascending Order

            income_df = clean_df(income)
            balance_df = clean_df(balance)
            cashflow_df = clean_df(cashflow)
            
            return income_df, balance_df, cashflow_df
            
        except Exception as e:
            print(f"Error fetching financials: {e}")
            return None, None, None

    def plot_revenue_vs_income(self, income_df):
        """
        Visualizes Revenue vs Net Income Trend (Dual Axis Chart).
        Fixed for latest Plotly version (titlefont deprecation).
        """
        if income_df is None or income_df.empty:
            return go.Figure()

        years = income_df.columns
        # Try finding exact row names (yfinance keys vary)
        try:
            revenue = income_df.loc['Total Revenue']
        except:
            revenue = income_df.iloc[0] # Fallback
            
        try:
            net_income = income_df.loc['Net Income']
        except:
            # Fallback search
            found = [idx for idx in income_df.index if 'Net Income' in str(idx)]
            net_income = income_df.loc[found[0]] if found else income_df.iloc[-1]

        fig = go.Figure()

        # Bar: Revenue
        fig.add_trace(go.Bar(
            x=years, y=revenue,
            name='Total Revenue',
            marker_color='#4B6CB7',
            opacity=0.8
        ))

        # Line: Net Income
        fig.add_trace(go.Scatter(
            x=years, y=net_income,
            name='Net Income',
            yaxis='y2',
            line=dict(color='#00CC96', width=4, shape='spline'),
            mode='lines+markers'
        ))

        fig.update_layout(
            title=dict(text="📊 Revenue vs. Net Income Growth (4 Years)", font=dict(color="white")),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='white')),
            # [FIX] Updated Y-Axis Title Syntax
            yaxis=dict(
                title=dict(text="Revenue", font=dict(color="#4B6CB7")), # New Syntax
                tickfont=dict(color="#4B6CB7"),
                gridcolor='#333'
            ),
            # [FIX] Updated Y-Axis 2 Title Syntax
            yaxis2=dict(
                title=dict(text="Net Income", font=dict(color="#00CC96")), # New Syntax
                tickfont=dict(color="#00CC96"),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            legend=dict(x=0, y=1.1, orientation='h', font=dict(color='white')),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
