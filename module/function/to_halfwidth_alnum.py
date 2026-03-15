"""
全角英数字を半角英数字に変換する

呼び出し方
from module.function.to_halfwidth_alnum import _to_halfwidth_alnum
"""


def to_halfwidth_alnum(s: str) -> str:
    # 全角→半角（英数字だけ）
    zen = (
        "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
        "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
        "０１２３４５６７８９"
    )
    han = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    trans = str.maketrans(zen, han)
    return str(s).translate(trans)