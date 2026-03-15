import datetime as dt
from pathlib import Path
from module.function.dl_codes import fetch_data_j_xls
from module.codes_data_select import build_codes_data
from module.target_scoring import score_targets
import sys

def _parse_mode(argv) -> str:
    # 何も指定されなければ 1430
    default_mode = "1430"
    if len(argv) <= 1:
        return default_mode

    mode = str(argv[1]).strip()
    allowed = {"1430", "1500", "1515", "1530"}
    if mode not in allowed:
        print(f'[ERROR] mode が不正です: "{mode}" (expected: 1430/1500/1515/1530)')
        sys.exit(2)
    return mode

#data_j.xls の確保（DL or 既存ファイル）
BASE_DIR = Path(__file__).resolve().parent
JPX_LIST_XLS = BASE_DIR / "data" / "data_j.xls"

print("[INFO] JPXから data_j.xls のURL探索 → ダウンロードを試行します...")
ok = fetch_data_j_xls(JPX_LIST_XLS)
if ok:
    print(f"[INFO] ダウンロード成功: {JPX_LIST_XLS}")
else:
    if JPX_LIST_XLS.exists():
        print(f"[WARN] ダウンロード失敗。既存の {JPX_LIST_XLS} を使用します。")
    else:
        print("[ERROR] data_j.xls の入手に失敗し、既存ファイルもありません。")
        sys.exit(1)


BASE_DIR = Path(__file__).resolve().parent

codes_csv = BASE_DIR / "input" / "codes.csv"
data_j_xls = BASE_DIR / "data" / "data_j.xls"
out_csv   = BASE_DIR / "output" / "codes_data.csv"
build_codes_data(
    codes_csv=codes_csv,
    data_j_xls=data_j_xls,
    out_csv=out_csv,
)

print("[INFO] codes_data.csv 作成完了")


BASE_DIR = Path(__file__).resolve().parent

codes_path = BASE_DIR / "output" / "codes_data.csv"
output_dir = BASE_DIR / "output"

today = dt.date.today()
mode = _parse_mode(sys.argv)
print(f"[INFO] mode={mode}")

out_csv = score_targets(
    codes_path=codes_path,
    output_dir=output_dir,
    today=today,
    mode=mode,
)
print("[INFO] スコアリング完了:", out_csv)