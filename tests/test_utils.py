"""文本工具与统计工具单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.utils.statistics import (
    frequency_distribution,
    mean,
    median,
    pearson_correlation,
    percentile,
    stddev,
)
from employee_insight.utils.text_utils import (
    extract_keywords,
    jaccard_similarity,
    levenshtein_distance,
    normalize_text,
    similarity,
    tokenize,
)


class TestTextUtils(unittest.TestCase):
    def test_tokenize_mixed(self) -> None:
        self.assertEqual(tokenize("Python 深度学习"), ["Python", "深度学习"])

    def test_extract_keywords_filters_stopwords(self) -> None:
        keywords = extract_keywords("机器学习 机器学习 负责 自然语言处理")
        self.assertIn("机器学习", keywords)
        self.assertNotIn("负责", keywords)

    def test_levenshtein(self) -> None:
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)

    def test_similarity_symmetric(self) -> None:
        self.assertAlmostEqual(similarity("abc", "abd"), 1 - 1 / 3, places=4)

    def test_jaccard(self) -> None:
        self.assertAlmostEqual(jaccard_similarity(["a", "b"], ["b", "c"]), 1 / 3, places=4)

    def test_normalize(self) -> None:
        self.assertEqual(normalize_text("  Hello   World "), "hello world")


class TestStatistics(unittest.TestCase):
    def test_mean_median(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0]
        self.assertEqual(mean(values), 2.5)
        self.assertEqual(median(values), 2.5)

    def test_median_odd(self) -> None:
        self.assertEqual(median([3.0, 1.0, 2.0]), 2.0)

    def test_stddev(self) -> None:
        self.assertAlmostEqual(stddev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]), 2.138, places=2)

    def test_percentile(self) -> None:
        self.assertEqual(percentile([1.0, 2.0, 3.0, 4.0], 50), 2.5)

    def test_correlation(self) -> None:
        self.assertAlmostEqual(pearson_correlation([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]), 1.0, places=4)

    def test_frequency(self) -> None:
        dist = frequency_distribution(["a", "b", "a"])
        self.assertEqual(dist, {"a": 2, "b": 1})


if __name__ == "__main__":
    unittest.main()
