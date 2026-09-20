"""员工画像聚合服务。

把散落在原始记录里的字段（司龄、职级、技能、绩效等）聚合成一份结构化画像，
并借助 :class:`LLMClient` 从自由文本中补充结构化标签。
"""
from __future__ import annotations

from typing import List

from employee_insight.models.employee import Employee
from employee_insight.models.profile import EmployeeProfile
from employee_insight.services.llm_client import LLMClient


def _seniority_level(tenure_years: float, title: str) -> str:
    """根据司龄与职级粗略判断层级。"""
    title_lower = title.lower()
    if "首席" in title or "principal" in title_lower or "专家" in title:
        return "principal"
    if "资深" in title or "高级" in title or "senior" in title_lower or tenure_years >= 5:
        return "senior"
    if tenure_years >= 2:
        return "mid"
    return "junior"


class ProfileService:
    """负责员工画像的构建。"""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def build(self, employee: Employee) -> EmployeeProfile:
        """将单条员工记录构建为画像。"""
        skill_tags = [s.strip() for s in employee.skills if s.strip()]
        keywords = self.llm.extract_keywords(employee.resume_text)
        # 去重并保持顺序。
        merged_tags = list(dict.fromkeys(skill_tags + keywords))
        summary = self.llm.summarize(employee.resume_text) if employee.resume_text else "暂无补充说明"

        return EmployeeProfile(
            employee_id=employee.employee_id,
            name=employee.name,
            department=employee.department,
            seniority_level=_seniority_level(employee.tenure_years, employee.title),
            skill_tags=merged_tags,
            extracted_keywords=keywords,
            summary=summary,
        )

    def build_all(self, employees: List[Employee]) -> List[EmployeeProfile]:
        """批量构建画像。"""
        return [self.build(e) for e in employees]
