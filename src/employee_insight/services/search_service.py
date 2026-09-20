"""员工搜索过滤服务。

提供按多条件组合过滤员工、以及基于文本相似度的模糊检索能力。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from employee_insight.models.employee import Employee
from employee_insight.utils.text_utils import similarity


@dataclass
class EmployeeQuery:
    """员工查询条件，所有字段均为可选，未设置的不参与过滤。"""

    department: Optional[str] = None
    title_keyword: Optional[str] = None
    min_tenure: Optional[float] = None
    performance_rating: Optional[str] = None
    required_skill: Optional[str] = None
    max_overtime: Optional[float] = None


class EmployeeSearchService:
    """员工检索服务。"""

    def filter(self, employees: List[Employee], query: EmployeeQuery) -> List[Employee]:
        """按条件组合过滤员工。"""
        result: List[Employee] = []
        for emp in employees:
            if not self._matches(emp, query):
                continue
            result.append(emp)
        return result

    def search_by_keyword(self, employees: List[Employee], keyword: str, top_n: int = 10) -> List[Employee]:
        """按关键词对姓名、岗位、技能做模糊匹配，返回相似度最高的若干员工。"""
        scored = [(emp, self._score(emp, keyword)) for emp in employees]
        scored = [pair for pair in scored if pair[1] > 0]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [emp for emp, _ in scored[:top_n]]

    @staticmethod
    def _matches(emp: Employee, query: EmployeeQuery) -> bool:
        if query.department and emp.department != query.department:
            return False
        if query.title_keyword and query.title_keyword not in emp.title:
            return False
        if query.min_tenure is not None and emp.tenure_years < query.min_tenure:
            return False
        if query.performance_rating and emp.performance_rating != query.performance_rating:
            return False
        if query.required_skill and query.required_skill not in emp.skills:
            return False
        if query.max_overtime is not None and emp.overtime_hours_per_month > query.max_overtime:
            return False
        return True

    @staticmethod
    def _score(emp: Employee, keyword: str) -> float:
        """计算员工与关键词的匹配得分，取各字段相似度最大值。"""
        candidates = [emp.name, emp.title, emp.department, *emp.skills]
        best = 0.0
        for field in candidates:
            if not field:
                continue
            score = similarity(field, keyword)
            best = max(best, score)
        return best
