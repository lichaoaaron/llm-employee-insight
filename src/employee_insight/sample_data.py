"""示例数据生成器。

按参数生成具有一定结构特征的示例员工数据，用于功能演示与测试，
避免依赖真实敏感数据。
"""
from __future__ import annotations

import random
from typing import List, Optional

from employee_insight.models.employee import Employee

_DEPARTMENTS = ["研发中心", "产品部", "风控部", "人力资源部", "市场部", "财务部"]
_TITLES = ["初级工程师", "工程师", "高级工程师", "专家", "经理", "总监"]
_RATINGS = ["S", "A", "B", "C", "D"]
_SKILL_POOL = [
    "Python", "Java", "Go", "SQL", "Spark", "Flink",
    "机器学习", "深度学习", "自然语言处理", "风控", "招聘", "薪酬",
]
_NAMES = ["张伟", "李娜", "王强", "赵敏", "陈杰", "刘洋", "孙丽", "周涛", "吴敏", "郑浩"]


class SampleDataGenerator:
    """示例员工数据生成器。"""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def generate(self, count: int = 50) -> List[Employee]:
        """生成 count 条示例员工数据。"""
        employees: List[Employee] = []
        for i in range(1, count + 1):
            department = self._rng.choice(_DEPARTMENTS)
            title = self._rng.choice(_TITLES)
            rating = self._rng.choices(_RATINGS, weights=[5, 30, 40, 18, 7], k=1)[0]
            skills = self._rng.sample(_SKILL_POOL, k=self._rng.randint(1, 4))
            employees.append(
                Employee(
                    employee_id=f"E{i:04d}",
                    name=f"{self._rng.choice(_NAMES)}{i}",
                    department=department,
                    title=title,
                    tenure_years=round(self._rng.uniform(0.2, 12.0), 1),
                    performance_rating=rating,
                    overtime_hours_per_month=round(self._rng.uniform(0, 70), 1),
                    months_since_promotion=self._rng.randint(1, 48),
                    skills=skills,
                    resume_text=f"负责{department}相关工作，掌握{'、'.join(skills)}。",
                )
            )
        return employees
