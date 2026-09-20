"""报告生成服务。

将分析结果输出为 JSON、CSV、Markdown、HTML 多种格式，
便于归档、下载与二次处理。
"""
from __future__ import annotations

import csv
import html
import io
import json
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Sequence


class ReportService:
    """多格式报告生成器。"""

    def __init__(self) -> None:
        self._indent = 2

    def to_json(self, payload: Any) -> str:
        """序列化为 JSON 字符串。"""
        return json.dumps(self._coerce(payload), ensure_ascii=False, indent=self._indent)

    def to_csv(self, rows: Sequence[Dict[str, Any]]) -> str:
        """将字典列表转换为 CSV 文本。"""
        if not rows:
            return ""
        columns = self._collect_columns(rows)
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: self._cell(row.get(k)) for k in columns})
        return buffer.getvalue()

    def to_markdown_table(self, rows: Sequence[Dict[str, Any]]) -> str:
        """将字典列表渲染为 Markdown 表格。"""
        if not rows:
            return ""
        columns = self._collect_columns(rows)
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join("---" for _ in columns) + " |"
        body = [
            "| " + " | ".join(self._cell(r.get(c)) for c in columns) + " |"
            for r in rows
        ]
        return "\n".join([header, separator, *body])

    def to_html_table(self, rows: Sequence[Dict[str, Any]]) -> str:
        """将字典列表渲染为 HTML 表格。"""
        if not rows:
            return ""
        columns = self._collect_columns(rows)
        head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
        body_rows = [
            "<tr>" + "".join(f"<td>{html.escape(self._cell(r.get(c)))}</td>" for c in columns) + "</tr>"
            for r in rows
        ]
        return (
            "<table border='1' cellspacing='0' cellpadding='4'>"
            f"<thead><tr>{head}</tr></thead>"
            f"<tbody>{''.join(body_rows)}</tbody></table>"
        )

    def to_html_page(self, title: str, sections: List[Dict[str, Any]]) -> str:
        """生成一个包含标题与若干表格区块的完整 HTML 页面。"""
        blocks = [f"<h1>{html.escape(title)}</h1>"]
        for section in sections:
            heading = section.get("heading", "")
            rows = section.get("rows", [])
            if heading:
                blocks.append(f"<h2>{html.escape(heading)}</h2>")
            if rows:
                blocks.append(self.to_html_table(rows))
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title></head><body>"
            + "".join(blocks)
            + "</body></html>"
        )

    @staticmethod
    def _coerce(value: Any) -> Any:
        """递归把 dataclass 转换为普通 dict。"""
        if is_dataclass(value):
            return {k: ReportService._coerce(v) for k, v in asdict(value).items()}
        if isinstance(value, (list, tuple)):
            return [ReportService._coerce(v) for v in value]
        if isinstance(value, dict):
            return {k: ReportService._coerce(v) for k, v in value.items()}
        return value

    @staticmethod
    def _collect_columns(rows: Sequence[Dict[str, Any]]) -> List[str]:
        seen: List[str] = []
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.append(key)
        return seen

    @staticmethod
    def _cell(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
