"""薪酬分析服务。

基于薪酬带宽，计算员工的薪酬竞争力（compa-ratio）与区间内位置，
识别低于/高于带宽的异常薪酬，辅助薪酬公平性分析。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from employee_insight.models.compensation import CompaRatioResult, EmployeeSalary, SalaryBand


@dataclass
class PayEquityReport:
    """薪酬公平性报告。"""

    total: int
    below_range_count: int
    above_range_count: int
    avg_compa_ratio: float
    results: List[CompaRatioResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "below_range_count": self.below_range_count,
            "above_range_count": self.above_range_count,
            "avg_compa_ratio": round(self.avg_compa_ratio, 4),
            "results": [r.to_dict() for r in self.results],
        }


class CompensationService:
    """薪酬竞争力与公平性分析。"""

    def __init__(self, bands: List[SalaryBand]) -> None:
        self._bands: Dict[str, SalaryBand] = {b.band_id: b for b in bands}

    def analyze(self, salaries: List[EmployeeSalary]) -> PayEquityReport:
        """对一批员工薪酬做竞争力分析。"""
        results: List[CompaRatioResult] = []
        for salary in salaries:
            band = self._bands.get(salary.band_id or "")
            if band is None:
                # 未归属带宽的员工跳过（或按无带宽处理）。
                continue
            compa_ratio = salary.base_salary / band.mid_salary if band.mid_salary else 0.0
            span = band.max_salary - band.min_salary
            position = (salary.base_salary - band.min_salary) / span if span > 0 else 0.0
            results.append(
                CompaRatioResult(
                    employee_id=salary.employee_id,
                    band_id=band.band_id,
                    salary=salary.base_salary,
                    compa_ratio=compa_ratio,
                    position_in_range=max(0.0, min(1.0, position)),
                    below_range=salary.base_salary < band.min_salary,
                    above_range=salary.base_salary > band.max_salary,
                )
            )

        below = sum(1 for r in results if r.below_range)
        above = sum(1 for r in results if r.above_range)
        avg_compa = sum(r.compa_ratio for r in results) / len(results) if results else 0.0
        return PayEquityReport(
            total=len(results),
            below_range_count=below,
            above_range_count=above,
            avg_compa_ratio=avg_compa,
            results=results,
        )
