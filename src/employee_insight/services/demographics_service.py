"""人员结构分析服务。

分析组织的人员结构：司龄分布、职级结构、部门集中度等，
为人力资源规划提供基础数据。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from employee_insight.models.employee import Employee
from employee_insight.utils.statistics import frequency_distribution, mean, median, percentile


@dataclass
class DemographicsReport:
    """人员结构分析报告。"""

    total: int
    avg_tenure: float
    median_tenure: float
    tenure_p90: float
    tenure_distribution: Dict[str, int]
    rating_distribution: Dict[str, int]
    department_distribution: Dict[str, int]
    title_distribution: Dict[str, int]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "avg_tenure": round(self.avg_tenure, 2),
            "median_tenure": round(self.median_tenure, 2),
            "tenure_p90": round(self.tenure_p90, 2),
            "tenure_distribution": self.tenure_distribution,
            "rating_distribution": self.rating_distribution,
            "department_distribution": self.department_distribution,
            "title_distribution": self.title_distribution,
        }


class DemographicsService:
    """人员结构分析。"""

    @staticmethod
    def _tenure_bucket(years: float) -> str:
        """把司龄映射到区间桶。"""
        if years < 1:
            return "0-1年"
        if years < 3:
            return "1-3年"
        if years < 5:
            return "3-5年"
        if years < 10:
            return "5-10年"
        return "10年以上"

    def analyze(self, employees: List[Employee]) -> DemographicsReport:
        tenure_values = [e.tenure_years for e in employees]
        tenure_buckets = [self._tenure_bucket(t) for t in tenure_values]
        ratings = [e.performance_rating for e in employees]
        departments = [e.department for e in employees]
        titles = [e.title for e in employees]

        return DemographicsReport(
            total=len(employees),
            avg_tenure=mean(tenure_values),
            median_tenure=median(tenure_values),
            tenure_p90=percentile(tenure_values, 90),
            tenure_distribution=frequency_distribution(tenure_buckets),
            rating_distribution=frequency_distribution(ratings),
            department_distribution=frequency_distribution(departments),
            title_distribution=frequency_distribution(titles),
        )
