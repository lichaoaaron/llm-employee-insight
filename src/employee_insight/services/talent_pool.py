"""人才梯队服务。

基于员工画像与风险数据，识别高潜人才、关键岗位后备，输出人才梯队分层。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from employee_insight.models.employee import Employee
from employee_insight.utils.statistics import mean

_RATING_SCORE = {"S": 1.0, "A": 0.8, "B": 0.6, "C": 0.4, "D": 0.2}


@dataclass
class TalentTierResult:
    """人才梯队分层结果。"""

    employee_id: str
    name: str
    potential_score: float
    tier: str           # core / high_potential / key
    rationale: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "potential_score": round(self.potential_score, 4),
            "tier": self.tier,
            "rationale": self.rationale,
        }


class TalentPoolService:
    """高潜人才与梯队识别。"""

    def identify(self, employees: List[Employee]) -> List[TalentTierResult]:
        """识别人才梯队，返回按潜力降序的结果。"""
        results: List[TalentTierResult] = []
        for emp in employees:
            potential = self._potential_score(emp)
            tier, rationale = self._tier_and_rationale(emp, potential)
            results.append(
                TalentTierResult(
                    employee_id=emp.employee_id,
                    name=emp.name,
                    potential_score=potential,
                    tier=tier,
                    rationale=rationale,
                )
            )
        results.sort(key=lambda r: r.potential_score, reverse=True)
        return results

    @staticmethod
    def _potential_score(emp: Employee) -> float:
        """潜力分 = 绩效 + 技能丰富度 + 成长性（晋升节奏）。"""
        performance = _RATING_SCORE.get(emp.performance_rating, 0.0)
        skill_breadth = min(1.0, len(emp.skills) / 5.0)
        growth = min(1.0, emp.months_since_promotion / 24.0)  # 晋升越频繁越有潜力
        return 0.5 * performance + 0.3 * skill_breadth + 0.2 * (1.0 - growth)

    @staticmethod
    def _tier_and_rationale(emp: Employee, potential: float) -> tuple[str, List[str]]:
        rationale: List[str] = []
        if _RATING_SCORE.get(emp.performance_rating, 0.0) >= 0.8:
            rationale.append("绩效优秀")
        if len(emp.skills) >= 4:
            rationale.append("技能丰富")
        if potential >= 0.7:
            return "high_potential", rationale
        if potential >= 0.5:
            return "core", rationale
        return "key", rationale

    def tier_distribution(self, results: List[TalentTierResult]) -> dict:
        """统计梯队分布。"""
        dist: dict[str, int] = {}
        for r in results:
            dist[r.tier] = dist.get(r.tier, 0) + 1
        return dist
