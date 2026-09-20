"""薪酬、对标、人员结构服务单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.config import AppConfig
from employee_insight.models.compensation import EmployeeSalary, SalaryBand
from employee_insight.models.employee import Employee
from employee_insight.services.benchmark_service import BenchmarkService
from employee_insight.services.compensation_service import CompensationService
from employee_insight.services.demographics_service import DemographicsService
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
        skills=["Python"],
    )
    base.update(overrides)
    return Employee(**base)


class TestCompensationService(unittest.TestCase):
    def setUp(self) -> None:
        self.bands = [SalaryBand("B1", "初级", 10000, 15000, 20000)]
        self.service = CompensationService(self.bands)

    def test_compa_ratio(self) -> None:
        salaries = [EmployeeSalary("E1", base_salary=15000, band_id="B1")]
        report = self.service.analyze(salaries)
        self.assertEqual(report.total, 1)
        self.assertAlmostEqual(report.results[0].compa_ratio, 1.0)

    def test_below_range(self) -> None:
        salaries = [EmployeeSalary("E1", base_salary=8000, band_id="B1")]
        report = self.service.analyze(salaries)
        self.assertTrue(report.results[0].below_range)

    def test_ignore_unknown_band(self) -> None:
        salaries = [EmployeeSalary("E1", base_salary=15000, band_id="NOPE")]
        report = self.service.analyze(salaries)
        self.assertEqual(report.total, 0)


class TestBenchmarkService(unittest.TestCase):
    def test_benchmark_sorted(self) -> None:
        employees = [
            _employee(employee_id="low", department="稳定部", tenure_years=8.0, performance_rating="S"),
            _employee(employee_id="high", department="风险部", tenure_years=0.2, performance_rating="D"),
        ]
        metrics = BenchmarkService(TurnoverRiskService(AppConfig())).benchmark(employees)
        self.assertEqual(metrics[0].department, "风险部")


class TestDemographicsService(unittest.TestCase):
    def test_distributions(self) -> None:
        employees = [
            _employee(tenure_years=0.5, performance_rating="A"),
            _employee(employee_id="E2", tenure_years=6.0, performance_rating="B"),
        ]
        report = DemographicsService().analyze(employees)
        self.assertEqual(report.total, 2)
        self.assertEqual(report.tenure_distribution["0-1年"], 1)
        self.assertEqual(report.rating_distribution["A"], 1)


if __name__ == "__main__":
    unittest.main()
