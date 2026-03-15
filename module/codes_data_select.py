# 02_heatmap_codes_data_select.py
# 調整予定
from __future__ import annotations
from pathlib import Path
import pandas as pd
from module.function.normalize_code import normalize_code as _normalize_code


def build_codes_data(
    codes_csv: Path,
    data_j_xls: Path,
    out_csv: Path,
    *,
    encoding_out: str = "utf-8-sig",
) -> Path:

    # --- input codes ---
    df_codes = pd.read_csv(codes_csv, dtype={"codes": "string"})
    if "codes" not in df_codes.columns:
        raise ValueError("'codes' 列が input/codes.csv に存在しません")

    code_list = [_normalize_code(x) for x in df_codes["codes"]]
    code_set = {c for c in code_list if c}

    if not code_set:
        raise ValueError("codes が空です")

    # --- JPX data ---
    # コード列は英字混在があるため string で読む
    df_jpx = pd.read_excel(data_j_xls, dtype={"コード": "string"})

    required_cols = [
        "コード",
        "銘柄名",
        "市場・商品区分",
        "33業種コード",
        "33業種区分",
        "17業種コード",
        "17業種区分",
    ]
    missing = [c for c in required_cols if c not in df_jpx.columns]
    if missing:
        raise ValueError(f"data_j.xls に必要列が不足しています: {missing}")

    df_jpx["_code_norm"] = df_jpx["コード"].map(_normalize_code)

    # --- filter ---
    df_sel = df_jpx[df_jpx["_code_norm"].isin(code_set)].copy()

    # --- rename & select ---
    df_out = (
        df_sel.rename(
            columns={
                "_code_norm": "code",
                "銘柄名": "name",
                "市場・商品区分": "market",
                "33業種コード": "33 Industry Code",
                "33業種区分": "33 Industry Classification",
                "17業種コード": "17 Industry Code",
                "17業種区分": "17 Industry Classification",
            }
        )[
            [
                "code",
                "name",
                "market",
                "33 Industry Code",
                "33 Industry Classification",
                "17 Industry Code",
                "17 Industry Classification",
            ]
        ]
    )

    # input の code 順を維持
    order = {c: i for i, c in enumerate(code_list) if c}
    df_out["_order"] = df_out["code"].map(order)
    df_out = df_out.sort_values("_order").drop(columns="_order")

    # --- output ---
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_csv, index=False, encoding=encoding_out)

    # 見つからなかったコードを警告
    missing_codes = sorted(code_set - set(df_out["code"]))
    if missing_codes:
        print(
            "[WARN] data_j.xls に存在しなかった code:",
            missing_codes[:20],
            "..." if len(missing_codes) > 20 else "",
        )

    return out_csv
