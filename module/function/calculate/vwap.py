"""
前日までの20日VWAP（=Σ(price*vol)/Σvol）。日足なので close を price として近似。

呼び出し方
import module.function.calculate.vwap as vwap_calc

df["vwap"] = _vwap_prev20(close, vol)
"""

import numpy as np
import pandas as pd

def _vwap_prev20(close: pd.Series, vol: pd.Series) -> pd.Series:
    """前日までの20日VWAP（=Σ(price*vol)/Σvol）。日足なので close を price として近似。"""
    pv = (close.shift(1) * vol.shift(1))
    pv_sum = pv.rolling(20, min_periods=20).sum()
    v_sum = vol.shift(1).rolling(20, min_periods=20).sum()
    return pv_sum / v_sum.replace(0, np.nan)