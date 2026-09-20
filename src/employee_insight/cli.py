"""命令行入口。

提供三个子命令：
- profile：构建员工画像；
- org：输出组织分析报告；
- risk：输出离职风险排行。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from employee_insight.config import load_config
from employee_insight.data_loader import load_employees
from employee_insight.models.employee import Employee
from employee_insight.services.llm_client import MockLLMClient, OpenAICompatibleClient
from employee_insight.services.org_analysis import OrgAnalysisService
from employee_insight.services.profile_service import ProfileService
from employee_insight.services.turnover_risk import TurnoverRiskService


def _build_llm(config):
    if config.llm_provider == "openai_compatible":
        return OpenAICompatibleClient(config.llm_api_base, config.llm_api_key, config.llm_model)
    return MockLLMClient()


def _load_data(data_path: Path) -> List[Employee]:
    if not data_path.exists():
        print(f"数据文件不存在：{data_path}", file=sys.stderr)
        sys.exit(1)
    return load_employees(data_path)


def _print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_profile(args, config) -> None:
    employees = _load_data(args.data)
    service = ProfileService(_build_llm(config))
    profiles = service.build_all(employees)
    _print_json([p.to_dict() for p in profiles])


def cmd_org(args, config) -> None:
    employees = _load_data(args.data)
    report = OrgAnalysisService().analyze(employees)
    _print_json(report.to_dict())


def cmd_risk(args, config) -> None:
    employees = _load_data(args.data)
    results = TurnoverRiskService(config).evaluate(employees)
    _print_json([r.to_dict() for r in results])


def main(argv: List[str] | None = None) -> None:
    config = load_config()
    parser = argparse.ArgumentParser(prog="employee-insight", description="员工信息智能分析与管理系统")
    parser.add_argument("--data", type=Path, default=config.data_dir / "sample_employees.json", help="员工数据 JSON 路径")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("profile", help="构建员工画像").set_defaults(func=cmd_profile)
    sub.add_parser("org", help="组织分析").set_defaults(func=cmd_org)
    sub.add_parser("risk", help="离职风险排行").set_defaults(func=cmd_risk)

    args = parser.parse_args(argv)
    args.func(args, config)


if __name__ == "__main__":
    main()
