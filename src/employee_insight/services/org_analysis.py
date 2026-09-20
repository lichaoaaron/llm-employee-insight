"""组织分析服务。

从员工列表出发，计算部门分布、平均司龄、管理幅度等基础组织指标，
为管理者提供结构化的组织健康视图。
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from employee_insight.models.employee import Employee


@dataclass
class DeptStat:
    """单个部门的统计结果。"""

    department: str
    headcount: int
    avg_tenure: float
    senior_count: int


@dataclass
class OrgReport:
    """组织分析报告。"""

    total_headcount: int
    department_count: int
    dept_stats: List[DeptStat]

    def to_dict(self) -> dict:
        return {
            "total_headcount": self.total_headcount,
            "department_count": self.department_count,
            "departments": [
                {
                    "department": s.department,
                    "headcount": s.headcount,
                    "avg_tenure": round(s.avg_tenure, 2),
                    "senior_count": s.senior_count,
                }
                for s in self.dept_stats
            ],
        }


class OrgAnalysisService:
    """组织维度统计分析。"""

    def analyze(self, employees: List[Employee]) -> OrgReport:
        groups: Dict[str, List[Employee]] = defaultdict(list)
        for emp in employees:
            groups[emp.department].append(emp)

        stats: List[DeptStat] = []
        for dept, members in sorted(groups.items()):
            avg_tenure = sum(m.tenure_years for m in members) / len(members)
            senior_count = sum(1 for m in members if m.tenure_years >= 5)
            stats.append(
                DeptStat(
                    department=dept,
                    headcount=len(members),
                    avg_tenure=avg_tenure,
                    senior_count=senior_count,
                )
            )

        return OrgReport(
            total_headcount=len(employees),
            department_count=len(groups),
            dept_stats=stats,
        )
