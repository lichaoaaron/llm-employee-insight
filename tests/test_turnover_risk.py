"""离职风险评估服务单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.config import AppConfig
from employee_insight.models.employee import Employee
from employee_insight.services.turnover_risk import TurnoverRiskService


def _employee(**overrides) -> Employee:
    base = dict(
        employee_id="E1",
        name="测试",
        department="研发中心",
        title="工程师",
        tenure_years=4.0,
        performance_rating="B",
        overtime_hours_per_month=30,
        months_since_promotion=12,
        skills=["Python"],
    )
    base.update(overrides)
    return Employee(**base)


class TestTurnoverRiskService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TurnoverRiskService(AppConfig())

    def test_high_risk_new_hire(self) -> None:
        # 司龄极短 + 绩效低 + 高强度加班 => 高风险。
        result = self.service.evaluate(
            [
                _employee(
                    tenure_years=0.3,
                    performance_rating="D",
                    overtime_hours_per_month=60,
                    months_since_promotion=30,
                    skills=[],
                )
            ]
        )[0]
        self.assertEqual(result.level, "high")

    def test_low_risk_stable_employee(self) -> None:
        # 长期司龄 + 高绩效 => 低风险。
        result = self.service.evaluate(
            [
                _employee(
                    tenure_years=8.0,
                    performance_rating="S",
                    overtime_hours_per_month=10,
                    months_since_promotion=6,
                )
            ]
        )[0]
        self.assertEqual(result.level, "low")

    def test_score_in_range(self) -> None:
        result = self.service.evaluate([_employee()])[0]
        self.assertGreaterEqual(result.score, 0.0)
        self.assertLessEqual(result.score, 1.0)

    def test_sorted_by_risk_desc(self) -> None:
        results = self.service.evaluate(
            [
                _employee(employee_id="low", tenure_years=8.0, performance_rating="S"),
                _employee(employee_id="high", tenure_years=0.2, performance_rating="D"),
            ]
        )
        self.assertEqual(results[0].employee_id, "high")


if __name__ == "__main__":
    unittest.main()
