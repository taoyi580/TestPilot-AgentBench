from __future__ import annotations

import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

from retriever import get_index, get_rgb_items, retrieve, rgb_query_counts
from rgb_data import find_item_by_query
from agent import run_agent

load_dotenv(override=False)

BASE_DIR = Path(__file__).resolve().parent
EVAL_PATH = BASE_DIR / "data" / "eval" / "retrieval_zh_refine.json"
HYBRID_EVAL_PATH = BASE_DIR / "data" / "eval" / "retrieval_hybrid_zh_refine.json"
REJECT_EVAL_PATH = BASE_DIR / "data" / "eval" / "reject_zh_refine.json"
TOOLS_EVAL_PATH = BASE_DIR / "data" / "eval" / "tool_calls_200.json"
TRACE_PATH = BASE_DIR / "traces" / "ask.jsonl"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_index("rgb")
    get_index("kb")
    yield


app = FastAPI(
    title="TestPilot",
    description="RGB 公开集上的检索问答演示",
    lifespan=lifespan,
)


class AskIn(BaseModel):
    question: str
    corpus: str = "rgb"
    k: int = 5
    mode: str = "qa"


def get_client() -> OpenAI:
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key or key.startswith("把你的"):
        raise RuntimeError("生成服务暂未配置，仍可查看检索结果")
    return OpenAI(api_key=key, base_url="https://api.deepseek.com")


def append_trace(row: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_eval_json(path: Path, drop_records: bool = True) -> dict | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if drop_records:
        data = {key: value for key, value in data.items() if key != "records"}
    data["metric_file"] = path.name
    return data


def load_metrics() -> dict | None:
    return load_eval_json(HYBRID_EVAL_PATH) or load_eval_json(EVAL_PATH)


@app.get("/health")
def health() -> dict:
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    return {
        "ok": True,
        "llm_configured": bool(key) and not key.startswith("把你的"),
    }


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/stats")
def stats() -> dict:
    rgb_index = get_index("rgb")
    kb_index = get_index("kb")
    counts = rgb_query_counts()
    return {
        "rgb_docs": len(rgb_index.docs),
        "rgb_queries": counts["zh_refine"],
        "rgb_query_total": counts["total"],
        "rgb_splits": counts,
        "kb_docs": len(kb_index.docs),
        "metrics": load_metrics(),
        "bm25_metrics": load_eval_json(EVAL_PATH),
        "reject_metrics": load_eval_json(REJECT_EVAL_PATH),
        "tool_metrics": load_eval_json(TOOLS_EVAL_PATH),
        "source": "https://github.com/chen700564/RGB",
    }


@app.get("/api/examples")
def examples() -> dict:
    items = get_rgb_items()
    qa = [
        {"query": item["query"], "answers": item["answers"]}
        for item in items[:8]
    ]
    reject = [
        {"query": item["query"], "answers": item["answers"]}
        for item in items[8:12]
    ]
    kb = [
        {"query": "会话串话是什么原因？"},
        {"query": "对比 bm25 和 hybrid 的 Hit@1"},
        {"query": "把当前评测保存成回归记录"},
    ]
    return {"qa": qa, "reject": reject, "kb": kb}


@app.post("/search")
def search(body: AskIn) -> dict:
    question = body.question.strip()
    if not question:
        return {"error": "请先输入问题"}
    corpus = (body.corpus or "rgb").lower()
    k = max(1, min(int(body.k or 5), 10))
    hits, elapsed_ms = retrieve(question, k=k, corpus=corpus, mode="hybrid")
    gold = find_item_by_query(get_rgb_items(), question) if corpus == "rgb" else None
    return {
        "sources": hits,
        "latency_ms": round(elapsed_ms, 2),
        "gold_answers": gold["answers"] if gold else [],
        "query_id": gold["id"] if gold else None,
    }


@app.post("/ask")
def ask(body: AskIn) -> dict:
    question = body.question.strip()
    if not question:
        return {"error": "请先输入问题"}
    corpus = (body.corpus or "rgb").lower()
    mode = (body.mode or "qa").lower()
    k = max(1, min(int(body.k or 5), 10))
    gold = find_item_by_query(get_rgb_items(), question) if corpus == "rgb" else None

    tools: list[dict] = []
    hits: list[dict] = []
    gen_ms = 0.0
    error = None
    text = ""

    if mode == "reject" and gold and gold["negative"]:
        hits = [
            {
                "id": f"neg-{i}",
                "title": text_item.replace("\n", " ").strip()[:28],
                "text": text_item,
                "score": 0.0,
            }
            for i, text_item in enumerate(gold["negative"][:k])
        ]
        elapsed_ms = 0.0
        evidence_note = "无证据模式：上下文仅含无关文档。"
        if hits:
            evidence = "\n\n".join(
                f"资料{i + 1}《{item['title']}》：\n{item['text']}"
                for i, item in enumerate(hits)
            )
            user_content = (
                f"问题：{question}\n\n"
                "请只根据下面资料回答。资料不足以回答就明确说不知道，不要编造。\n\n"
                f"{evidence}"
            )
        else:
            user_content = f"问题：{question}\n\n没有检索到资料。请明确说不知道，不要编造。"
        try:
            client = get_client()
            started = time.perf_counter()
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是文档问答助手。用简体中文短句回答。必须依据给定资料；资料没有就说不知道。",
                    },
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2,
            )
            gen_ms = (time.perf_counter() - started) * 1000
            text = resp.choices[0].message.content or ""
        except Exception as exc:
            error = str(exc)
    else:
        evidence_note = ""
        elapsed_ms = 0.0
        try:
            agent_out = run_agent(question, corpus=corpus)
            text = agent_out["answer"]
            hits = agent_out["sources"]
            tools = agent_out["tools"]
            gen_ms = agent_out["generate_ms"]
        except Exception as exc:
            hits, elapsed_ms = retrieve(question, k=k, corpus=corpus, mode="hybrid")
            error = str(exc)

    result = {
        "answer": text,
        "error": error,
        "sources": hits,
        "tools": tools,
        "latency_ms": round(elapsed_ms, 2),
        "generate_ms": round(gen_ms, 2),
        "corpus": corpus,
        "mode": mode,
        "note": evidence_note,
        "gold_answers": gold["answers"] if gold else [],
        "query_id": gold["id"] if gold else None,
    }
    append_trace(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "corpus": corpus,
            "mode": mode,
            "tools": [item.get("name") for item in tools],
            "source_ids": [item["id"] for item in hits],
            "latency_ms": result["latency_ms"],
            "generate_ms": result["generate_ms"],
            "error": error,
        }
    )
    return result
