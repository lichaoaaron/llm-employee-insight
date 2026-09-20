"""配置加载服务。

从 JSON 文件加载技能字典、职业发展路径、薪酬带宽等业务配置，
避免把这些结构化配置硬编码在代码里。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from employee_insight.models.career import CareerPath
from employee_insight.models.compensation import SalaryBand
from employee_insight.models.skill import SkillDefinition


class ConfigLoader:
    """业务配置加载器。"""

    @staticmethod
    def _read_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def load_skill_definitions(self, path: Path) -> List[SkillDefinition]:
        """加载技能字典。期望 JSON 结构：[{skill_id, name, aliases, cluster}]。"""
        raw = self._read_json(path)
        return [
            SkillDefinition(
                skill_id=item["skill_id"],
                name=item["name"],
                aliases=item.get("aliases", []),
                cluster=item.get("cluster", "通用"),
                description=item.get("description", ""),
            )
            for item in raw
        ]

    def load_career_paths(self, path: Path) -> List[CareerPath]:
        """加载职业发展路径。期望 JSON 结构：[{path_id, name, from_position_id, to_position_id, ...}]。"""
        raw = self._read_json(path)
        return [
            CareerPath(
                path_id=item["path_id"],
                name=item["name"],
                from_position_id=item["from_position_id"],
                to_position_id=item["to_position_id"],
                required_tenure_years=item.get("required_tenure_years", 2.0),
                required_performance=item.get("required_performance", "B"),
                required_skill_ids=item.get("required_skill_ids", []),
            )
            for item in raw
        ]

    def load_salary_bands(self, path: Path) -> List[SalaryBand]:
        """加载薪酬带宽。期望 JSON 结构：[{band_id, name, min_salary, mid_salary, max_salary}]。"""
        raw = self._read_json(path)
        return [
            SalaryBand(
                band_id=item["band_id"],
                name=item["name"],
                min_salary=item["min_salary"],
                mid_salary=item["mid_salary"],
                max_salary=item["max_salary"],
                position_ids=item.get("position_ids", []),
            )
            for item in raw
        ]
