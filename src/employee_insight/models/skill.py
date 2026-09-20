"""技能体系数据模型。

定义技能、技能簇与技能等级，支撑技能匹配、缺口分析等能力。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SkillDefinition:
    """一条技能定义，构成企业技能字典。"""

    skill_id: str
    name: str
    aliases: List[str] = field(default_factory=list)
    cluster: str = "通用"
    description: str = ""

    def all_names(self) -> List[str]:
        """返回技能名及其所有别名。"""
        return [self.name, *self.aliases]

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "aliases": self.aliases,
            "cluster": self.cluster,
            "description": self.description,
        }


@dataclass
class SkillRequirement:
    """某个岗位对某项技能的要求。"""

    skill_id: str
    required_level: int = 1   # 1~5
    weight: float = 1.0       # 该技能在该岗位中的权重


@dataclass
class EmployeeSkill:
    """员工掌握的某项技能及其水平。"""

    skill_id: str
    level: int = 1            # 1~5


@dataclass
class SkillGap:
    """技能缺口：岗位要求与员工水平的差距。"""

    skill_id: str
    skill_name: str
    required_level: int
    current_level: int
    gap: int

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "required_level": self.required_level,
            "current_level": self.current_level,
            "gap": self.gap,
        }
