"""流失预测模型。

在基础离职风险打分之上，引入司龄曲线、加班交互、技能缺口等更细粒度的
影响因素，输出流失概率估计与风险画像，供更精细的人员保留决策使用。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from employee_insight.models.employee import Employee
from employee_insight.utils.statistics import mean

_RATING_SCORE = {"S": 1.0, "A": 0.8, "B": 0.6, "C": 0.4, "D": 0.2}


@dataclass
class AttritionPrediction:
    """单个员工的流失预测结果。"""

    employee_id: str
    name: str
    probability: float
    tier: str
    dominant_factor: str
    factors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "probability": round(self.probability, 4),
            "tier": self.tier,
            "dominant_factor": self.dominant_factor,
            "factors": self.factors,
        }


class AttritionModel:
    """基于多因子加权的流失概率模型。"""

    def __init__(self) -> None:
        # 各因子权重。
        self.weights = {
            "tenure": 0.20,
            "performance": 0.30,
            "overtime": 0.20,
            "promotion": 0.15,
            "skill": 0.15,
        }

    def _factor_scores(self, emp: Employee) -> dict[str, float]:
        """计算各因子得分（0~1，越大越危险）。"""
        # 司龄曲线：极短（<1年）与极长（>10年）风险都偏高，中间稳定。
        if emp.tenure_years < 1:
            tenure = 0.85
        elif emp.tenure_years > 10:
            tenure = 0.55
        else:
            tenure = max(0.0, 0.85 - 0.05 * emp.tenure_years)

        performance = 1.0 - _RATING_SCORE.get(emp.performance_rating, 0.5)
        overtime = min(1.0, emp.overtime_hours_per_month / 60.0)
        promotion = min(1.0, emp.months_since_promotion / 36.0)
        skill = 0.0 if emp.skills else 0.5
        return {
            "tenure": tenure,
            "performance": performance,
            "overtime": overtime,
            "promotion": promotion,
            "skill": skill,
        }

    def predict(self, employees: List[Employee]) -> List[AttritionPrediction]:
        """对一批员工做流失概率估计。"""
        results: List[AttritionPrediction] = []
        for emp in employees:
            scores = self._factor_scores(emp)
            probability = sum(self.weights[k] * scores[k] for k in self.weights)
            probability = max(0.0, min(1.0, probability))

            # 主导因子 = 加权贡献最大的因子。
            contributions = {k: self.weights[k] * scores[k] for k in self.weights}
            dominant = max(contributions, key=contributions.get)

            factors = [k for k, s in scores.items() if s >= 0.5]
            results.append(
                AttritionPrediction(
                    employee_id=emp.employee_id,
                    name=emp.name,
                    probability=probability,
                    tier=self._tier(probability),
                    dominant_factor=dominant,
                    factors=factors,
                )
            )
        results.sort(key=lambda r: r.probability, reverse=True)
        return results

    def cohort_risk(self, predictions: List[AttritionPrediction]) -> dict:
        """统计整批预测的风险分布。"""
        if not predictions:
            return {"avg_probability": 0.0, "high_risk_count": 0, "tiers": {}}
        avg = mean([p.probability for p in predictions])
        high = sum(1 for p in predictions if p.tier == "high")
        tiers: dict[str, int] = {}
        for p in predictions:
            tiers[p.tier] = tiers.get(p.tier, 0) + 1
        return {"avg_probability": round(avg, 4), "high_risk_count": high, "tiers": tiers}

    @staticmethod
    def _tier(probability: float) -> str:
        if probability >= 0.7:
            return "high"
        if probability >= 0.45:
            return "medium"
        return "low"
