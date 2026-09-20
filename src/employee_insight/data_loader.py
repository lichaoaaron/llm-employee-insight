"""示例数据加载器。

从 JSON 文件读取员工原始记录并转换为 :class:`Employee` 列表。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from employee_insight.models.employee import Employee


def load_employees(path: Path) -> List[Employee]:
    """从 JSON 文件加载员工列表。"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    employees: List[Employee] = []
    for item in raw:
        employees.append(
            Employee(
                employee_id=item["employee_id"],
                name=item["name"],
                department=item["department"],
                title=item["title"],
                tenure_years=float(item["tenure_years"]),
                performance_rating=item["performance_rating"],
                overtime_hours_per_month=float(item["overtime_hours_per_month"]),
                months_since_promotion=int(item["months_since_promotion"]),
                skills=item.get("skills", []),
                resume_text=item.get("resume_text", ""),
            )
        )
    return employees
