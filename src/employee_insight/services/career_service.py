"""职业规划服务。

基于职业发展路径与员工画像，输出可晋升路径与继任候选人成熟度评估。
"""
from __future__ import annotations

from typing import Dict, List

from employee_insight.models.career import CareerPath, SuccessionCandidate
from employee_insight.models.employee import Employee

# 绩效评级映射为 0~1 的绩效分，用于继任成熟度评估。
_RATING_SCORE = {"S": 1.0, "A": 0.8, "B": 0.6, "C": 0.4, "D": 0.2}


class CareerService:
    """职业发展分析服务。"""

    def __init__(self, paths: List[CareerPath]) -> None:
        self._paths_by_from: Dict[str, List[CareerPath]] = {}
        for p in paths:
            self._paths_by_from.setdefault(p.from_position_id, []).append(p)

    def available_paths(self, employee: Employee, position_id: str) -> List[CareerPath]:
        """返回员工从当前岗位可走的职业路径（已过滤不满足条件者）。"""
        result: List[CareerPath] = []
        for path in self._paths_by_from.get(position_id, []):
            if employee.tenure_years < path.required_tenure_years:
                continue
            if _RATING_SCORE.get(employee.performance_rating, 0.0) < _RATING_SCORE.get(path.required_performance, 0.0):
                continue
            result.append(path)
        return result

    def succession_rank(
        self,
        candidates: List[Employee],
        position_id: str,
        position_skill_ids: List[str],
    ) -> List[SuccessionCandidate]:
        """对继任候选人按成熟度排序。

        成熟度由四方面加权：司龄（0.25）、绩效（0.35）、技能覆盖（0.25）、
        距晋升月数（0.15，越久越成熟）。
        """
        ranked: List[SuccessionCandidate] = []
        for emp in candidates:
            tenure_factor = min(1.0, emp.tenure_years / 8.0)
            performance_factor = _RATING_SCORE.get(emp.performance_rating, 0.0)
            skill_factor = self._skill_coverage(emp.skills, position_skill_ids)
            promotion_factor = min(1.0, emp.months_since_promotion / 24.0)
            score = (
                0.25 * tenure_factor
                + 0.35 * performance_factor
                + 0.25 * skill_factor
                + 0.15 * promotion_factor
            )
            level = self._readiness(score)
            strengths, gaps = self._strength_gap(emp.skills, position_skill_ids)
            ranked.append(
                SuccessionCandidate(
                    employee_id=emp.employee_id,
                    name=emp.name,
                    position_id=position_id,
                    readiness_score=score,
                    level=level,
                    strengths=strengths,
                    gaps=gaps,
                )
            )
        ranked.sort(key=lambda c: c.readiness_score, reverse=True)
        return ranked

    @staticmethod
    def _skill_coverage(owned: List[str], required: List[str]) -> float:
        if not required:
            return 1.0
        owned_set = set(owned)
        return len(owned_set & set(required)) / len(set(required))

    @staticmethod
    def _readiness(score: float) -> str:
        if score >= 0.7:
            return "ready"
        if score >= 0.5:
            return "developing"
        return "future"

    @staticmethod
    def _strength_gap(owned: List[str], required: List[str]) -> tuple[List[str], List[str]]:
        owned_set, required_set = set(owned), set(required)
        strengths = sorted(owned_set & required_set)
        gaps = sorted(required_set - owned_set)
        return strengths, gaps
