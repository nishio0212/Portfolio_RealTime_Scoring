"""
python nikkei225_from_saved_html.py --html "構成銘柄一覧 － 日経平均プロフィル.html"
python nikkei225_from_saved_html.py --html "構成銘柄一覧 － 日経平均プロフィル.html" --out "nikkei225.csv"

"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


def extract_code_name_from_html(html_text: str) -> pd.DataFrame:
    """
    日経平均プロフィル（構成銘柄一覧）をブラウザで保存したHTMLから、
    「コード」「銘柄名」を抽出してDataFrameで返す。
    """
    soup = BeautifulSoup(html_text, "lxml")

    rows: list[tuple[str, str]] = []

    # テーブル内の行を走査（保存HTMLでも安定しやすい）
    for tr in soup.select("table tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        code = tds[0].get_text(strip=True)
        name = tds[1].get_text(strip=True)

        # コードは4桁数字が基本
        if re.fullmatch(r"\d{4}", code):
            rows.append((code, name))

    df = pd.DataFrame(rows, columns=["code", "name"]).drop_duplicates()

    # コード順に整列
    if not df.empty:
        df = df.sort_values("code").reset_index(drop=True)

    return df


def main():
    parser = argparse.ArgumentParser(
        description="保存した日経225構成銘柄HTMLから code/name を抽出してCSV出力します。"
    )
    parser.add_argument(
        "--html",
        required=True,
        help="ブラウザで保存したHTMLファイルのパス（例: '構成銘柄一覧 － 日経平均プロフィル.html'）",
    )
    parser.add_argument(
        "--out",
        default="nikkei225_code_name.csv",
        help="出力CSVパス（デフォルト: nikkei225_code_name.csv）",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSVの文字コード（Excel想定ならutf-8-sig推奨）",
    )
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        raise FileNotFoundError(f"HTMLが見つかりません: {html_path}")

    # 保存HTMLの文字コードは環境でブレるので errors=ignore で堅く読む
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")

    df = extract_code_name_from_html(html_text)

    if df.empty:
        raise RuntimeError(
            "抽出結果が0件でした。保存したHTMLが別ページ/構造変更の可能性があります。"
        )

    out_path = Path(args.out)
    df.to_csv(out_path, index=False, encoding=args.encoding)

    print(f"[OK] rows={len(df)} -> {out_path.resolve()}")


if __name__ == "__main__":
    main()
