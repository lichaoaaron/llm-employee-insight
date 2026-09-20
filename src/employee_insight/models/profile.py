"""员工画像数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class EmployeeProfile:
    """由原始员工记录聚合出的画像结果。"""

    employee_id: str
    name: str
    department: str
    seniority_level: str          # junior / mid / senior / principal
    skill_tags: List[str] = field(default_factory=list)
    extracted_keywords: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        """转成可序列化的字典，便于 CLI 输出 JSON。"""
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "department": self.department,
            "seniority_level": self.seniority_level,
            "skill_tags": self.skill_tags,
            "extracted_keywords": self.extracted_keywords,
            "summary": self.summary,
        }
