"""
RSI（Relative Strength Index、相対力指数）を計算する関数

呼び出し方
df["rsi"] = _rsi(close, 14)
"""

import pandas as pd

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(100)  # avg_loss == 0（全日上昇）→ RSI=100
    return rsi