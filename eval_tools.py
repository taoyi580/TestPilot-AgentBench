"""五工具离线调用评测：200 题，看首轮是否选对工具。"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from retriever import get_rgb_items
from agent_tools import OPENAI_TOOLS

load_dotenv(override=False)
BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "data" / "eval" / "tool_calls_200.json"


def cases() -> list[dict]:
    items = get_rgb_items("zh_refine")
    out: list[dict] = []
    for item in items[:80]:
        out.append(
            {
                "id": f"search-{item['id']}",
                "query": item["query"],
                "expect": "search_docs",
            }
        )
    similar = [
        "线上出现会话串话，帮我找相似故障",
        "停止按钮失效还在后台写内容，有没有同类问题",
        "工具调用失败该怎么处理，查相似记录",
        "Cron 表达式不合法会怎样，找相关故障说明",
        "流式输出中断过，有没有类似案例",
        "多 Agent 派发后父任务没续上，查相似问题",
        "对话上下文串到别人会话，检索同类故障",
        "超时后任务还在跑，帮我找相似故障记录",
    ]
    for i, query in enumerate(similar * 5):
        out.append({"id": f"similar-{i}", "query": query, "expect": "similar_incidents"})
    history = [
        "最近几次问答的耗时是多少",
        "查看历史运行记录",
        "上一轮调用了哪些工具",
        "最近运行的证据编号有哪些",
        "列出最近 3 次问答轨迹",
        "历史运行里有没有失败",
    ]
    for i, query in enumerate(history * 5):
        out.append({"id": f"history-{i}", "query": query, "expect": "run_history"})
    compare = [
        "对比 bm25 和 hybrid 的 Hit@1",
        "两个检索版本差多少",
        "版本对比一下评测结果",
        "hybrid 比 bm25 提升了多少",
        "比较两份检索评测的 P95",
    ]
    for i, query in enumerate(compare * 5):
        out.append({"id": f"compare-{i}", "query": query, "expect": "compare_versions"})
    save = [
        "把当前评测保存成回归记录",
        "保存一次回归",
        "把这次结果记入回归",
        "回归保存，备注 hybrid 实验",
        "请保存评测快照",
    ]
    for i, query in enumerate(save * 5):
        out.append({"id": f"save-{i}", "query": query, "expect": "save_regression"})
    return out[:200]


def first_tool(message) -> str | None:
    calls = message.tool_calls or []
    if not calls:
        return None
    first = calls[0]
    function = getattr(first, "function", None)
    if function is not None:
        return function.name
    if isinstance(first, dict):
        return (first.get("function") or {}).get("name") or first.get("name")
    return getattr(first, "name", None)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key or key.startswith("把你的"):
        raise SystemExit("缺少 DEEPSEEK_API_KEY")
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    dataset = cases()
    correct = 0
    records = []
    for item in dataset:
        last_error = None
        resp = None
        for attempt in range(5):
            try:
                resp = client.chat.completions.create(
                    model="deepseek-chat",
                    temperature=0,
                    tools=OPENAI_TOOLS,
                    tool_choice="auto",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "根据用户意图选择工具。事实问答用 search_docs；"
                                "故障排查用 similar_incidents；历史运行用 run_history；"
                                "对比评测用 compare_versions；保存回归用 save_regression。"
                            ),
                        },
                        {"role": "user", "content": item["query"]},
                    ],
                )
                break
            except Exception as exc:
                last_error = exc
                time.sleep(2 ** attempt)
        if resp is None:
            raise last_error
        got = first_tool(resp.choices[0].message)
        ok = got == item["expect"]
        correct += int(ok)
        records.append({**item, "got": got, "ok": ok})
        print(f"{item['id']}\t{ok}\t{got}\t{item['expect']}", flush=True)
    result = {
        "dataset": "self-built 5-tool first-call routing",
        "n": len(dataset),
        "correct": correct,
        "rate": round(correct / len(dataset), 4),
        "records": records,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"n": result["n"], "correct": correct, "rate": result["rate"]}, ensure_ascii=False))
    print(f"已写入 {OUT_PATH}")


if __name__ == "__main__":
    main()
