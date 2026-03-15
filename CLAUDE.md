# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

日本株のリアルタイム・スコアリングシステム。JPX上場銘柄リストとYahoo Financeの株価データを使い、テクニカル指標に基づくルールで銘柄をスコアリング・ランキングしてCSV出力する。

## 実行方法

```bash
# 通常実行（デフォルト mode=1430）
python main.py

# モード指定（1430 / 1500 / 1515 / 1530）
python main.py 1430

# バッチ経由（ログあり）
RealTime_scoring.bat 1430

# 結果CSVをGmailで送信（環境変数 GMAIL_ADDRESS / GMAIL_APP_PASSWORD / GMAIL_TO が必要）
python send_csv.py 1430
```

Python 3.10 を前提とする（`C:\Program Files\Python310\python.exe`）。

## アーキテクチャ

`main.py` が以下の3ステップを順番に実行する：

### ステップ1: JPX銘柄リスト取得
`module/function/dl_codes.py` — JPXサイトから `data/data_j.xls` をダウンロード（失敗時は既存ファイルを使用）。

### ステップ2: 対象銘柄データ構築
`module/codes_data_select.py` — `input/codes.csv`（スコアリング対象コード一覧）と `data_j.xls` をマージし、銘柄名・市場区分・業種情報を付与して `output/codes_data.csv` を生成。

### ステップ3: スコアリング
`module/target_scoring.py` — メインエンジン。`score_targets()` が各銘柄に対して：

1. Yahoo Finance API（`module/function/yahoo_get_history.py`）から日足データ（過去365日）を取得
2. mode が `1430`/`1500`/`1515` かつスコア日が当日の場合、1分足を追加取得して指定時刻のcloseに上書き
3. `module/function/calculate/` でテクニカル指標を計算：EMA(9,20,200)、MACD(12,26,9)、RSI(14)、VWAP(前20日)
4. `module/function/scoring/add_features_for_rules.py` で派生フラグを生成（`acc_gt0`、`oc_neg`、`vol_ge_avg20` 等）
5. 各条件関数でスコアを集計し `output/YYYY-MM-DD/rank_{mode}.csv` に出力

## スコアリング設計

| カテゴリ | ルール | 上限 |
|---|---|---|
| SETUP | R1(160), R5(130), R6(110), R9(50) | 450 |
| CONFIRM | R2(130), R3(100), R8(20) | 250 |
| MARKET | R4(190), R7(70), R10(50) | 300 |
| PENALTY | D_RSI(-60), D_TRND(-80), D_BIG(-20), D_VOL(0) | -400 |
| BONUS | R1+R6(120)、R3+R7(120) 等の組み合わせ | 400 |

**フィルタ条件**（該当銘柄はスキップ）：
- 出来高 < 3,000,000株
- 売買代金 < 10,000,000,000円
- 日足データが150日未満

score <= 0 の銘柄は出力しない。

## ディレクトリ構造

```
input/codes.csv          # 対象銘柄コード一覧（"codes"列）
data/data_j.xls          # JPX銘柄リスト（自動DL）
output/codes_data.csv    # コード+銘柄情報のマージ結果
output/YYYY-MM-DD/       # スコアリング結果（rank_1430.csv 等）
logs/                    # バッチ実行ログ
snapshot/                # 保存済みHTMLスナップショット（nikkei225用）
```

## 各モードの意味

- `1430`: 当日14:30時点のcloseでスコアリング（1分足から取得）
- `1500`: 当日15:00時点
- `1515`: 当日15:15時点
- `1530`: 日足終値を使用（1分足取得なし）

## その他のスクリプト

- `output_close.py`: kabu+ API WebSocketを使ったリアルタイム価格取得テスト用（本番フローとは独立）
- `nikkei225_from_saved_html.py`: 保存済みHTMLからNikkei225構成銘柄を抽出
- `send_csv.py`: 結果CSVをGmail SMTPで送信（環境変数で認証情報を渡す）

## 新しいスコアリング条件を追加するとき

1. `module/function/scoring/scoring_condN.py`（または `penalty_condN.py`）を作成
2. `module/function/scoring/add_features_for_rules.py` に必要な派生フラグを追加
3. `module/target_scoring.py` の `SETUP_RULES` / `CONFIRM_RULES` / `MARKET_RULES` / `PENALTY_RULES` / `BONUS_RULES` にエントリを追加
