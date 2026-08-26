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

from retriever import get_index, get_rgb_items, retrieve
from rgb_data import find_item_by_query

load_dotenv(override=False)

BASE_DIR = Path(__file__).resolve().parent
EVAL_PATH = BASE_DIR / "data" / "eval" / "retrieval_zh_refine.json"
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
        raise RuntimeError("还没有配置钥匙，请把 DeepSeek API Key 写进 .env")
    return OpenAI(api_key=key, base_url="https://api.deepseek.com")


def append_trace(row: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_metrics() -> dict | None:
    if not EVAL_PATH.exists():
        return None
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


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


@app.get("/learn")
def learn() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "learn.html")


@app.get("/learn-data.js")
def learn_data() -> FileResponse:
    return FileResponse(
        BASE_DIR / "static" / "learn-data.js",
        media_type="text/javascript; charset=utf-8",
    )


@app.get("/guide")
def guide() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "guide.html")


@app.get("/api/stats")
def stats() -> dict:
    rgb_index = get_index("rgb")
    kb_index = get_index("kb")
    items = get_rgb_items()
    return {
        "rgb_docs": len(rgb_index.docs),
        "rgb_queries": len(items),
        "kb_docs": len(kb_index.docs),
        "metrics": load_metrics(),
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
        {"query": "Cron 表达式不合法会怎样？"},
        {"query": "工具调用失败时该怎么处理？"},
    ]
    return {"qa": qa, "reject": reject, "kb": kb}


@app.post("/search")
def search(body: AskIn) -> dict:
    question = body.question.strip()
    if not question:
        return {"error": "请先输入问题"}
    corpus = (body.corpus or "rgb").lower()
    k = max(1, min(int(body.k or 5), 10))
    hits, elapsed_ms = retrieve(question, k=k, corpus=corpus)
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

    if mode == "reject" and gold and gold["negative"]:
        hits = [
            {
                "id": f"neg-{i}",
                "title": text.replace("\n", " ").strip()[:28],
                "text": text,
                "score": 0.0,
            }
            for i, text in enumerate(gold["negative"][:k])
        ]
        elapsed_ms = 0.0
        evidence_note = "演示无证据：只提供该题的噪声文档，不含正例。"
    else:
        hits, elapsed_ms = retrieve(question, k=k, corpus=corpus)
        evidence_note = ""

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

    gen_ms = 0.0
    try:
        client = get_client()
        started = time.perf_counter()
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是文档问答助手。用简体中文短句回答。"
                        "必须依据给定资料；资料没有就说不知道。"
                    ),
                },
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
        gen_ms = (time.perf_counter() - started) * 1000
        text = resp.choices[0].message.content or ""
        error = None
    except Exception as exc:
        text = ""
        error = str(exc)

    result = {
        "answer": text,
        "error": error,
        "sources": hits,
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
            "source_ids": [item["id"] for item in hits],
            "latency_ms": result["latency_ms"],
            "generate_ms": result["generate_ms"],
            "error": error,
        }
    )
    return result
