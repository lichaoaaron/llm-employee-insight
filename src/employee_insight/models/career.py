"""职业发展数据模型。

定义职业发展路径、岗位任职要求与继任候选，支撑职业规划与继任计划能力。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Position:
    """岗位定义。"""

    position_id: str
    name: str
    level: int = 1            # 职级
    department_id: str = ""


@dataclass
class CareerPath:
    """职业发展路径：描述从一个岗位到下一个岗位的晋升/转岗关系。"""

    path_id: str
    name: str
    from_position_id: str
    to_position_id: str
    required_tenure_years: float = 2.0
    required_performance: str = "B"  # 最低绩效要求
    required_skill_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path_id": self.path_id,
            "name": self.name,
            "from_position_id": self.from_position_id,
            "to_position_id": self.to_position_id,
            "required_tenure_years": self.required_tenure_years,
            "required_performance": self.required_performance,
            "required_skill_ids": self.required_skill_ids,
        }


@dataclass
class SuccessionCandidate:
    """继任候选人评估结果。"""

    employee_id: str
    name: str
    position_id: str
    readiness_score: float      # 0~1，越大越成熟
    level: str                  # ready / developing / future
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "position_id": self.position_id,
            "readiness_score": round(self.readiness_score, 4),
            "level": self.level,
            "strengths": self.strengths,
            "gaps": self.gaps,
        }
