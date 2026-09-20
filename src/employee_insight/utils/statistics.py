"""统计工具。

提供描述性统计与简单相关性计算，供组织分析、团队健康、绩效趋势等服务复用。
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, List, Sequence


def mean(values: Sequence[float]) -> float:
    """算术平均值；空序列返回 0。"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    """中位数。"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    mid = n // 2
    if n % 2 == 1:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0


def variance(values: Sequence[float], sample: bool = True) -> float:
    """方差；默认按样本方差（除以 n-1）计算。"""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    denominator = len(values) - 1 if sample else len(values)
    return sum((v - m) ** 2 for v in values) / denominator


def stddev(values: Sequence[float], sample: bool = True) -> float:
    """标准差。"""
    return math.sqrt(variance(values, sample))


def percentile(values: Sequence[float], p: float) -> float:
    """计算第 p 百分位（0<=p<=100），使用线性插值法。"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]
    rank = (p / 100.0) * (len(sorted_values) - 1)
    lower = int(rank)
    frac = rank - lower
    if lower + 1 >= len(sorted_values):
        return sorted_values[lower]
    return sorted_values[lower] * (1 - frac) + sorted_values[lower + 1] * frac


def pearson_correlation(xs: Sequence[float], ys: Sequence[float]) -> float:
    """皮尔逊相关系数；长度不一致或方差为 0 时返回 0。"""
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx, my = mean(xs), mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return 0.0
    return cov / (dx * dy)


def frequency_distribution(values: Iterable[str]) -> dict[str, int]:
    """统计各取值的出现次数，按次数降序返回。"""
    counter = Counter(values)
    return dict(counter.most_common())


def zscore(value: float, avg: float, sd: float) -> float:
    """标准分数（z-score）；标准差为 0 时返回 0。"""
    if sd == 0:
        return 0.0
    return (value - avg) / sd
