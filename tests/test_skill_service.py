"""技能服务单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.models.skill import EmployeeSkill, SkillDefinition, SkillRequirement
from employee_insight.services.skill_service import SkillService


class TestSkillService(unittest.TestCase):
    def setUp(self) -> None:
        definitions = [
            SkillDefinition("S1", "Python", aliases=["python", "py"], cluster="编程"),
            SkillDefinition("S2", "机器学习", aliases=["ML", "machine learning"], cluster="AI"),
            SkillDefinition("S3", "SQL", aliases=[], cluster="数据"),
        ]
        self.service = SkillService(definitions)

    def test_resolve_by_alias(self) -> None:
        self.assertEqual(self.service.resolve_skill_id("machine learning"), "S2")
        self.assertEqual(self.service.resolve_skill_id("py"), "S1")

    def test_no_gap_when_covered(self) -> None:
        reqs = [SkillRequirement("S1", required_level=3)]
        owned = [EmployeeSkill("S1", level=4)]
        result = self.service.find_gaps(reqs, owned, "E1", "P1")
        self.assertEqual(result.gaps, [])
        self.assertAlmostEqual(result.overall_score, 1.0)

    def test_gap_detected(self) -> None:
        reqs = [SkillRequirement("S1", required_level=3), SkillRequirement("S3", required_level=2)]
        owned = [EmployeeSkill("S1", level=1)]
        result = self.service.find_gaps(reqs, owned, "E1", "P1")
        gap_ids = {g.skill_id for g in result.gaps}
        self.assertIn("S1", gap_ids)
        self.assertIn("S3", gap_ids)

    def test_coverage_partial(self) -> None:
        reqs = [SkillRequirement("S1", required_level=2)]
        owned = [EmployeeSkill("S1", level=1)]
        result = self.service.find_gaps(reqs, owned, "E1", "P1")
        self.assertAlmostEqual(result.overall_score, 0.5)


if __name__ == "__main__":
    unittest.main()
