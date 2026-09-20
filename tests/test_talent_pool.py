"""人才梯队服务单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.models.employee import Employee
from employee_insight.services.talent_pool import TalentPoolService


def _employee(**overrides) -> Employee:
    base = dict(
        employee_id="E1",
        name="张三",
        department="研发中心",
        title="工程师",
        tenure_years=3.0,
        performance_rating="A",
        overtime_hours_per_month=30,
        months_since_promotion=6,
        skills=["Python", "Java", "SQL", "机器学习", "深度学习"],
    )
    base.update(overrides)
    return Employee(**base)


class TestTalentPoolService(unittest.TestCase):
    def test_high_potential(self) -> None:
        result = TalentPoolService().identify([_employee(performance_rating="S")])[0]
        self.assertEqual(result.tier, "high_potential")

    def test_sorted_desc(self) -> None:
        results = TalentPoolService().identify(
            [
                _employee(employee_id="low", performance_rating="C", skills=["Python"]),
                _employee(employee_id="high", performance_rating="S"),
            ]
        )
        self.assertEqual(results[0].employee_id, "high")

    def test_tier_distribution(self) -> None:
        service = TalentPoolService()
        results = service.identify([_employee(), _employee(employee_id="E2", performance_rating="C")])
        dist = service.tier_distribution(results)
        self.assertGreaterEqual(sum(dist.values()), 2)


if __name__ == "__main__":
    unittest.main()
