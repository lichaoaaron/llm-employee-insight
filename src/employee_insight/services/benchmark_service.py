"""部门对标服务。

将各部门的关键指标（人数、平均司龄、平均风险、资深占比等）横向对比，
识别表现突出或异常的部门。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from employee_insight.models.employee import Employee
from employee_insight.services.org_analysis import OrgAnalysisService
from employee_insight.services.turnover_risk import TurnoverRiskService
from employee_insight.utils.statistics import mean, stddev, zscore


@dataclass
class DepartmentMetric:
    """单个部门的对标指标。"""

    department: str
    headcount: int
    avg_tenure: float
    avg_risk: float
    senior_ratio: float
    z_risk: float = 0.0

    def to_dict(self) -> dict:
        return {
            "department": self.department,
            "headcount": self.headcount,
            "avg_tenure": round(self.avg_tenure, 2),
            "avg_risk": round(self.avg_risk, 4),
            "senior_ratio": round(self.senior_ratio, 4),
            "z_risk": round(self.z_risk, 4),
        }


class BenchmarkService:
    """部门对标分析。"""

    def __init__(self, risk_service: TurnoverRiskService) -> None:
        self._risk_service = risk_service
        self._org_service = OrgAnalysisService()

    def benchmark(self, employees: List[Employee]) -> List[DepartmentMetric]:
        """计算各部门指标，并对离职风险做 z-score 标准化对标。"""
        grouped: Dict[str, List[Employee]] = {}
        for emp in employees:
            grouped.setdefault(emp.department, []).append(emp)

        metrics: List[DepartmentMetric] = []
        for dept, members in grouped.items():
            risks = self._risk_service.evaluate(members)
            avg_risk = mean([r.score for r in risks])
            avg_tenure = mean([m.tenure_years for m in members])
            senior_ratio = sum(1 for m in members if m.tenure_years >= 5) / len(members)
            metrics.append(
                DepartmentMetric(
                    department=dept,
                    headcount=len(members),
                    avg_tenure=avg_tenure,
                    avg_risk=avg_risk,
                    senior_ratio=senior_ratio,
                )
            )

        # 用全部门风险均值/标准差计算 z-score，识别显著偏离的部门。
        risk_values = [m.avg_risk for m in metrics]
        avg_risk_all = mean(risk_values)
        sd_risk = stddev(risk_values)
        for m in metrics:
            m.z_risk = zscore(m.avg_risk, avg_risk_all, sd_risk)

        metrics.sort(key=lambda m: m.avg_risk, reverse=True)
        return metrics
