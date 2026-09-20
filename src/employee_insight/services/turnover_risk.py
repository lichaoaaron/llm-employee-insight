"""离职风险评估服务。

基于多维因子对员工离职风险进行打分：司龄越短、绩效越低、加班越多、
距晋升越久、技能与岗位匹配度越低，风险越高。各因子权重由配置注入。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from employee_insight.config import AppConfig
from employee_insight.models.employee import Employee

# 绩效评级映射为 0~1 的绩效分。
_RATING_SCORE = {"S": 1.0, "A": 0.8, "B": 0.6, "C": 0.4, "D": 0.2}


@dataclass
class RiskResult:
    """单个员工的离职风险结果。"""

    employee_id: str
    name: str
    score: float
    level: str
    reasons: List[str]

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "score": round(self.score, 4),
            "level": self.level,
            "reasons": self.reasons,
        }


class TurnoverRiskService:
    """离职风险打分器。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def _score_one(self, emp: Employee) -> float:
        """返回 0~1 之间的风险分（越大越危险）。"""
        # 司龄因子：司龄越长越稳定。
        tenure_factor = max(0.0, 1.0 - emp.tenure_years / 10.0)
        # 绩效因子：绩效越好越稳定。
        performance_factor = 1.0 - _RATING_SCORE.get(emp.performance_rating, 0.5)
        # 加班因子：加班越多，离职倾向越高。
        overtime_factor = min(1.0, emp.overtime_hours_per_month / 60.0)
        # 晋升因子：距晋升越久，风险越高。
        promotion_factor = min(1.0, emp.months_since_promotion / 36.0)
        # 技能因子：技能缺失越多，匹配度越低。
        skill_factor = 0.0 if emp.skills else 0.4

        cfg = self.config
        score = (
            cfg.tenure_weight * tenure_factor
            + cfg.performance_weight * performance_factor
            + cfg.overtime_weight * overtime_factor
            + cfg.promotion_weight * promotion_factor
            + cfg.skill_weight * skill_factor
        )
        return min(1.0, max(0.0, score))

    def _level(self, score: float) -> str:
        if score >= self.config.high_risk_threshold:
            return "high"
        if score >= self.config.medium_risk_threshold:
            return "medium"
        return "low"

    def _reasons(self, emp: Employee, score: float) -> List[str]:
        reasons: List[str] = []
        if emp.tenure_years < 1:
            reasons.append("司龄不足 1 年")
        if _RATING_SCORE.get(emp.performance_rating, 0.5) <= 0.4:
            reasons.append("绩效偏低")
        if emp.overtime_hours_per_month >= 50:
            reasons.append("长期高强度加班")
        if emp.months_since_promotion >= 24:
            reasons.append("长期未获晋升")
        if not emp.skills:
            reasons.append("技能信息缺失")
        return reasons

    def evaluate(self, employees: List[Employee]) -> List[RiskResult]:
        results: List[RiskResult] = []
        for emp in employees:
            score = self._score_one(emp)
            results.append(
                RiskResult(
                    employee_id=emp.employee_id,
                    name=emp.name,
                    score=score,
                    level=self._level(score),
                    reasons=self._reasons(emp, score),
                )
            )
        # 按风险分降序排列，便于优先关注高风险人员。
        results.sort(key=lambda r: r.score, reverse=True)
        return results
