import plotly.graph_objects as go
import pandas as pd

class MacroAgent:
    def __init__(self):
        # Keywords for Hawkish (Rate Hike) vs Dovish (Rate Cut)
        self.hawkish_terms = ["inflation", "tightening", "raise", "hike", "strong", "resilient"]
        self.dovish_terms = ["recession", "slowdown", "cut", "lower", "weak", "unemployment"]

    def analyze_minutes(self):
        """
        Analyze FOMC minutes text to calculate sentiment score.
        """
        # Sample text representing recent Fed sentiment (Mock data)
        sample_text = """
        The Committee remains highly attentive to inflation risks. 
        Recent indicators suggest that economic activity has been expanding at a solid pace. 
        Job gains have remained strong, and the unemployment rate has remained low. 
        Inflation has eased over the past year but remains elevated.
        The Committee seeks to achieve maximum employment and inflation at the rate of 2 percent over the longer run.
        In support of these goals, the Committee decided to maintain the target range for the federal funds rate at 5-1/4 to 5-1/2 percent.
        """
        
        # Text Analysis
        hawkish_score = sum(sample_text.count(w) for w in self.hawkish_terms)
        dovish_score = sum(sample_text.count(w) for w in self.dovish_terms)
        
        total = hawkish_score + dovish_score
        sentiment = (hawkish_score - dovish_score) / total if total > 0 else 0
        
        return sentiment, sample_text

    def plot_sentiment_gauge(self, sentiment):
        """
        Plot Hawkish vs Dovish Gauge Chart (White text enforced)
        """
        # Normalize score (-1 to 1 mapped to 0 to 100)
        score = (sentiment + 1) * 50 
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "🦅 Fed Hawkishness Score", 'font': {'size': 24, 'color': "white"}},
            delta = {'reference': 50, 'increasing': {'color': "#EF553B"}, 'decreasing': {'color': "#00CC96"}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white", 'tickfont': {'color': 'white'}},
                'bar': {'color': "#2E3440"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#333",
                'steps': [
                    {'range': [0, 40], 'color': "#00CC96"}, # Dovish (Green)
                    {'range': [40, 60], 'color': "#FECB52"}, # Neutral (Yellow)
                    {'range': [60, 100], 'color': "#EF553B"}], # Hawkish (Red)
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': score}}))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "white", 'family': "Arial"}
        )
        
        return fig

    def plot_dot_plot(self):
        """
        Plot Fed Dot Plot Projection (Interest Rates)
        """
        years = ['2024', '2025', '2026', 'Longer run']
        rates = [4.6, 3.9, 3.1, 2.5] # Median projection
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years, y=rates,
            mode='markers+lines',
            marker=dict(size=15, color='#FFA15A'),
            line=dict(width=3, color='#FFA15A', dash='dot'),
            name='Fed Median Projection'
        ))
        
        fig.update_layout(
            title=dict(text="📈 Fed Interest Rate Projections (Dot Plot)", font=dict(color="white")),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title=dict(text="Year", font=dict(color="white")), tickfont=dict(color="white"), gridcolor='#444'),
            yaxis=dict(title=dict(text="Interest Rate (%)", font=dict(color="white")), tickfont=dict(color="white"), gridcolor='#444'),
            font=dict(color="white")
        )
        return fig