"""五个受控工具：文档检索、相似故障、历史运行、版本对比、回归保存。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.tools import tool

from retriever import retrieve

BASE_DIR = Path(__file__).resolve().parent
TRACE_PATH = BASE_DIR / "traces" / "ask.jsonl"
EVAL_DIR = BASE_DIR / "data" / "eval"
REGRESSION_PATH = EVAL_DIR / "regressions.jsonl"


def _clip(hits: list[dict], limit: int = 5) -> list[dict]:
    return [
        {
            "id": item["id"],
            "title": item["title"],
            "text": item["text"][:500],
            "score": item.get("score", 0),
        }
        for item in hits[:limit]
    ]


def build_tools(corpus: str = "rgb") -> tuple[list, list]:
    collected: list[dict] = []

    @tool
    def search_docs(query: str, k: int = 5) -> str:
        """检索知识库文档，回答事实类或文档问答时优先使用。"""
        hits, _ = retrieve(query, k=max(1, min(k, 8)), corpus=corpus, mode="hybrid")
        slim = _clip(hits)
        collected.extend(slim)
        return json.dumps(slim, ensure_ascii=False)

    @tool
    def similar_incidents(query: str, k: int = 5) -> str:
        """查找相似故障或同类问题记录，适合串话、超时、工具失败等排查。"""
        hits, _ = retrieve(query, k=max(1, min(k, 8)), corpus="kb", mode="hybrid")
        slim = _clip(hits)
        collected.extend(slim)
        return json.dumps(slim, ensure_ascii=False)

    @tool
    def run_history(limit: int = 5) -> str:
        """查看最近问答运行记录，包括耗时、工具和证据编号。"""
        if not TRACE_PATH.exists():
            return json.dumps({"runs": []}, ensure_ascii=False)
        lines = [line for line in TRACE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = []
        for line in lines[-max(1, min(limit, 20)) :]:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append(
                {
                    "ts": item.get("ts"),
                    "question": (item.get("question") or "")[:80],
                    "tools": item.get("tools") or [],
                    "latency_ms": item.get("latency_ms"),
                    "source_ids": item.get("source_ids") or [],
                }
            )
        return json.dumps({"runs": rows}, ensure_ascii=False)

    @tool
    def compare_versions(left: str = "bm25", right: str = "hybrid") -> str:
        """对比两份检索评测结果，例如 bm25 与 hybrid 的 Hit@1。"""
        mapping = {
            "bm25": EVAL_DIR / "retrieval_zh_refine.json",
            "hybrid": EVAL_DIR / "retrieval_hybrid_zh_refine.json",
        }
        left_path = mapping.get(left, EVAL_DIR / left)
        right_path = mapping.get(right, EVAL_DIR / right)
        if not left_path.exists() or not right_path.exists():
            return json.dumps(
                {"error": "评测文件不存在", "left": str(left_path.name), "right": str(right_path.name)},
                ensure_ascii=False,
            )
        left_data = json.loads(left_path.read_text(encoding="utf-8"))
        right_data = json.loads(right_path.read_text(encoding="utf-8"))

        def hit1(data: dict) -> float:
            return float((data.get("hit") or {}).get("1", {}).get("rate") or 0)

        return json.dumps(
            {
                "left": left,
                "right": right,
                "left_hit_at_1": hit1(left_data),
                "right_hit_at_1": hit1(right_data),
                "delta_hit_at_1": round(hit1(right_data) - hit1(left_data), 4),
                "left_p95_ms": left_data.get("p95_latency_ms"),
                "right_p95_ms": right_data.get("p95_latency_ms"),
            },
            ensure_ascii=False,
        )

    @tool
    def save_regression(note: str = "") -> str:
        """把当前评测指标保存为一条回归记录，便于以后对比。"""
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "note": note,
            "files": {},
        }
        for name in ("retrieval_zh_refine.json", "retrieval_hybrid_zh_refine.json"):
            path = EVAL_DIR / name
            if path.exists():
                payload["files"][name] = json.loads(path.read_text(encoding="utf-8"))
        REGRESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        with REGRESSION_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return json.dumps({"saved": True, "path": str(REGRESSION_PATH.name)}, ensure_ascii=False)

    return [
        search_docs,
        similar_incidents,
        run_history,
        compare_versions,
        save_regression,
    ], collected

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "检索知识库文档，回答事实类或文档问答时优先使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "similar_incidents",
            "description": "查找相似故障或同类问题记录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_history",
            "description": "查看最近问答运行记录。",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_versions",
            "description": "对比 bm25 与 hybrid 两份检索评测结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "left": {"type": "string"},
                    "right": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_regression",
            "description": "保存当前评测指标为回归记录。",
            "parameters": {
                "type": "object",
                "properties": {"note": {"type": "string"}},
            },
        },
    },
]


def run_named_tool(name: str, arguments: dict, corpus: str = "rgb") -> str:
    tools, _ = build_tools(corpus)
    mapping = {item.name: item for item in tools}
    tool_fn = mapping.get(name)
    if tool_fn is None:
        return json.dumps({"error": f"未知工具 {name}"}, ensure_ascii=False)
    return tool_fn.invoke(arguments or {})
