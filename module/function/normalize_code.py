"""
日本株の銘柄コードを正規化する関数群

呼び出し方
----------------
from module.function.normalize_code import normalize_code
code = normalize_code(input_value)
----------------
"""
import re

# ----------------------------------------------------------
# 日本株 銘柄コード正規化 関数
# ----------------------------------------------------------
def normalize_code(x) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    s = re.sub(r"\.0$", "", s)  # 1301.0 対策
    s = s.replace(" ", "").upper()

    # 4桁数字のみ → そのまま(必要なら zfill(4))
    if re.fullmatch(r"\d{1,4}", s):
        return s.zfill(4)

    # 英字付き（例: 285A / 130A など）→ 英字を残す
    if re.fullmatch(r"\d{1,4}[A-Z]", s):
        return s  # ゼロ埋めしない（0285A みたいな表記はYahooでまず使わない）

    return ""
