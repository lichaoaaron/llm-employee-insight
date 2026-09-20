"""LLM 摘要服务。

利用大模型把结构化分析结果转化为自然语言摘要，输出可供管理层直接阅读的
文字结论。无模型时回退到规则模板。
"""
from __future__ import annotations

from typing import List

from employee_insight.services.llm_client import LLMClient, MockLLMClient
from employee_insight.services.turnover_risk import RiskResult


class SummaryService:
    """分析结果自然语言摘要生成器。"""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or MockLLMClient()

    def summarize_risk(self, results: List[RiskResult]) -> str:
        """把离职风险排行概括成一段文字。"""
        high = [r for r in results if r.level == "high"]
        medium = [r for r in results if r.level == "medium"]

        text = (
            f"离职风险分析结果：总人数 {len(results)}，"
            f"高风险 {len(high)} 人，中风险 {len(medium)} 人。"
        )
        high_names = "、".join(r.name for r in high[:5])
        if high_names:
            text += f"高风险员工包括：{high_names}。"
        return self._llm.summarize(text)

    def summarize_org(self, org_dict: dict) -> str:
        """把组织分析结果概括成一段文字。"""
        total = org_dict.get("total_headcount", 0)
        dept_count = org_dict.get("department_count", 0)
        text = f"组织共有 {total} 名员工、{dept_count} 个部门。"
        return self._llm.summarize(text)
