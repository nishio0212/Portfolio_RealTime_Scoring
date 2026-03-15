"""
説明
MACD (Moving Average Convergence Divergence) を計算する関数

呼び出し方
from module.function.calculate.macd import _macd
df["macd"], df["signal"] = _macd(close, 12, 26, 9)

"""

import pandas as pd
from typing import Tuple
from module.function.calculate.ema import _ema

def _macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
    ema_fast = _ema(close, fast)
    ema_slow = _ema(close, slow)
    macd = ema_fast - ema_slow
    sig = _ema(macd, signal)
    return macd, sig