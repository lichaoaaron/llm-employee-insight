"""培训发展数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class TrainingCourse:
    """一门培训课程。"""

    course_id: str
    name: str
    target_skill_ids: List[str] = field(default_factory=list)
    duration_hours: float = 0.0
    level: int = 1          # 适合的技能水平
    online: bool = True

    def to_dict(self) -> dict:
        return {
            "course_id": self.course_id,
            "name": self.name,
            "target_skill_ids": self.target_skill_ids,
            "duration_hours": self.duration_hours,
            "level": self.level,
            "online": self.online,
        }


@dataclass
class TrainingPlanItem:
    """培训计划中的一项：为某员工安排一门课程。"""

    employee_id: str
    course_id: str
    course_name: str
    reason: str            # 推荐原因

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "course_id": self.course_id,
            "course_name": self.course_name,
            "reason": self.reason,
        }
