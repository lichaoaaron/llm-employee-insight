"""全局配置模块。

集中管理系统运行参数，支持通过环境变量覆盖默认值，便于在本地开发与
生产环境之间切换，避免把密钥、阈值等硬编码进业务代码。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _as_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw not in (None, "") else default


def _as_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw not in (None, "") else default


@dataclass(frozen=True)
class AppConfig:
    """应用运行参数（不可变，按需从环境变量加载）。"""

    # 离职风险模型各因子的权重，总和约为 1.0。
    tenure_weight: float = field(default_factory=lambda: _as_float("EI_TENURE_WEIGHT", 0.25))
    performance_weight: float = field(default_factory=lambda: _as_float("EI_PERFORMANCE_WEIGHT", 0.30))
    overtime_weight: float = field(default_factory=lambda: _as_float("EI_OVERTIME_WEIGHT", 0.15))
    promotion_weight: float = field(default_factory=lambda: _as_float("EI_PROMOTION_WEIGHT", 0.15))
    skill_weight: float = field(default_factory=lambda: _as_float("EI_SKILL_WEIGHT", 0.15))

    # 风险等级阈值：score >= high 视为高风险，>= medium 视为中风险。
    high_risk_threshold: float = field(default_factory=lambda: _as_float("EI_HIGH_RISK", 0.65))
    medium_risk_threshold: float = field(default_factory=lambda: _as_float("EI_MEDIUM_RISK", 0.40))

    # 大模型接入：mock 表示使用内置规则抽取，openai_compatible 表示走兼容接口。
    llm_provider: str = os.getenv("EI_LLM_PROVIDER", "mock")
    llm_api_base: str = os.getenv("EI_LLM_API_BASE", "")
    llm_api_key: str = os.getenv("EI_LLM_API_KEY", "")
    llm_model: str = os.getenv("EI_LLM_MODEL", "gpt-4o-mini")

    # 数据目录。
    data_dir: Path = Path(os.getenv("EI_DATA_DIR", "data"))


def load_config() -> AppConfig:
    """构造应用配置。"""
    return AppConfig()
