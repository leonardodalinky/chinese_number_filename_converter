import sys
import os
import glob
import argparse
import chinese2digits as cd
from pathlib import Path
from typing import Optional, List

CHINESE_DIGIT = (
    "零", "一", "二", "三", "四", "五", "六", "七", "八", "九",
)
CHINESE_DIGIT_DICT = {
    "0": "零",
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九"
}

CHINESE_CARRY_DIGIT = (
    ("亿", 1e8),
    ("万", 1e4),
    ("千", 1e3),
    ("百", 1e2),
    ("十", 1e1),
)


def v2c(v: str) -> str:
    """
    将阿拉伯数字字符串转为中文字符

    :param v:
    :return:
    """
    v = v.strip()
    i_part: str = "0"
    d_part: Optional[str] = None
    if v.count(".") == 1:
        # 是小数
        tmp = v.split(".")
        i_part, d_part = tmp
    elif v.count(".") == 0:
        # 是整数
        i_part = v
    else:
        raise ValueError(f"{v} 不是一个正经的小数")
    # 先处理小数
    if d_part is not None:
        for k, v in CHINESE_DIGIT_DICT.items():
            d_part = d_part.replace(k, v)
    d_str = "" if d_part is None else f"点{d_part}"
    # 再处理整数
    i_value = int(i_part)
    for k, v in CHINESE_CARRY_DIGIT:
        # 处理多位数
        if i_value >= v:
            q = int(i_value / v)
            r = int(i_value - q * v)
            return v2c(str(q)) + k + v2c(str(r)) + d_str
    # 能运行到这里，都是个位数
    if i_value >= 10:
        return v2c(str(i_value)) + d_str
    else:
        return CHINESE_DIGIT_DICT[str(i_value)] + d_str


def c2a(s: str) -> str:
    """
    将一串字符中所有的中文数字到阿拉伯数字，返回一串新字符串

    :param s:
    :return:
    """
    return cd.takeNumberFromString(s)["replacedText"]


def a2c(s: str) -> str:
    """
    将一串字符中所有的阿拉伯数字到中文数字，返回一串新字符串

    :param s:
    :return:
    """
    d = cd.takeDigitsNumberFromString(s)
    ret = s
    for digits in d["digitsNumberStringList"]:
        ret = ret.replace(digits, v2c(digits))
    return ret


def convert_filename(filepath: str, to_arabic=True):
    """
    将路径上的文件修改名称

    :param filepath: 文件路径
    :param to_arabic: 若为 True，则为中文转阿拉伯；反之为阿拉伯转中文.
    :return:
    """
    pass


if __name__ == "__main__":
    # arg parser
    parser = argparse.ArgumentParser(description="将文件名的中文数字与阿拉伯数字互相转化的工具")
    parser.add_argument("-t", "--type", type=str, choices=["c2a", "a2c"], default="c2a", action="store",
                        help="c2a 将中文转为阿拉伯，a2c 将阿拉伯转为中文，默认为 c2a")
    parser.add_argument("paths", type=str, nargs="+", action="store", help="文件或者文件夹的路径，支持通配符")
    if len(sys.argv) <= 1:
        print("请输入参数!")
        parser.print_help()
        sys.exit(-1)
    args = parser.parse_args(sys.argv[1:])
    raw_paths: List[str] = args.paths
    conv_func = c2a if args.type == "c2a" else a2c
    for p in raw_paths:
        paths: List[str] = glob.glob(p)
        for path_str in paths:
            path = Path(path_str)
            if path.is_dir():
                # dir
                for file_path in path.iterdir():
                    if file_path.is_file():
                        file_path.rename(file_path.parent.joinpath(conv_func(file_path.name)))
            elif path.is_file():
                # file
                path.rename(path.parent.joinpath(conv_func(path.name)))
    sys.exit(0)
