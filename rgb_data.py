"""读取 RGB 公开集（chen700564/RGB，CC BY-NC-SA 4.0，仅非商业使用）。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RGB_DIR = BASE_DIR / "data" / "rgb"


def flatten_docs(value) -> list[str]:
    out: list[str] = []
    if value is None:
        return out
    if isinstance(value, str):
        text = value.strip()
        if text:
            out.append(text)
        return out
    if isinstance(value, list):
        for item in value:
            out.extend(flatten_docs(item))
    return out


def doc_id(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def load_rgb_items(split: str = "zh_refine") -> list[dict]:
    path = RGB_DIR / f"{split}.json"
    if not path.exists():
        raise FileNotFoundError(f"找不到 RGB 数据：{path}")
    items: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        answers = obj.get("answer") or []
        if isinstance(answers, str):
            answers = [answers]
        items.append(
            {
                "id": obj.get("id"),
                "query": str(obj.get("query") or "").strip(),
                "answers": [str(a).strip() for a in answers if str(a).strip()],
                "positive": flatten_docs(obj.get("positive")),
                "negative": flatten_docs(obj.get("negative")),
            }
        )
    return items


def unique_docs(items: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for item in items:
        for text in item["positive"] + item["negative"]:
            did = doc_id(text)
            if did in seen:
                continue
            title = text.replace("\n", " ").strip()[:28]
            seen[did] = {"id": did, "title": title or did, "text": text}
    return list(seen.values())


def find_item_by_query(items: list[dict], query: str) -> dict | None:
    needle = query.strip()
    for item in items:
        if item["query"] == needle:
            return item
    return None
