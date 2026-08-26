"""LangGraph 编排五个工具后生成回答。"""

from __future__ import annotations

import os
import time

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agent_tools import build_tools

SYSTEM = (
    "你是研发文档与故障诊断助手。"
    "工具：search_docs（文档检索）、similar_incidents（相似故障）、"
    "run_history（历史运行）、compare_versions（版本对比）、save_regression（回归保存）。"
    "事实问答先检索文档；故障排查查相似记录；问历史运行、对比评测或保存回归时用对应工具。"
    "只根据工具返回的资料回答。资料不够就说不知道，不要编造。用简体中文短句。"
)


def _llm() -> ChatOpenAI:
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key or key.startswith("把你的"):
        raise RuntimeError("生成服务暂未配置，仍可查看检索结果")
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=key,
        base_url="https://api.deepseek.com",
        temperature=0.2,
    )


def run_agent(question: str, corpus: str = "rgb") -> dict:
    tools, collected = build_tools(corpus)
    started = time.perf_counter()
    graph = create_react_agent(_llm(), tools, prompt=SYSTEM)
    result = graph.invoke(
        {"messages": [("user", question)]},
        config={"recursion_limit": 8},
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    messages = result.get("messages") or []
    answer = ""
    tools_used: list[dict] = []
    for message in messages:
        for call in getattr(message, "tool_calls", None) or []:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", "")
            args = call.get("args") if isinstance(call, dict) else getattr(call, "args", {})
            tools_used.append({"name": name, "args": args})
        content = getattr(message, "content", "")
        if content and getattr(message, "type", "") == "ai" and not getattr(message, "tool_calls", None):
            answer = content if isinstance(content, str) else str(content)
    if not answer and messages:
        content = getattr(messages[-1], "content", "")
        answer = content if isinstance(content, str) else str(content)
    return {
        "answer": answer,
        "sources": collected,
        "tools": tools_used,
        "generate_ms": round(elapsed_ms, 2),
    }
