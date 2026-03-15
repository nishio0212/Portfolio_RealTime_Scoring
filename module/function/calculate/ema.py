"""
EMA（指数移動平均）を計算する関数

呼び出し方
from module.function.calculate.ema import _ema
df["ema9"] = ema(close, 9)
"""

import pandas as pd

def _ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()