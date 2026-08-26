"""jieba + BM25 检索。语料可选 RGB 公开集或本地研发笔记。"""

from __future__ import annotations

import pickle
import time
from pathlib import Path

import jieba
from rank_bm25 import BM25Okapi

from rgb_data import load_rgb_items, unique_docs

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "data" / "kb"
CACHE_DIR = BASE_DIR / "data" / "cache"

_indexes: dict[str, "Bm25Index"] = {}
_rgb_items: list[dict] | None = None


def tokenize(text: str) -> list[str]:
    return [tok for tok in jieba.cut_for_search(text) if tok.strip()]


class Bm25Index:
    def __init__(self, docs: list[dict], tokens: list[list[str]] | None = None):
        self.docs = docs
        self.tokens = tokens or [tokenize(doc["text"]) for doc in docs]
        self.bm25 = BM25Okapi(self.tokens)

    def search(self, query: str, k: int = 5) -> tuple[list[dict], float]:
        started = time.perf_counter()
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(
            zip(self.docs, scores, strict=True),
            key=lambda item: item[1],
            reverse=True,
        )
        hits: list[dict] = []
        for doc, score in ranked[:k]:
            if float(score) <= 0:
                continue
            hits.append(
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "text": doc["text"],
                    "score": round(float(score), 4),
                }
            )
        elapsed_ms = (time.perf_counter() - started) * 1000
        return hits, elapsed_ms


def _load_kb_docs() -> list[dict]:
    docs: list[dict] = []
    for path in sorted(KB_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        title = text.splitlines()[0] if text else path.stem
        docs.append({"id": path.stem, "title": title, "text": text})
    if not docs:
        raise RuntimeError("data/kb 里还没有资料文件")
    return docs


def _load_rgb_index(split: str = "zh_refine") -> Bm25Index:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"rgb_{split}.pkl"
    src = BASE_DIR / "data" / "rgb" / f"{split}.json"
    stamp = src.stat().st_mtime if src.exists() else 0
    if cache_path.exists():
        payload = pickle.loads(cache_path.read_bytes())
        if payload.get("stamp") == stamp:
            return Bm25Index(payload["docs"], payload["tokens"])
    items = load_rgb_items(split)
    docs = unique_docs(items)
    index = Bm25Index(docs)
    cache_path.write_bytes(
        pickle.dumps({"stamp": stamp, "docs": index.docs, "tokens": index.tokens})
    )
    return index


def get_rgb_items(split: str = "zh_refine") -> list[dict]:
    global _rgb_items
    if _rgb_items is None:
        _rgb_items = load_rgb_items(split)
    return _rgb_items


def get_index(corpus: str = "rgb") -> Bm25Index:
    key = corpus.strip().lower() or "rgb"
    if key not in _indexes:
        if key == "kb":
            _indexes[key] = Bm25Index(_load_kb_docs())
        elif key == "rgb":
            _indexes[key] = _load_rgb_index()
        else:
            raise ValueError("语料只能是 rgb 或 kb")
    return _indexes[key]


def retrieve(question: str, k: int = 5, corpus: str = "rgb") -> tuple[list[dict], float]:
    return get_index(corpus).search(question, k=k)
