"""命令行入口。

提供以下子命令：
- profile：构建员工画像；
- org：输出组织分析报告；
- risk：输出离职风险排行；
- search：按条件过滤或关键词检索员工；
- team-health：输出部门维度的团队健康评估；
- report：将风险结果导出为 CSV / Markdown / HTML 报告。
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
from employee_insight.services.report_service import ReportService
from employee_insight.services.search_service import EmployeeQuery, EmployeeSearchService
from employee_insight.services.team_health_service import TeamHealthService
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


def _group_by_department(employees: List[Employee]) -> dict[str, List[Employee]]:
    grouped: dict[str, List[Employee]] = {}
    for emp in employees:
        grouped.setdefault(emp.department, []).append(emp)
    return grouped


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


def cmd_search(args, config) -> None:
    employees = _load_data(args.data)
    service = EmployeeSearchService()
    if args.keyword:
        matched = service.search_by_keyword(employees, args.keyword, top_n=args.top_n)
    else:
        query = EmployeeQuery(
            department=args.department,
            title_keyword=args.title,
            min_tenure=args.min_tenure,
            performance_rating=args.rating,
            required_skill=args.skill,
            max_overtime=args.max_overtime,
        )
        matched = service.filter(employees, query)
    _print_json(
        [{"employee_id": e.employee_id, "name": e.name, "department": e.department, "title": e.title} for e in matched]
    )


def cmd_team_health(args, config) -> None:
    employees = _load_data(args.data)
    risk_service = TurnoverRiskService(config)
    service = TeamHealthService(risk_service)
    reports = [service.evaluate(dept, members).to_dict() for dept, members in sorted(_group_by_department(employees).items())]
    _print_json(reports)


def cmd_report(args, config) -> None:
    employees = _load_data(args.data)
    risk_service = TurnoverRiskService(config)
    rows = [r.to_dict() for r in risk_service.evaluate(employees)]
    report = ReportService()
    if args.format == "csv":
        print(report.to_csv(rows))
    elif args.format == "markdown":
        print(report.to_markdown_table(rows))
    elif args.format == "html":
        print(report.to_html_page("离职风险报告", [{"heading": "风险排行", "rows": rows}]))
    else:
        _print_json(rows)


def main(argv: List[str] | None = None) -> None:
    config = load_config()
    parser = argparse.ArgumentParser(prog="employee-insight", description="员工信息智能分析与管理系统")
    parser.add_argument("--data", type=Path, default=config.data_dir / "sample_employees.json", help="员工数据 JSON 路径")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("profile", help="构建员工画像").set_defaults(func=cmd_profile)
    sub.add_parser("org", help="组织分析").set_defaults(func=cmd_org)
    sub.add_parser("risk", help="离职风险排行").set_defaults(func=cmd_risk)

    search = sub.add_parser("search", help="按条件过滤或关键词检索员工")
    search.add_argument("--keyword", help="模糊检索关键词")
    search.add_argument("--department", help="按部门过滤")
    search.add_argument("--title", help="按岗位关键词过滤")
    search.add_argument("--min-tenure", type=float, help="最小司龄")
    search.add_argument("--rating", help="绩效评级（S/A/B/C/D）")
    search.add_argument("--skill", help="要求具备的技能")
    search.add_argument("--max-overtime", type=float, help="最大月加班时长")
    search.add_argument("--top-n", type=int, default=10, help="关键词检索返回条数")
    search.set_defaults(func=cmd_search)

    sub.add_parser("team-health", help="团队健康评估").set_defaults(func=cmd_team_health)

    report = sub.add_parser("report", help="导出报告")
    report.add_argument("--format", choices=["json", "csv", "markdown", "html"], default="json")
    report.set_defaults(func=cmd_report)

    args = parser.parse_args(argv)
    args.func(args, config)


if __name__ == "__main__":
    main()
