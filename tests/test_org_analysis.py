"""组织分析服务单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.models.employee import Employee
from employee_insight.services.org_analysis import OrgAnalysisService


def _employee(emp_id: str, dept: str, tenure: float) -> Employee:
    return Employee(
        employee_id=emp_id,
        name="测试",
        department=dept,
        title="工程师",
        tenure_years=tenure,
        performance_rating="B",
        overtime_hours_per_month=30,
        months_since_promotion=12,
    )


class TestOrgAnalysisService(unittest.TestCase):
    def test_department_distribution(self) -> None:
        employees = [
            _employee("1", "研发中心", 6.0),
            _employee("2", "研发中心", 4.0),
            _employee("3", "风控部", 8.0),
        ]
        report = OrgAnalysisService().analyze(employees)
        self.assertEqual(report.total_headcount, 3)
        self.assertEqual(report.department_count, 2)

    def test_avg_tenure(self) -> None:
        employees = [
            _employee("1", "研发中心", 6.0),
            _employee("2", "研发中心", 4.0),
        ]
        report = OrgAnalysisService().analyze(employees)
        dept = report.dept_stats[0]
        self.assertAlmostEqual(dept.avg_tenure, 5.0)

    def test_senior_count(self) -> None:
        employees = [
            _employee("1", "研发中心", 6.0),
            _employee("2", "研发中心", 2.0),
        ]
        report = OrgAnalysisService().analyze(employees)
        self.assertEqual(report.dept_stats[0].senior_count, 1)


if __name__ == "__main__":
    unittest.main()
