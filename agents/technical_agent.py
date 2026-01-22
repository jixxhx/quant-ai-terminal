import yfinance as yf
import pandas as pd
import pandas_ta as ta

class TechnicalAnalyst:
    def __init__(self, ticker):
        self.ticker = ticker

    def fetch_data(self, period="1y"):
        try:
            df = yf.download(self.ticker, period=period)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df=None):
        if df is None:
            df = self.fetch_data()
        
        if df.empty:
            return df

        # 1. SMA (Simple Moving Average)
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['SMA_50'] = ta.sma(df['Close'], length=50)
        df['SMA_200'] = ta.sma(df['Close'], length=200)

        # 2. EMA (Exponential Moving Average)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)   # [NEW]
        df['EMA_200'] = ta.ema(df['Close'], length=200) # [NEW]

        # 3. Bollinger Bands
        bbands = ta.bbands(df['Close'], length=20, std=2.0)
        if bbands is not None and not bbands.empty:
            bbu = [c for c in bbands.columns if c.startswith('BBU')][0]
            bbl = [c for c in bbands.columns if c.startswith('BBL')][0]
            bbm = [c for c in bbands.columns if c.startswith('BBM')][0]
            df['BB_Upper'] = bbands[bbu]
            df['BB_Lower'] = bbands[bbl]
            df['BB_Mid']   = bbands[bbm]

        # 4. Parabolic SAR [NEW]
        # (psar returns 'PSARl' and 'PSARs' sometimes, need dynamic check)
        psar = ta.psar(df['High'], df['Low'], df['Close'])
        if psar is not None and not psar.empty:
            # Combine long and short columns into one for plotting
            psar_cols = [c for c in psar.columns if c.startswith('PSAR')]
            df['PSAR'] = psar[psar_cols].fillna(0).sum(axis=1)
            # Fix zeros if overlap (rare)
            df['PSAR'] = df['PSAR'].replace(0, pd.NA)

        # 5. Donchian Channels [NEW]
        donchian = ta.donchian(df['High'], df['Low'], lower_length=20, upper_length=20)
        if donchian is not None and not donchian.empty:
            dcu = [c for c in donchian.columns if c.startswith('DCU')][0]
            dcl = [c for c in donchian.columns if c.startswith('DCL')][0]
            df['DC_Upper'] = donchian[dcu]
            df['DC_Lower'] = donchian[dcl]

        # 6. VWAP (Volume Weighted Average Price) [NEW]
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])

        # 7. RSI
        df['RSI'] = ta.rsi(df['Close'], length=14)

        return df

    def get_summary(self):
        """
        Returns a dictionary summary.
        """
        df = self.calculate_indicators()
        if df.empty:
            return "No Data"

        latest = df.iloc[-1]
        
        sentiment = "NEUTRAL"
        sma_50 = latest.get('SMA_50', 0)
        current_price = latest['Close']

        if sma_50 > 0:
            if current_price > sma_50:
                sentiment = "BULLISH"
            elif current_price < sma_50:
                sentiment = "BEARISH"
            
        return {
            "current_price": current_price,
            "rsi": latest.get('RSI', 50),
            "sma_20": latest.get('SMA_20', 0),
            "sma_50": latest.get('SMA_50', 0),
            "sma_200": latest.get('SMA_200', 0),
            "sentiment": sentiment
        }
