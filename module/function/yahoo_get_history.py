"""
yfinance を使って株価データを取得する関数

呼び出し方
----------------
from module.function.yahoo_get_history import get_history

df = get_history(ticker, start=start, end=end, interval="1d")
if df.empty:
    print(f"[WARN] {ticker}: データ取得失敗（スキップ）")
    continue
----------------
"""

import pandas as pd
import yfinance as yf


def get_history(symbol: str, start: str, end: str, interval: str = "1d", session=None) -> pd.DataFrame:
    """
    yfinance で株価履歴を取得して DataFrame で返す。

    Parameters
    ----------
    symbol   : ティッカー文字列（例: "7203.T"）
    start    : 取得開始日 "YYYY-MM-DD"
    end      : 取得終了日 "YYYY-MM-DD"（排他的）
    interval : "1d"（日足）または "1m"（1分足）など
    session  : 後方互換のために受け取るが使用しない

    Returns
    -------
    DataFrame（空の場合は pd.DataFrame()）
    カラム: Open / High / Low / Close / Volume（非調整終値）
    インデックス: タイムゾーン付き DatetimeIndex
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval, auto_adjust=False)
    except Exception as e:
        print(f"[ERROR] {symbol}: データ取得中に例外が発生しました -> {e}")
        return pd.DataFrame()

    if df is None or df.empty:
        print(f"[WARN] {symbol}: データが空でした（スキップ）")
        return pd.DataFrame()

    return df
