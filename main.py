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
from agent import run_agent

load_dotenv(override=False)

BASE_DIR = Path(__file__).resolve().parent
TRACE_PATH = BASE_DIR / "traces" / "ask.jsonl"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_index("rgb")
    get_index("kb")
    yield


app = FastAPI(
    title="TestPilot",
    description="先检索知识库证据，再生成带来源的研发问答和故障诊断结果。",
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


def public_sources(items: list[dict]) -> list[dict]:
    return [
        {
            "id": item.get("id"),
            "title": item.get("title"),
            "text": item.get("text"),
        }
        for item in items
    ]


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


@app.get("/api/examples")
def examples() -> dict:
    items = get_rgb_items()
    qa = [{"query": item["query"]} for item in items[:8]]
    reject = [{"query": item["query"]} for item in items[8:12]]
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
    hits, _ = retrieve(question, k=k, corpus=corpus, mode="hybrid")
    return {"sources": public_sources(hits)}


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

    public_result = {
        "answer": text,
        "error": error,
        "sources": public_sources(hits),
    }
    retrieval_ms = round(elapsed_ms, 2)
    generation_ms = round(gen_ms, 2)
    append_trace(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "corpus": corpus,
            "mode": mode,
            "tools": [item.get("name") for item in tools],
            "source_ids": [item["id"] for item in hits],
            "latency_ms": retrieval_ms,
            "generate_ms": generation_ms,
            "error": error,
        }
    )
    return public_result
