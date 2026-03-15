import os
import time
import json
import math
import threading
from typing import Dict, List, Set, Optional

import requests
import websocket


# ==========
# 設定
# ==========
API_BASE = "http://localhost:18080/kabusapi"   # 検証は 18081 のこともある
WS_URL = "ws://localhost:18080/kabusapi/websocket"

TOKEN = os.environ.get("KABU_API_TOKEN", "")

BATCH_SIZE = 50
BATCH_WAIT_SEC = 30           # まずは 20～30秒で計測推奨
SLEEP_AFTER_REGISTER = 1.0    # 登録反映の猶予（最初は1秒）


# ==========
# REST: PUSH対象銘柄の登録
# ==========
def register_push_symbols(symbols: List[str]) -> None:
    """
    kabuステの「PUSH配信対象銘柄リスト」に登録する想定。
    実際のAPIパス/ボディはあなたの実装に合わせて調整してください。
    """
    url = f"{API_BASE}/register"  # ←ここは要調整（例：銘柄登録用API）
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": TOKEN,
    }

    payload = {
        "Symbols": symbols
    }

    r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=10)
    r.raise_for_status()


# ==========
# WebSocket受信（バッチ内の銘柄が1回でも来たらOKにする）
# ==========
class TickCollector:
    def __init__(self, target_symbols: Set[str]):
        self.target_symbols = set(target_symbols)
        self.got_symbols: Set[str] = set()
        self.last: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def on_message(self, ws, message: str):
        try:
            data = json.loads(message)
        except Exception:
            return

        # ここは配信フォーマットに合わせて調整
        # kabuステPUSHの例：Symbol / CurrentPrice / CurrentPriceTime などが入る
        symbol = str(data.get("Symbol") or data.get("symbol") or "")
        if not symbol:
            return

        with self.lock:
            if symbol in self.target_symbols:
                cp = data.get("CurrentPrice")
                cpt = data.get("CurrentPriceTime")
                if cp is not None:
                    self.got_symbols.add(symbol)
                    self.last[symbol] = {
                        "CurrentPrice": cp,
                        "CurrentPriceTime": cpt,
                        "raw": data,
                    }

    def snapshot(self):
        with self.lock:
            return set(self.got_symbols), dict(self.last)


def ws_collect_for_batch(symbols: List[str], wait_sec: int) -> Dict[str, Dict]:
    target = set(symbols)
    collector = TickCollector(target_symbols=target)

    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=collector.on_message,
    )

    t = threading.Thread(target=ws.run_forever, daemon=True)
    t.start()

    start = time.time()
    while True:
        got, last = collector.snapshot()
        if got == target:
            break
        if time.time() - start >= wait_sec:
            break
        time.sleep(0.1)

    ws.close()
    _, last = collector.snapshot()
    return last


# ==========
# メイン：498銘柄をバッチで回して計測
# ==========
def run_rotation_test(all_symbols: List[str]):
    batches = [all_symbols[i:i+BATCH_SIZE] for i in range(0, len(all_symbols), BATCH_SIZE)]
    print(f"symbols={len(all_symbols)} batches={len(batches)} batch_size={BATCH_SIZE}")

    overall_start = time.time()
    results: Dict[str, Dict] = {}
    batch_stats = []

    for idx, batch in enumerate(batches, start=1):
        b_start = time.time()

        # 1) 登録
        register_push_symbols(batch)
        time.sleep(SLEEP_AFTER_REGISTER)

        # 2) 受信待ち
        last_map = ws_collect_for_batch(batch, wait_sec=BATCH_WAIT_SEC)

        # 3) 結果
        for sym, rec in last_map.items():
            results[sym] = rec

        elapsed = time.time() - b_start
        got_cnt = len(last_map)
        miss_cnt = len(batch) - got_cnt
        batch_stats.append((idx, len(batch), got_cnt, miss_cnt, elapsed))
        print(f"[batch {idx}/{len(batches)}] size={len(batch)} got={got_cnt} miss={miss_cnt} elapsed={elapsed:.1f}s")

    overall_elapsed = time.time() - overall_start
    got_total = len(results)
    miss_total = len(all_symbols) - got_total

    print("\n==== Summary ====")
    print(f"overall_elapsed={overall_elapsed:.1f}s")
    print(f"got_total={got_total} miss_total={miss_total} miss_rate={miss_total/len(all_symbols):.1%}")
    print("batch_stats: (idx, size, got, miss, elapsed)")
    for row in batch_stats:
        print(row)

    return results


if __name__ == "__main__":
    # ここに498銘柄（例： '7203' とか '7203@1' とかAPI仕様に合わせた形式）を入れる
    symbols = []  # TODO
    run_rotation_test(symbols)
