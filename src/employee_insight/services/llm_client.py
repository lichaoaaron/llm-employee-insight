"""大模型客户端抽象。

把大模型调用封装成统一接口，业务代码只依赖 :class:`LLMClient`，
从而可以在「离线规则抽取」与「真实大模型」之间无缝切换：

- :class:`MockLLMClient`：基于规则的关键词抽取，无需联网与密钥，保证可离线运行；
- :class:`OpenAICompatibleClient`：对接任意 OpenAI 兼容接口，仅依赖标准库 urllib。
"""
from __future__ import annotations

import json
import urllib.request
from abc import ABC, abstractmethod
from typing import List, Optional


class LLMClient(ABC):
    """大模型客户端统一接口。"""

    @abstractmethod
    def extract_keywords(self, text: str, max_items: int = 8) -> List[str]:
        """从自由文本中抽取结构化关键词。"""

    @abstractmethod
    def summarize(self, text: str) -> str:
        """对文本生成一段简短摘要。"""


class MockLLMClient(LLMClient):
    """规则版客户端：按词频与命中词表抽取关键词，保证离线可用。"""

    # 常见技能/能力词表，用于规则抽取兜底。
    _SKILL_HINTS = (
        "python", "java", "go", "sql", "spark", "flink", "hadoop",
        "机器学习", "深度学习", "自然语言处理", "数据仓库", "风控",
        "招聘", "薪酬", "绩效", "培训", "组织发展", "项目管理",
    )

    def extract_keywords(self, text: str, max_items: int = 8) -> List[str]:
        lowered = text.lower()
        keywords: List[str] = []
        for hint in self._SKILL_HINTS:
            if hint in lowered:
                keywords.append(hint)
            if len(keywords) >= max_items:
                break
        return keywords

    def summarize(self, text: str) -> str:
        stripped = " ".join(text.split())
        if not stripped:
            return "暂无可用信息"
        return stripped[:120] + ("…" if len(stripped) > 120 else "")


class OpenAICompatibleClient(LLMClient):
    """OpenAI 兼容接口客户端（chat/completions），基于标准库 urllib 实现。"""

    def __init__(self, api_base: str, api_key: str, model: str) -> None:
        if not api_base or not api_key:
            raise ValueError("api_base 与 api_key 不能为空")
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model = model

    def _complete(self, system: str, user: str) -> str:
        url = f"{self.api_base}/chat/completions"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]

    def extract_keywords(self, text: str, max_items: int = 8) -> List[str]:
        system = "你是信息抽取助手，只输出 JSON 数组，不要输出其他内容。"
        user = f"请从以下文本抽取最多 {max_items} 个结构化关键词：\n{text}"
        raw = self._complete(system, user)
        try:
            items = json.loads(raw)
            return [str(i) for i in items][:max_items]
        except json.JSONDecodeError:
            return MockLLMClient().extract_keywords(text, max_items)

    def summarize(self, text: str) -> str:
        system = "你是摘要助手，用一句话概括员工信息。"
        return self._complete(system, text).strip()
