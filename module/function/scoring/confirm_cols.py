"""
必要なカラムがDataFrameに存在するか確認するユーティリティ関数

呼び出し方
from module.function.scoring.confirm_cols import _confirm_cols

例：_confirm_cols(d, ["acc_gt0", "oc_neg", "range_ge3"], "rank1")
"""

import pandas as pd

def _confirm_cols(df: pd.DataFrame, cols: list[str], rule_name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"[{rule_name}] 必要なカラムが不足しています: {missing}")