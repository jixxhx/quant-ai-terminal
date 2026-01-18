import numpy as np
import pandas as pd
import yfinance as yf


class WhatIfAgent:
    def __init__(self):
        self.factor_tickers = {
            "market": "SPY",
            "rates": "^TNX",       # 10Y yield index
            "oil": "CL=F",         # Crude oil
            "dxy": "DX-Y.NYB"      # US Dollar Index
        }

    def _download(self, ticker, period="1y"):
        data = yf.download(ticker, period=period)
        if data is None or data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data

    def _prepare_series(self, ticker, period="1y"):
        df = self._download(ticker, period)
        if df.empty or "Close" not in df.columns:
            return pd.Series(dtype=float)
        return df["Close"].astype(float)

    def build_regression(self, ticker, period="1y"):
        stock = self._prepare_series(ticker, period)
        if stock.empty:
            return None

        market = self._prepare_series(self.factor_tickers["market"], period)
        rates = self._prepare_series(self.factor_tickers["rates"], period)
        oil = self._prepare_series(self.factor_tickers["oil"], period)
        dxy = self._prepare_series(self.factor_tickers["dxy"], period)

        data = pd.concat({
            "stock": stock,
            "market": market,
            "rates": rates,
            "oil": oil,
            "dxy": dxy
        }, axis=1).dropna()

        if data.empty or len(data) < 60:
            return None

        # Returns for equity/commodity/currency
        y = data["stock"].pct_change().dropna()
        X_market = data["market"].pct_change().reindex(y.index)
        X_oil = data["oil"].pct_change().reindex(y.index)
        X_dxy = data["dxy"].pct_change().reindex(y.index)

        # Rate changes in percentage points (TNX index is in %)
        X_rates = data["rates"].diff().reindex(y.index)

        X = pd.concat([X_market, X_rates, X_oil, X_dxy], axis=1)
        X.columns = ["market", "rates", "oil", "dxy"]
        X = X.dropna()
        y = y.reindex(X.index)

        if X.empty or y.empty:
            return None

        X_mat = np.column_stack([np.ones(len(X)), X.values])
        beta = np.linalg.lstsq(X_mat, y.values, rcond=None)[0]
        intercept = beta[0]
        coeffs = dict(zip(X.columns, beta[1:]))

        y_hat = X_mat @ beta
        ss_res = np.sum((y.values - y_hat) ** 2)
        ss_tot = np.sum((y.values - np.mean(y.values)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0

        return {
            "intercept": intercept,
            "coeffs": coeffs,
            "r2": r2,
            "sample_size": len(X)
        }

    def predict_shock(self, model, shocks):
        if model is None:
            return None
        pred = model["intercept"]
        pred += model["coeffs"]["market"] * shocks.get("market", 0.0)
        pred += model["coeffs"]["rates"] * shocks.get("rates", 0.0)
        pred += model["coeffs"]["oil"] * shocks.get("oil", 0.0)
        pred += model["coeffs"]["dxy"] * shocks.get("dxy", 0.0)
        return pred
