"""员工数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Employee:
    """一条员工记录，对应数据源中的一行。

    字段语义：
    - performance_rating: 绩效评级，取值 S / A / B / C / D。
    - months_since_promotion: 距上次晋升/调岗的月数。
    - resume_text: 简历、绩效评语等自由文本，供 LLM 抽取结构化信息。
    """

    employee_id: str
    name: str
    department: str
    title: str
    tenure_years: float
    performance_rating: str
    overtime_hours_per_month: float
    months_since_promotion: int
    skills: List[str] = field(default_factory=list)
    resume_text: str = ""

    def __post_init__(self) -> None:
        if self.tenure_years < 0:
            raise ValueError("tenure_years 不能为负")
        if self.overtime_hours_per_month < 0:
            raise ValueError("overtime_hours_per_month 不能为负")
        if self.months_since_promotion < 0:
            raise ValueError("months_since_promotion 不能为负")
