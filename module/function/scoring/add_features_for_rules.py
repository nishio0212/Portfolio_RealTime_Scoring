"""
Top10条件で使う派生フラグを作る（未来情報なし）
vol_avg20 は「前日までの平均」= rolling(20).mean().shift(1)

呼び出し方
from module.function.scoring.memo import add_features_for_rules

例:
d = add_features_for_rules(df)
"""

import pandas as pd

def add_features_for_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Top10条件で使う派生フラグを作る（未来情報なし）
    vol_avg20 は「前日までの平均」= rolling(20).mean().shift(1)
    """
    d = df.copy()

    # 列名ゆらぎ吸収（vol/volume）
    if "volume" not in d.columns and "vol" in d.columns:
        d["volume"] = d["vol"]

    # --- 前日までの出来高平均（重要） ---
    d["vol_avg20"] = d["volume"].rolling(20, min_periods=20).mean().shift(1)

    # --- ローソク関連 ---
    d["oc_neg"] = d["close"] <= d["open"]  # 陰線
    d["range_ge3"] = ((d["high"] - d["low"]) / d["close"]) >= 0.03  # 値幅率>=3%

    # --- EMA差の加速（acc_norm） ---
    diff = d["ema9"] - d["ema20"]
    acc = diff - diff.shift(1)
    d["acc_norm"] = (acc / d["close"]) * 100  # %表現
    d["acc_gt0"] = d["acc_norm"] > 0
    d["acc_gt0p03"] = d["acc_norm"] > 0.03
    d["acc_gt0p06"] = d["acc_norm"] > 0.06

    # --- 出来高系 ---
    d["vol_ge_avg20"] = d["volume"] >= d["vol_avg20"]
    d["vol_ge_1p3"] = d["volume"] >= (1.3 * d["vol_avg20"])

    # --- RSI ---
    if "rsi" in d.columns:
        d["rsi_45_55"] = (d["rsi"] >= 45) & (d["rsi"] <= 55)

    # --- トレンド系（存在する場合だけ使う） ---
    if "ema200" in d.columns:
        d["close_gt_ema200"] = d["close"] > d["ema200"]
        d["close_le_ema200"] = d["close"] <= d["ema200"]
    if "ema20" in d.columns:
        d["ema20_up"] = d["ema20"] > d["ema20"].shift(1)

    # --- MACD / signal（存在する場合だけ） ---
    if "macd" in d.columns and "signal" in d.columns:
        macd_diff = d["macd"] - d["signal"]
        d["macd_gt_signal"] = macd_diff > 0
        cross = (macd_diff > 0) & (macd_diff.shift(1) <= 0)
        d["macd_cross_within5d"] = cross.rolling(5, min_periods=1).max().astype(bool)

    # --- EMAクロス（存在する場合だけ） ---
    ema_diff = d["ema9"] - d["ema20"]
    ema_cross = (ema_diff > 0) & (ema_diff.shift(1) <= 0)
    d["ema_cross_within5d"] = ema_cross.rolling(5, min_periods=1).max().astype(bool)

    # --- VWAP（存在する場合だけ） ---
    if "vwap" in d.columns:
        d["close_gt_vwap"] = d["close"] > d["vwap"]
    
    return d
