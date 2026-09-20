"""分析引擎编排器。

把画像、组织、离职风险、团队健康、部门对标、人员结构等多个分析服务
编排为一次完整的分析流程，输出统一的结构化报告。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from employee_insight.config import AppConfig
from employee_insight.models.employee import Employee
from employee_insight.services.benchmark_service import BenchmarkService
from employee_insight.services.demographics_service import DemographicsService
from employee_insight.services.llm_client import LLMClient, MockLLMClient
from employee_insight.services.org_analysis import OrgAnalysisService
from employee_insight.services.profile_service import ProfileService
from employee_insight.services.team_health_service import TeamHealthService
from employee_insight.services.turnover_risk import TurnoverRiskService


@dataclass
class AnalysisReport:
    """一次完整分析产出的综合报告。"""

    org: Dict[str, Any]
    risk: List[Dict[str, Any]]
    profiles: List[Dict[str, Any]]
    team_health: List[Dict[str, Any]]
    benchmark: List[Dict[str, Any]]
    demographics: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "org": self.org,
            "risk": self.risk,
            "profiles": self.profiles,
            "team_health": self.team_health,
            "benchmark": self.benchmark,
            "demographics": self.demographics,
        }


class AnalysisEngine:
    """员工信息分析编排引擎。"""

    def __init__(self, config: AppConfig, llm: LLMClient | None = None) -> None:
        self._config = config
        self._llm = llm or MockLLMClient()
        self._profile = ProfileService(self._llm)
        self._org = OrgAnalysisService()
        self._risk = TurnoverRiskService(config)
        self._team = TeamHealthService(self._risk)
        self._benchmark = BenchmarkService(self._risk)
        self._demographics = DemographicsService()

    def run(self, employees: List[Employee]) -> AnalysisReport:
        """执行完整分析流程。"""
        org = self._org.analyze(employees).to_dict()
        risk = [r.to_dict() for r in self._risk.evaluate(employees)]
        profiles = [p.to_dict() for p in self._profile.build_all(employees)]

        grouped: Dict[str, List[Employee]] = {}
        for emp in employees:
            grouped.setdefault(emp.department, []).append(emp)
        team_health = [self._team.evaluate(dept, members).to_dict() for dept, members in sorted(grouped.items())]

        benchmark = [m.to_dict() for m in self._benchmark.benchmark(employees)]
        demographics = self._demographics.analyze(employees).to_dict()

        return AnalysisReport(
            org=org,
            risk=risk,
            profiles=profiles,
            team_health=team_health,
            benchmark=benchmark,
            demographics=demographics,
        )
