"""jieba + BM25，并可与 TF-IDF 融合后重排序。"""

from __future__ import annotations

import math
import pickle
import time
from collections import Counter
from pathlib import Path

import jieba
from rank_bm25 import BM25Okapi

from rgb_data import load_rgb_items, unique_docs

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "data" / "kb"
CACHE_DIR = BASE_DIR / "data" / "cache"

_indexes: dict[str, "HybridIndex"] = {}
_rgb_items: dict[str, list[dict]] = {}


def tokenize(text: str) -> list[str]:
    return [tok for tok in jieba.cut_for_search(text) if tok.strip()]


def _rrf(rank: int, k: int = 60) -> float:
    return 1.0 / (k + rank)


class HybridIndex:
    def __init__(self, docs: list[dict], tokens: list[list[str]] | None = None):
        self.docs = docs
        self.tokens = tokens or [tokenize(doc["text"]) for doc in docs]
        self.bm25 = BM25Okapi(self.tokens)
        n_docs = len(self.docs)
        df: Counter[str] = Counter()
        for toks in self.tokens:
            df.update(set(toks))
        self.idf = {tok: math.log((n_docs + 1) / (count + 1)) + 1.0 for tok, count in df.items()}
        self.doc_w: list[dict[str, float]] = []
        self.doc_norm: list[float] = []
        for toks in self.tokens:
            tf = Counter(toks)
            weights = {
                tok: (1.0 + math.log(count)) * self.idf[tok] for tok, count in tf.items()
            }
            norm = math.sqrt(sum(value * value for value in weights.values())) or 1.0
            self.doc_w.append(weights)
            self.doc_norm.append(norm)

    def _bm25_ranks(self, query: str, limit: int) -> list[tuple[int, float]]:
        scores = self.bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out: list[tuple[int, float]] = []
        for idx in order[:limit]:
            if float(scores[idx]) <= 0:
                continue
            out.append((idx, float(scores[idx])))
        return out

    def _tfidf_ranks(self, query: str, limit: int) -> list[tuple[int, float]]:
        qtf = Counter(tokenize(query))
        q_w = {
            tok: (1.0 + math.log(count)) * self.idf[tok]
            for tok, count in qtf.items()
            if tok in self.idf
        }
        q_norm = math.sqrt(sum(value * value for value in q_w.values())) or 1.0
        scored: list[tuple[int, float]] = []
        for idx, (weights, norm) in enumerate(zip(self.doc_w, self.doc_norm, strict=True)):
            dot = sum(q_w[tok] * weights[tok] for tok in q_w if tok in weights)
            scored.append((idx, dot / (q_norm * norm)))
        scored.sort(key=lambda item: item[1], reverse=True)
        return [item for item in scored[:limit] if item[1] > 0]

    def search(self, query: str, k: int = 5, mode: str = "hybrid") -> tuple[list[dict], float]:
        started = time.perf_counter()
        method = (mode or "hybrid").lower()
        take = max(k, 50)
        if method == "bm25":
            ranked = self._bm25_ranks(query, take)
        else:
            bm25_ranks = self._bm25_ranks(query, 200)
            tfidf_ranks = self._tfidf_ranks(query, 200)
            fused: dict[int, float] = {}
            bm25_map = {idx: score for idx, score in bm25_ranks}
            tfidf_map = {idx: score for idx, score in tfidf_ranks}
            for rank, (idx, _) in enumerate(bm25_ranks, start=1):
                fused[idx] = fused.get(idx, 0.0) + _rrf(rank)
            for rank, (idx, _) in enumerate(tfidf_ranks, start=1):
                fused[idx] = fused.get(idx, 0.0) + _rrf(rank)
            cand = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:take]
            if cand:
                bm25_vals = [bm25_map.get(idx, 0.0) for idx, _ in cand]
                tfidf_vals = [tfidf_map.get(idx, 0.0) for idx, _ in cand]
                b_min, b_max = min(bm25_vals), max(bm25_vals)
                t_min, t_max = min(tfidf_vals), max(tfidf_vals)
                ranked = []
                for idx, _ in cand:
                    b = bm25_map.get(idx, 0.0)
                    t = tfidf_map.get(idx, 0.0)
                    b_n = 0.0 if b_max == b_min else (b - b_min) / (b_max - b_min)
                    t_n = 0.0 if t_max == t_min else (t - t_min) / (t_max - t_min)
                    ranked.append((idx, 0.65 * b_n + 0.35 * t_n))
                ranked.sort(key=lambda item: item[1], reverse=True)
            else:
                ranked = bm25_ranks[:take]
        hits: list[dict] = []
        for idx, score in ranked[:k]:
            doc = self.docs[idx]
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


def _load_rgb_index(split: str = "zh_refine") -> HybridIndex:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"rgb_{split}_hybrid.pkl"
    src = BASE_DIR / "data" / "rgb" / f"{split}.json"
    stamp = src.stat().st_mtime if src.exists() else 0
    if cache_path.exists():
        payload = pickle.loads(cache_path.read_bytes())
        if payload.get("stamp") == stamp:
            return HybridIndex(payload["docs"], payload["tokens"])
    items = load_rgb_items(split)
    docs = unique_docs(items)
    index = HybridIndex(docs)
    cache_path.write_bytes(
        pickle.dumps({"stamp": stamp, "docs": index.docs, "tokens": index.tokens})
    )
    return index


def get_rgb_items(split: str = "zh_refine") -> list[dict]:
    if split not in _rgb_items:
        _rgb_items[split] = load_rgb_items(split)
    return _rgb_items[split]


def rgb_query_counts() -> dict:
    counts = {
        "zh_refine": len(get_rgb_items("zh_refine")),
        "zh_int": len(get_rgb_items("zh_int")),
        "zh_fact": len(get_rgb_items("zh_fact")),
    }
    counts["total"] = counts["zh_refine"] + counts["zh_int"] + counts["zh_fact"]
    return counts


def get_index(corpus: str = "rgb") -> HybridIndex:
    key = corpus.strip().lower() or "rgb"
    if key not in _indexes:
        if key == "kb":
            _indexes[key] = HybridIndex(_load_kb_docs())
        elif key == "rgb":
            _indexes[key] = _load_rgb_index()
        else:
            raise ValueError("语料只能是 rgb 或 kb")
    return _indexes[key]


def retrieve(
    question: str,
    k: int = 5,
    corpus: str = "rgb",
    mode: str = "hybrid",
) -> tuple[list[dict], float]:
    return get_index(corpus).search(question, k=k, mode=mode)
