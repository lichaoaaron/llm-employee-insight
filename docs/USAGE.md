# 使用指南

本文档介绍「基于大模型的员工信息智能分析与管理系统」命令行工具的使用方式。

## 快速开始

```bash
# 无需安装，以模块方式运行（需在项目根目录下）
PYTHONPATH=src python -m employee_insight --data data/sample_employees.json <子命令>
```

## 子命令

### profile — 构建员工画像

聚合每位员工的画像，输出层级、技能标签、抽取关键词与摘要。

```bash
python -m employee_insight --data data/sample_employees.json profile
```

### org — 组织分析

统计部门人数、平均司龄、资深人员占比。

```bash
python -m employee_insight --data data/sample_employees.json org
```

### risk — 离职风险排行

按五因子加权模型输出离职风险，降序排列并附触发原因。

```bash
python -m employee_insight --data data/sample_employees.json risk
```

### search — 检索 / 过滤员工

按条件过滤：

```bash
python -m employee_insight --data data/sample_employees.json search --department 研发中心 --min-tenure 3
```

按关键词模糊检索：

```bash
python -m employee_insight --data data/sample_employees.json search --keyword Python --top-n 5
```

### team-health — 团队健康评估

按部门输出健康分与改进建议。

```bash
python -m employee_insight --data data/sample_employees.json team-health
```

### report — 导出报告到标准输出

```bash
python -m employee_insight --data data/sample_employees.json report --format csv
python -m employee_insight --data data/sample_employees.json report --format html
```

### export — 导出报告到文件

```bash
python -m employee_insight --data data/sample_employees.json export --format csv --output risk.csv
python -m employee_insight --data data/sample_employees.json export --format html --output risk.html
```

### dashboard — 综合仪表盘

```bash
python -m employee_insight --data data/sample_employees.json dashboard
```

## 接入真实大模型

默认使用规则版客户端离线抽取关键词。如需接入大模型，设置以下环境变量：

```bash
export EI_LLM_PROVIDER=openai_compatible
export EI_LLM_API_BASE=https://your-endpoint
export EI_LLM_API_KEY=sk-xxx
export EI_LLM_MODEL=your-model
```

## 数据格式

员工数据为 JSON 数组，字段如下：

```json
[
  {
    "employee_id": "E1001",
    "name": "张伟",
    "department": "研发中心",
    "title": "高级算法工程师",
    "tenure_years": 6.5,
    "performance_rating": "A",
    "overtime_hours_per_month": 30,
    "months_since_promotion": 12,
    "skills": ["Python", "自然语言处理"],
    "resume_text": "负责自然语言处理方向研发……"
  }
]
```

同时支持 CSV 导入，表头可为中文（员工编号/姓名/部门/岗位/司龄/绩效/月加班时长/距晋升月数/技能/简历文本）。
