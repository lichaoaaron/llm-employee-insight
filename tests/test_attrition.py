"""流失预测模型与示例数据生成器单元测试。"""
from __future__ import annotations

import unittest

from employee_insight.models.employee import Employee
from employee_insight.sample_data import SampleDataGenerator
from employee_insight.services.attrition_model import AttritionModel


def _employee(**overrides) -> Employee:
    base = dict(
        employee_id="E1",
        name="张三",
        department="研发中心",
        title="工程师",
        tenure_years=3.0,
        performance_rating="A",
        overtime_hours_per_month=30,
        months_since_promotion=12,
        skills=["Python"],
    )
    base.update(overrides)
    return Employee(**base)


class TestAttritionModel(unittest.TestCase):
    def test_probability_in_range(self) -> None:
        result = AttritionModel().predict([_employee()])[0]
        self.assertGreaterEqual(result.probability, 0.0)
        self.assertLessEqual(result.probability, 1.0)

    def test_new_hire_high_risk(self) -> None:
        model = AttritionModel()
        result = model.predict(
            [_employee(tenure_years=0.2, performance_rating="D", overtime_hours_per_month=60, skills=[])]
        )[0]
        self.assertEqual(result.tier, "high")

    def test_cohort_risk(self) -> None:
        model = AttritionModel()
        predictions = model.predict([_employee(), _employee(employee_id="E2", performance_rating="S")])
        cohort = model.cohort_risk(predictions)
        self.assertIn("avg_probability", cohort)
        self.assertIn("high_risk_count", cohort)


class TestSampleDataGenerator(unittest.TestCase):
    def test_generate_count(self) -> None:
        data = SampleDataGenerator(seed=42).generate(20)
        self.assertEqual(len(data), 20)
        self.assertTrue(all(e.employee_id for e in data))

    def test_deterministic(self) -> None:
        a = SampleDataGenerator(seed=1).generate(10)
        b = SampleDataGenerator(seed=1).generate(10)
        self.assertEqual([e.employee_id for e in a], [e.employee_id for e in b])


if __name__ == "__main__":
    unittest.main()
