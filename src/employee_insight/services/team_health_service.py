"""团队健康评估服务。

从工作负荷分布、技能覆盖、人员流动风险、资历结构等维度评估团队健康度。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from employee_insight.models.employee import Employee
from employee_insight.services.turnover_risk import TurnoverRiskService
from employee_insight.utils.statistics import mean, stddev


@dataclass
class TeamHealthReport:
    """团队健康评估报告。"""

    department: str
    headcount: int
    avg_turnover_risk: float
    high_risk_count: int
    workload_stddev: float          # 加班时长标准差，反映负荷不均衡程度
    skill_diversity: float          # 技能多样性 0~1
    senior_ratio: float             # 资深人员（司龄>=5年）占比
    health_score: float             # 综合健康分 0~1
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "department": self.department,
            "headcount": self.headcount,
            "avg_turnover_risk": round(self.avg_turnover_risk, 4),
            "high_risk_count": self.high_risk_count,
            "workload_stddev": round(self.workload_stddev, 2),
            "skill_diversity": round(self.skill_diversity, 4),
            "senior_ratio": round(self.senior_ratio, 4),
            "health_score": round(self.health_score, 4),
            "suggestions": self.suggestions,
        }


class TeamHealthService:
    """团队健康评估。"""

    def __init__(self, risk_service: TurnoverRiskService) -> None:
        self._risk_service = risk_service

    def evaluate(self, department: str, members: List[Employee]) -> TeamHealthReport:
        if not members:
            return TeamHealthReport(
                department=department,
                headcount=0,
                avg_turnover_risk=0.0,
                high_risk_count=0,
                workload_stddev=0.0,
                skill_diversity=0.0,
                senior_ratio=0.0,
                health_score=0.0,
            )

        risks = self._risk_service.evaluate(members)
        avg_risk = mean([r.score for r in risks])
        high_count = sum(1 for r in risks if r.level == "high")

        overtime = [m.overtime_hours_per_month for m in members]
        workload_std = stddev(overtime)

        skill_diversity = self._skill_diversity(members)
        senior_ratio = sum(1 for m in members if m.tenure_years >= 5) / len(members)

        # 健康分 = 1 - 风险贡献 - 负荷失衡贡献 - 结构失衡贡献。
        risk_penalty = 0.4 * avg_risk
        workload_penalty = 0.15 * min(1.0, workload_std / 40.0)
        structure_penalty = 0.15 * (1.0 - min(1.0, senior_ratio / 0.5))
        health_score = max(0.0, min(1.0, 1.0 - risk_penalty - workload_penalty - structure_penalty))

        suggestions = self._suggestions(avg_risk, high_count, workload_std, senior_ratio, skill_diversity)

        return TeamHealthReport(
            department=department,
            headcount=len(members),
            avg_turnover_risk=avg_risk,
            high_risk_count=high_count,
            workload_stddev=workload_std,
            skill_diversity=skill_diversity,
            senior_ratio=senior_ratio,
            health_score=health_score,
            suggestions=suggestions,
        )

    @staticmethod
    def _skill_diversity(members: List[Employee]) -> float:
        """技能多样性：去重技能总数与总技能数的比例。"""
        all_skills = [s for m in members for s in m.skills]
        if not all_skills:
            return 0.0
        return len(set(all_skills)) / len(all_skills)

    @staticmethod
    def _suggestions(
        avg_risk: float,
        high_count: int,
        workload_std: float,
        senior_ratio: float,
        skill_diversity: float,
    ) -> List[str]:
        tips: List[str] = []
        if high_count > 0:
            tips.append(f"存在 {high_count} 名高风险离职员工，建议重点面谈")
        elif avg_risk > 0.5:
            tips.append("团队整体离职风险偏高，建议关注激励与保留措施")
        if workload_std >= 30:
            tips.append("加班负荷分布不均，建议重新平衡任务分配")
        if senior_ratio < 0.2:
            tips.append("资深人员占比偏低，建议加强梯队培养")
        if skill_diversity < 0.3:
            tips.append("技能结构单一，建议补充多元技能人才")
        if not tips:
            tips.append("团队状态良好，保持现有管理节奏")
        return tips
