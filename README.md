# 基于大语言模型的员工信息智能分析与管理系统

面向人力资源管理场景，提供员工画像聚合、自由文本结构化抽取、组织分析与离职
风险评估能力。核心业务逻辑仅依赖 Python 标准库，可离线运行；大模型调用通过
可插拔客户端接入，默认使用内置规则抽取兜底。

## 功能特性

- **员工画像聚合**：将司龄、职级、技能、绩效等散落字段聚合成结构化画像。
- **自由文本结构化抽取**：从简历/绩效评语中抽取技能关键词，支持接入真实 LLM。
- **组织分析**：部门分布、平均司龄、资深人员占比等组织健康指标。
- **离职风险评估**：多维因子加权打分，输出风险等级与触发原因。

## 快速开始

```bash
# 安装（可选，直接以模块方式运行亦可）
pip install -e .

# 构建员工画像
python -m employee_insight --data data/sample_employees.json profile

# 组织分析
python -m employee_insight --data data/sample_employees.json org

# 离职风险排行
python -m employee_insight --data data/sample_employees.json risk
```

## 接入真实大模型

设置环境变量后即可切换到 OpenAI 兼容接口：

```bash
export EI_LLM_PROVIDER=openai_compatible
export EI_LLM_API_BASE=https://your-endpoint
export EI_LLM_API_KEY=sk-xxx
export EI_LLM_MODEL=your-model
```

## 目录结构

```
employee-insight-system/
├── src/employee_insight/
│   ├── models/          # 数据模型
│   ├── services/        # 业务服务（画像、组织分析、离职风险、LLM 客户端）
│   ├── cli.py           # 命令行入口
│   ├── config.py        # 配置
│   └── data_loader.py   # 数据加载
├── data/                # 示例数据
└── tests/               # 单元测试
```

## 运行测试

```bash
python -m unittest discover -s tests
```
