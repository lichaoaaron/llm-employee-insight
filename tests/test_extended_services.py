"""职业规划、报告、导入、搜索、团队健康服务单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.config import AppConfig
from employee_insight.models.career import CareerPath
from employee_insight.models.employee import Employee
from employee_insight.services.career_service import CareerService
from employee_insight.services.importer import EmployeeImporter
from employee_insight.services.report_service import ReportService
from employee_insight.services.search_service import EmployeeQuery, EmployeeSearchService
from employee_insight.services.team_health_service import TeamHealthService
from employee_insight.services.turnover_risk import TurnoverRiskService


def _employee(**overrides) -> Employee:
    base = dict(
        employee_id="E1",
        name="张三",
        department="研发中心",
        title="工程师",
        tenure_years=3.0,
        performance_rating="A",
        overtime_hours_per_month=30,
        months_since_promotion=12,
        skills=["Python", "机器学习"],
    )
    base.update(overrides)
    return Employee(**base)


class TestCareerService(unittest.TestCase):
    def test_available_paths_filters(self) -> None:
        paths = [
            CareerPath("P1", "晋升", "工程师", "高级工程师", required_tenure_years=2.0, required_performance="B"),
            CareerPath("P2", "晋升", "工程师", "专家", required_tenure_years=10.0, required_performance="A"),
        ]
        service = CareerService(paths)
        emp = _employee(tenure_years=3.0, performance_rating="A")
        available = service.available_paths(emp, "工程师")
        self.assertEqual([p.path_id for p in available], ["P1"])

    def test_succession_rank_sorted(self) -> None:
        service = CareerService([])
        candidates = [
            _employee(employee_id="low", tenure_years=0.5, performance_rating="C", skills=[]),
            _employee(employee_id="high", tenure_years=8.0, performance_rating="S", skills=["Python"]),
        ]
        ranked = service.succession_rank(candidates, "P1", position_skill_ids=["Python"])
        self.assertEqual(ranked[0].employee_id, "high")


class TestImporter(unittest.TestCase):
    def test_import_valid_csv(self) -> None:
        csv_text = "员工编号,姓名,部门,岗位,司龄,绩效\nE1,张三,研发中心,工程师,3,A\n"
        result = EmployeeImporter().import_csv(csv_text)
        self.assertEqual(len(result.employees), 1)
        self.assertEqual(result.employees[0].employee_id, "E1")

    def test_import_missing_field(self) -> None:
        csv_text = "员工编号,姓名\nE1,张三\n"
        result = EmployeeImporter().import_csv(csv_text)
        self.assertEqual(len(result.employees), 0)
        self.assertTrue(any("必填字段" in e for e in result.errors))


class TestReportService(unittest.TestCase):
    def test_csv_columns(self) -> None:
        rows = [{"name": "张三", "score": 0.8}, {"name": "李四", "score": 0.5}]
        csv_text = ReportService().to_csv(rows)
        self.assertIn("name,score", csv_text)
        self.assertIn("张三", csv_text)

    def test_markdown_table(self) -> None:
        md = ReportService().to_markdown_table([{"a": "1", "b": "2"}])
        self.assertIn("| a | b |", md)

    def test_html_escape(self) -> None:
        html_text = ReportService().to_html_table([{"a": "<b>x</b>"}])
        self.assertIn("&lt;b&gt;", html_text)


class TestSearchService(unittest.TestCase):
    def test_filter_by_department(self) -> None:
        employees = [_employee(department="研发中心"), _employee(employee_id="E2", department="风控部")]
        result = EmployeeSearchService().filter(employees, EmployeeQuery(department="风控部"))
        self.assertEqual([e.employee_id for e in result], ["E2"])

    def test_keyword_search(self) -> None:
        employees = [_employee(name="张三"), _employee(employee_id="E2", name="李四", skills=["SQL"])]
        result = EmployeeSearchService().search_by_keyword(employees, "SQL", top_n=5)
        self.assertEqual(result[0].employee_id, "E2")


class TestTeamHealthService(unittest.TestCase):
    def test_healthy_team(self) -> None:
        risk_service = TurnoverRiskService(AppConfig())
        members = [_employee(tenure_years=6.0, performance_rating="S", overtime_hours_per_month=10)]
        report = TeamHealthService(risk_service).evaluate("研发中心", members)
        self.assertGreater(report.health_score, 0.5)

    def test_empty_team(self) -> None:
        report = TeamHealthService(TurnoverRiskService(AppConfig())).evaluate("空部门", [])
        self.assertEqual(report.headcount, 0)
        self.assertEqual(report.health_score, 0.0)


if __name__ == "__main__":
    unittest.main()
