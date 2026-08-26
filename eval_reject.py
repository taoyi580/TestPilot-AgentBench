"""无证据拒答：RGB zh_refine 前 100 题只提供 negative 文档。"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from retriever import get_rgb_items

load_dotenv(override=False)
BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "data" / "eval" / "reject_zh_refine.json"
REFUSE_MARKERS = ("不知道", "无法回答", "没有足够", "资料不足", "无法确定", "未提供", "无法从")


def is_reject(text: str) -> bool:
    return any(marker in (text or "") for marker in REFUSE_MARKERS)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key or key.startswith("把你的"):
        raise SystemExit("缺少 DEEPSEEK_API_KEY")
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    items = get_rgb_items("zh_refine")[:100]
    records = []
    correct = 0
    for item in items:
        docs = item["negative"][:5]
        evidence = "\n\n".join(f"资料{i + 1}：\n{text}" for i, text in enumerate(docs))
        resp = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": "只根据资料回答。资料不足以回答问题时必须说不知道，不要编造。",
                },
                {
                    "role": "user",
                    "content": f"问题：{item['query']}\n\n{evidence}",
                },
            ],
        )
        answer = resp.choices[0].message.content or ""
        ok = is_reject(answer)
        correct += int(ok)
        records.append({"id": item["id"], "query": item["query"], "ok": ok, "answer": answer[:200]})
        print(f"{item['id']}\t{ok}\t{item['query'][:20]}", flush=True)
    result = {
        "dataset": "RGB zh_refine negative-only",
        "n": len(items),
        "correct": correct,
        "rate": round(correct / len(items), 4),
        "records": records,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"n": result["n"], "correct": correct, "rate": result["rate"]}, ensure_ascii=False))
    print(f"已写入 {OUT_PATH}")


if __name__ == "__main__":
    main()
