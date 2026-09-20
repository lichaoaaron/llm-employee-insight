"""数据导入服务。

支持从 CSV 文件导入员工数据，包含字段校验与类型转换，返回 Employee 列表
及导入过程中的错误信息。
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from employee_insight.models.employee import Employee


@dataclass
class ImportResult:
    """导入结果。"""

    employees: List[Employee] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_rows: int = 0

    def to_dict(self) -> dict:
        return {
            "imported": len(self.employees),
            "errors": self.errors,
            "total_rows": self.total_rows,
        }


class EmployeeImporter:
    """员工数据 CSV 导入器。"""

    REQUIRED_FIELDS = {"employee_id", "name", "department", "title"}

    def __init__(self) -> None:
        self._column_map: Dict[str, str] = {
            "员工编号": "employee_id",
            "姓名": "name",
            "部门": "department",
            "岗位": "title",
            "司龄": "tenure_years",
            "绩效": "performance_rating",
            "月加班时长": "overtime_hours_per_month",
            "距晋升月数": "months_since_promotion",
            "技能": "skills",
            "简历文本": "resume_text",
        }

    def import_csv(self, text: str) -> ImportResult:
        """从 CSV 文本导入员工数据。"""
        result = ImportResult()
        reader = csv.DictReader(io_csv_lines(text))
        if not reader.fieldnames:
            result.errors.append("CSV 缺少表头")
            return result

        for row_index, raw_row in enumerate(reader, start=2):
            result.total_rows += 1
            row = {self._column_map.get(k, k): v for k, v in raw_row.items() if k}
            employee, error = self._parse_row(row, row_index)
            if error:
                result.errors.append(error)
            else:
                result.employees.append(employee)
        return result

    def _parse_row(self, row: Dict[str, str], row_index: int) -> tuple[Optional[Employee], str]:
        missing = [f for f in self.REQUIRED_FIELDS if not (row.get(f) or "").strip()]
        if missing:
            return None, f"第 {row_index} 行缺少必填字段：{', '.join(missing)}"

        try:
            tenure = float(row.get("tenure_years") or 0)
            overtime = float(row.get("overtime_hours_per_month") or 0)
            months = int(float(row.get("months_since_promotion") or 0))
            skills = [s.strip() for s in (row.get("skills") or "").split(";") if s.strip()]
            employee = Employee(
                employee_id=row["employee_id"].strip(),
                name=row["name"].strip(),
                department=row["department"].strip(),
                title=row["title"].strip(),
                tenure_years=tenure,
                performance_rating=(row.get("performance_rating") or "B").strip().upper(),
                overtime_hours_per_month=overtime,
                months_since_promotion=months,
                skills=skills,
                resume_text=row.get("resume_text", "").strip(),
            )
            return employee, ""
        except (ValueError, TypeError) as exc:
            return None, f"第 {row_index} 行字段类型错误：{exc}"


def io_csv_lines(text: str) -> list[str]:
    """把 CSV 文本按行拆分，兼容 Windows 换行。"""
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
