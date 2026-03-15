from __future__ import annotations

import os
import sys
import time
import datetime as dt
from pathlib import Path
import smtplib
from email.message import EmailMessage


def send_gmail_csv(
    gmail_address: str,
    app_password: str,
    to_addrs: list[str],
    subject: str,
    body: str,
    csv_path: Path,
) -> None:
    """Gmail SMTPでCSVを添付送信する（送信の責務だけ）"""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    msg = EmailMessage()
    msg["From"] = gmail_address
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(body)

    msg.add_attachment(
        csv_path.read_bytes(),
        maintype="text",
        subtype="csv",
        filename=csv_path.name,
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(gmail_address, app_password)
        smtp.send_message(msg)


def resolve_csv_path(base_dir: Path, mode: str, target_date: dt.date | None = None) -> Path:
    """main.pyの出力規約(output/YYYY-MM-DD/rank_MODE.csv)に合わせてCSVパスを決める"""
    d = target_date or dt.date.today()
    # d = dt.date(2026, 1, 14)  # for test
    return base_dir / "output" / d.strftime("%Y-%m-%d") / f"rank_{mode}.csv"


def wait_for_file(path: Path, timeout_sec: int = 300, interval_sec: int = 10) -> None:
    """ファイルが作られるまで最大timeout_sec待つ（見つからなければ例外）"""
    start = time.time()
    while not path.exists():
        if time.time() - start > timeout_sec:
            raise TimeoutError(f"Timed out waiting for file: {path}")
        time.sleep(interval_sec)


def parse_mode(argv: list[str]) -> str:
    """引数からmodeを取る。未指定なら1430。"""
    if len(argv) <= 1:
        return "1430"
    mode = argv[1].strip()
    allowed = {"1430", "1500", "1515", "1530"}
    if mode not in allowed:
        raise ValueError(f"Invalid mode: {mode} (expected one of {sorted(allowed)})")
    return mode


def get_required_env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise ValueError(f"Missing env var: {name}")
    return v


def main() -> int:
    try:
        base_dir = Path(__file__).resolve().parent  # RealTime_scoring直下に置く前提
        mode = parse_mode(sys.argv)

        # タスクスケジューラ等で環境変数を設定しておく想定
        gmail_address = get_required_env("GMAIL_ADDRESS")
        app_password = get_required_env("GMAIL_APP_PASSWORD")
        to_addrs = [x.strip() for x in get_required_env("GMAIL_TO").split(",") if x.strip()]

        csv_path = resolve_csv_path(base_dir, mode)

        # 15:00起動時点でまだ生成されてない可能性がゼロではないので少し待つ（不要なら0に）
        timeout_sec = int(os.getenv("WAIT_CSV_TIMEOUT_SEC", "300"))
        interval_sec = int(os.getenv("WAIT_CSV_INTERVAL_SEC", "10"))
        if timeout_sec > 0:
            wait_for_file(csv_path, timeout_sec=timeout_sec, interval_sec=interval_sec)

        # ヘッダだけ等を弾きたいならサイズチェック（必要なら調整）
        min_bytes = int(os.getenv("MIN_CSV_BYTES", "10"))
        if csv_path.stat().st_size < min_bytes:
            raise ValueError(f"CSV too small (maybe empty/header only): {csv_path}")

        today_str = dt.date.today().strftime("%Y-%m-%d")
        subject = f"rank_{mode}.csv ({today_str})"
        body = f"本日のスコアリング結果を送付します。\n\n{csv_path}"

        # ★ mainから送信関数を呼ぶ（あなたの好みの形）
        send_gmail_csv(
            gmail_address=gmail_address,
            app_password=app_password,
            to_addrs=to_addrs,
            subject=subject,
            body=body,
            csv_path=csv_path,
        )

        print(f"[INFO] Sent: {csv_path} -> {to_addrs}")
        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
