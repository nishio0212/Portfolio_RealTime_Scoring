"""
output/codes_data.csv から code,name を読み込み、DataFrameで返す。

呼び出し方
--------------------
from module.function.load_codes_data_df import load_code_data
df = load_code_data(csv_path)
--------------------
"""

import pandas as pd
from pathlib import Path

def load_code_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype=str, encoding="utf-8")
    if "code" not in df.columns or "name" not in df.columns:
        raise ValueError("output/codes_data.csv は 'code','name' 列が必要です。")

    df["code"] = df["code"].str.strip()
    df["name"] = df["name"].str.strip()
    df = df.dropna(subset=["code", "name"])
    df = df[(df["code"] != "") & (df["name"] != "")]
    df = df.drop_duplicates(subset="code", keep="first")
    return df
