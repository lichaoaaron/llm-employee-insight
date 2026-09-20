"""组织架构数据模型。

描述公司—部门—团队的树状层级，以及员工在组织中的归属关系，
供组织分析、团队健康评估等服务使用。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Department:
    """部门节点。"""

    department_id: str
    name: str
    parent_id: Optional[str] = None
    manager_employee_id: Optional[str] = None
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "department_id": self.department_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "manager_employee_id": self.manager_employee_id,
            "description": self.description,
        }


@dataclass
class Team:
    """团队节点，挂在部门之下。"""

    team_id: str
    name: str
    department_id: str
    leader_employee_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "team_id": self.team_id,
            "name": self.name,
            "department_id": self.department_id,
            "leader_employee_id": self.leader_employee_id,
        }


@dataclass
class OrganizationTree:
    """组织树：维护部门与团队集合，并提供层级查询。"""

    departments: List[Department] = field(default_factory=list)
    teams: List[Team] = field(default_factory=list)
    _dept_by_id: Dict[str, Department] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self._dept_by_id = {d.department_id: d for d in self.departments}

    def children_of(self, department_id: str) -> List[Department]:
        """返回指定部门的直接子部门。"""
        return [d for d in self.departments if d.parent_id == department_id]

    def teams_of(self, department_id: str) -> List[Team]:
        """返回指定部门下的团队。"""
        return [t for t in self.teams if t.department_id == department_id]

    def ancestors(self, department_id: str) -> List[str]:
        """返回部门的自下而上的祖先链（不含自身），如 [父, 祖父, ...]。"""
        chain: List[str] = []
        current = self._dept_by_id.get(department_id)
        while current is not None and current.parent_id:
            chain.append(current.parent_id)
            current = self._dept_by_id.get(current.parent_id)
        return chain

    def is_descendant_of(self, department_id: str, ancestor_id: str) -> bool:
        """判断 department_id 是否位于 ancestor_id 的子树中。"""
        return ancestor_id in self.ancestors(department_id)
