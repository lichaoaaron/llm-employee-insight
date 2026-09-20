"""培训推荐服务。

根据技能缺口为员工匹配合适的培训课程，生成培训计划。
"""
from __future__ import annotations

from typing import List

from employee_insight.models.skill import EmployeeSkill, SkillGap, SkillRequirement
from employee_insight.models.training import TrainingCourse, TrainingPlanItem
from employee_insight.services.skill_service import SkillService


class TrainingRecommendationService:
    """培训推荐服务。"""

    def __init__(self, skill_service: SkillService, courses: List[TrainingCourse]) -> None:
        self._skill_service = skill_service
        self._courses = courses

    def recommend(
        self,
        employee_id: str,
        requirements: List[SkillRequirement],
        owned: List[EmployeeSkill],
        position_id: str,
    ) -> List[TrainingPlanItem]:
        """根据技能缺口推荐课程，返回培训计划项列表。"""
        match = self._skill_service.find_gaps(requirements, owned, employee_id, position_id)
        gap_skill_ids = {g.skill_id for g in match.gaps}

        plan: List[TrainingPlanItem] = []
        for course in self._courses:
            if not (set(course.target_skill_ids) & gap_skill_ids):
                continue
            plan.append(
                TrainingPlanItem(
                    employee_id=employee_id,
                    course_id=course.course_id,
                    course_name=course.name,
                    reason=self._reason(course, match.gaps),
                )
            )
        # 优先推荐能补齐最严重缺口的课程。
        plan.sort(key=lambda item: item.course_name)
        return plan

    @staticmethod
    def _reason(course: TrainingCourse, gaps: List[SkillGap]) -> str:
        """生成推荐原因文案。"""
        names = [g.skill_name for g in gaps if g.skill_id in course.target_skill_ids]
        if not names:
            return "补充岗位相关技能"
        return "补充技能缺口：" + "、".join(names)
