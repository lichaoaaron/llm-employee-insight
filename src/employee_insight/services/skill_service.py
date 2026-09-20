"""技能分析服务。

基于企业技能字典，提供技能别名归一、岗位要求匹配、技能缺口分析等能力。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from employee_insight.models.skill import (
    EmployeeSkill,
    SkillDefinition,
    SkillGap,
    SkillRequirement,
)
from employee_insight.utils.text_utils import similarity


@dataclass
class SkillMatchResult:
    """技能匹配结果。"""

    employee_id: str
    position_id: str
    coverage: float             # 满足要求的技能占比（按权重）
    overall_score: float        # 综合匹配得分 0~1
    gaps: List[SkillGap] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "position_id": self.position_id,
            "coverage": round(self.coverage, 4),
            "overall_score": round(self.overall_score, 4),
            "gaps": [g.to_dict() for g in self.gaps],
        }


class SkillService:
    """技能字典与匹配服务。"""

    def __init__(self, definitions: List[SkillDefinition]) -> None:
        self._defs: Dict[str, SkillDefinition] = {d.skill_id: d for d in definitions}

    def resolve_skill_id(self, name: str) -> Optional[str]:
        """将技能名称（含别名）解析为规范 skill_id。"""
        for skill_id, definition in self._defs.items():
            for candidate in definition.all_names():
                if similarity(name, candidate) >= 0.85:
                    return skill_id
        return None

    def find_gaps(
        self,
        requirements: List[SkillRequirement],
        owned: List[EmployeeSkill],
        employee_id: str,
        position_id: str,
    ) -> SkillMatchResult:
        """计算员工相对某岗位要求的技能覆盖度与缺口。"""
        owned_map = {e.skill_id: e.level for e in owned}
        gaps: List[SkillGap] = []
        total_weight = 0.0
        covered_weight = 0.0
        score_sum = 0.0

        for req in requirements:
            definition = self._defs.get(req.skill_id)
            name = definition.name if definition else req.skill_id
            current = owned_map.get(req.skill_id, 0)
            total_weight += req.weight
            # 覆盖度：当前水平占要求水平的比例（封顶 1）。
            ratio = min(1.0, current / req.required_level) if req.required_level else 0.0
            covered_weight += req.weight * ratio
            score_sum += req.weight * ratio
            if current < req.required_level:
                gaps.append(
                    SkillGap(
                        skill_id=req.skill_id,
                        skill_name=name,
                        required_level=req.required_level,
                        current_level=current,
                        gap=req.required_level - current,
                    )
                )

        coverage = covered_weight / total_weight if total_weight else 0.0
        overall = score_sum / total_weight if total_weight else 0.0
        # 缺口按差距降序排列，方便优先补最短板。
        gaps.sort(key=lambda g: g.gap, reverse=True)
        return SkillMatchResult(
            employee_id=employee_id,
            position_id=position_id,
            coverage=coverage,
            overall_score=overall,
            gaps=gaps,
        )
