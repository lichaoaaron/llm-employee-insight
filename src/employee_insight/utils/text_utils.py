"""文本处理工具。

提供面向中英文混合文本的分词、关键词抽取、字符串相似度等基础能力，
供画像抽取、技能匹配、搜索过滤等服务复用。
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, List

# 中文按单字切分处理能力有限，这里采用「连续中文字符段 + 英文/数字词」的混合切分策略。
_CJK_RUN = re.compile(r"[\u4e00-\u9fff]+")
_ALNUM_RUN = re.compile(r"[A-Za-z0-9_]+")
# 常见停用词（供关键词抽取过滤）。
_STOP_WORDS = {
    "的", "了", "和", "与", "及", "或", "在", "是", "我", "你", "他", "她", "它",
    "有", "这", "那", "也", "都", "而", "并", "个", "对", "从", "为", "以", "等",
    "负责", "进行", "开展", "完成", "熟悉", "掌握", "了解", "包括", "以及",
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are",
}


def tokenize(text: str) -> List[str]:
    """将文本切分为 token 列表。

    规则：连续中文段作为一个 token，连续的英文/数字串作为一个 token。
    """
    if not text:
        return []
    tokens: List[str] = []
    pos = 0
    while pos < len(text):
        cjk = _CJK_RUN.match(text, pos)
        if cjk:
            tokens.append(cjk.group(0))
            pos = cjk.end()
            continue
        alnum = _ALNUM_RUN.match(text, pos)
        if alnum:
            tokens.append(alnum.group(0))
            pos = alnum.end()
            continue
        pos += 1  # 跳过标点、空白
    return tokens


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """基于词频抽取关键词，返回按出现次数降序的 token 列表。

    过滤停用词与单字符 token。
    """
    tokens = [t.lower() for t in tokenize(text) if t.lower() not in _STOP_WORDS and len(t) > 1]
    counter = Counter(tokens)
    return [word for word, _ in counter.most_common(top_n)]


def normalize_text(text: str) -> str:
    """去除首尾空白、压缩内部连续空白、统一为小写。"""
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def levenshtein_distance(a: str, b: str) -> int:
    """计算两个字符串的编辑距离（动态规划实现）。"""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def similarity(a: str, b: str) -> float:
    """基于编辑距离的相似度，取值 0~1，越大越相似。"""
    a, b = normalize_text(a), normalize_text(b)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return 1.0 - levenshtein_distance(a, b) / max(len(a), len(b))


def jaccard_similarity(left: Iterable[str], right: Iterable[str]) -> float:
    """计算两个集合的 Jaccard 相似度。"""
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def best_match(candidate: str, options: Iterable[str]) -> tuple[str, float]:
    """从候选项中找出与目标字符串最相似的一项及其相似度。"""
    best, best_score = "", -1.0
    for opt in options:
        score = similarity(candidate, opt)
        if score > best_score:
            best, best_score = opt, score
    return best, best_score
