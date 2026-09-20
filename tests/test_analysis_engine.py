"""分析引擎、配置加载、摘要服务单元测试。"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from employee_insight.config import AppConfig
from employee_insight.models.employee import Employee
from employee_insight.services.analysis_engine import AnalysisEngine
from employee_insight.services.config_loader import ConfigLoader
from employee_insight.services.summary_service import SummaryService
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


class TestAnalysisEngine(unittest.TestCase):
    def test_run_produces_report(self) -> None:
        report = AnalysisEngine(AppConfig()).run([_employee()])
        data = report.to_dict()
        self.assertIn("org", data)
        self.assertIn("risk", data)
        self.assertIn("profiles", data)
        self.assertIn("team_health", data)
        self.assertIn("benchmark", data)
        self.assertIn("demographics", data)


class TestConfigLoader(unittest.TestCase):
    def test_load_skill_definitions(self) -> None:
        raw = [{"skill_id": "S1", "name": "Python", "aliases": ["py"], "cluster": "编程"}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False)
            path = Path(f.name)
        try:
            defs = ConfigLoader().load_skill_definitions(path)
            self.assertEqual(defs[0].skill_id, "S1")
            self.assertEqual(defs[0].aliases, ["py"])
        finally:
            path.unlink()

    def test_load_salary_bands(self) -> None:
        raw = [{"band_id": "B1", "name": "初级", "min_salary": 1, "mid_salary": 2, "max_salary": 3}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False)
            path = Path(f.name)
        try:
            bands = ConfigLoader().load_salary_bands(path)
            self.assertEqual(bands[0].mid_salary, 2)
        finally:
            path.unlink()


class TestSummaryService(unittest.TestCase):
    def test_summarize_risk(self) -> None:
        results = TurnoverRiskService(AppConfig()).evaluate([_employee()])
        text = SummaryService().summarize_risk(results)
        self.assertIn("离职风险", text)

    def test_summarize_org(self) -> None:
        text = SummaryService().summarize_org({"total_headcount": 10, "department_count": 3})
        self.assertIn("10", text)


if __name__ == "__main__":
    unittest.main()
