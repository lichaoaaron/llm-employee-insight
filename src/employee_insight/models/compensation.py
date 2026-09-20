"""薪酬数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SalaryBand:
    """薪酬带宽：一个职级/岗位序列的薪酬区间。"""

    band_id: str
    name: str
    min_salary: float
    mid_salary: float
    max_salary: float
    position_ids: List[str] = field(default_factory=list)

    def contains(self, salary: float) -> bool:
        return self.min_salary <= salary <= self.max_salary

    def to_dict(self) -> dict:
        return {
            "band_id": self.band_id,
            "name": self.name,
            "min_salary": self.min_salary,
            "mid_salary": self.mid_salary,
            "max_salary": self.max_salary,
        }


@dataclass
class EmployeeSalary:
    """员工薪酬记录。"""

    employee_id: str
    base_salary: float
    bonus: float = 0.0
    band_id: Optional[str] = None

    @property
    def total_compensation(self) -> float:
        return self.base_salary + self.bonus


@dataclass
class CompaRatioResult:
    """薪酬竞争力分析结果。"""

    employee_id: str
    band_id: str
    salary: float
    compa_ratio: float        # 相对薪酬中位值
    position_in_range: float  # 在带宽内的位置 0~1
    below_range: bool
    above_range: bool

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "band_id": self.band_id,
            "salary": self.salary,
            "compa_ratio": round(self.compa_ratio, 4),
            "position_in_range": round(self.position_in_range, 4),
            "below_range": self.below_range,
            "above_range": self.above_range,
        }
