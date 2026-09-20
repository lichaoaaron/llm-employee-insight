"""员工画像服务单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.models.employee import Employee
from employee_insight.services.llm_client import MockLLMClient
from employee_insight.services.profile_service import ProfileService


class TestProfileService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProfileService(MockLLMClient())

    def _employee(self, **overrides) -> Employee:
        base = dict(
            employee_id="E1",
            name="测试",
            department="研发中心",
            title="高级工程师",
            tenure_years=3.0,
            performance_rating="A",
            overtime_hours_per_month=30,
            months_since_promotion=12,
            skills=["Python"],
            resume_text="熟悉 Python 与机器学习。",
        )
        base.update(overrides)
        return Employee(**base)

    def test_build_merges_skills_and_keywords(self) -> None:
        profile = self.service.build(self._employee())
        self.assertIn("Python", profile.skill_tags)
        self.assertIn("机器学习", profile.skill_tags)

    def test_seniority_level_junior(self) -> None:
        profile = self.service.build(self._employee(tenure_years=0.5, title="初级工程师"))
        self.assertEqual(profile.seniority_level, "junior")

    def test_seniority_level_principal(self) -> None:
        profile = self.service.build(self._employee(title="首席工程师"))
        self.assertEqual(profile.seniority_level, "principal")

    def test_build_all(self) -> None:
        profiles = self.service.build_all([self._employee(), self._employee(employee_id="E2")])
        self.assertEqual(len(profiles), 2)


if __name__ == "__main__":
    unittest.main()
