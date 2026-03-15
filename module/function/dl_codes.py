"""
JPXサイトから data_j.xls のURLを探索しダウンロードする関数群
呼び出し方
----------------
from module.01_dl_codes import fetch_data_j_xls
ok = fetch_data_j_xls(dest=Path("保存先のパス"))
----------------
"""

import re
import requests 
from pathlib import Path

# -------------------------
# JPX から data_j.xls のURLをページ内探索で見つけてDL
# -------------------------
def fetch_data_j_xls(dest: Path, timeout: float = 15.0) -> bool:
    """
    JPXサイトから data_j.xls のリンクを探索しダウンロードする。
    成功: True / 失敗: False
    """
    CANDIDATE_PAGES = [
        "https://www.jpx.co.jp/markets/statistics-equities/misc/01.html",
        "https://www.jpx.co.jp/markets/statistics-equities/misc/index.html",
        "https://www.jpx.co.jp/markets/statistics-equities/index.html",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MarketCodesFetcher/1.0)"
    }
    session = requests.Session()
    session.headers.update(headers)

    target_url = None
    for page in CANDIDATE_PAGES:
        try:
            resp = session.get(page, timeout=timeout)
            if resp.status_code != 200:
                continue
            m = re.search(r'href=["\']([^"\']*data_j\.xls)["\']', resp.text, re.IGNORECASE)
            if m:
                link = m.group(1)
                if link.startswith("http"):
                    target_url = link
                else:
                    from urllib.parse import urljoin
                    target_url = urljoin(page, link)
                break
        except Exception:
            continue

    if not target_url:
        return False

    try:
        r = session.get(target_url, timeout=timeout)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return True
    except Exception:
        return False


# ==========================================================
# 呼び出し例（main.py から）
# ==========================================================
#
#    from pathlib import Path
#    from module.01_dl_codes import fetch_data_j_xls
#
#   data_j.xls の確保（DL or 既存ファイル）
#    BASE_DIR = Path(__file__).resolve().parent
#    JPX_LIST_XLS = BASE_DIR / "data" / "data_j.xls"
#
#    print("[INFO] JPXから data_j.xls のURL探索 → ダウンロードを試行します...")
#    ok = fetch_data_j_xls(JPX_LIST_XLS)
#    if ok:
#        print(f"[INFO] ダウンロード成功: {JPX_LIST_XLS}")
#    else:
#        if JPX_LIST_XLS.exists():
#            print(f"[WARN] ダウンロード失敗。既存の {JPX_LIST_XLS} を使用します。")
#        else:
#            print("[ERROR] data_j.xls の入手に失敗し、既存ファイルもありません。")
#            sys.exit(1)
#
# ==========================================================