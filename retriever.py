"""jieba + BM25，并与 BGE 向量（Qdrant）做混合召回，可选交叉编码器重排。"""

from __future__ import annotations

import json
import pickle
import time
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
import jieba

from chunker import chunk_docs
from embedder import MODEL_NAME, VECTOR_DIM, embed_passages
from reranker import rerank_doc_ids
from rgb_data import load_rgb_items, unique_docs
from vector_store import QdrantStore

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "data" / "kb"
CACHE_DIR = BASE_DIR / "data" / "cache"
QDRANT_DIR = BASE_DIR / "data" / "qdrant"

_indexes: dict[str, "HybridIndex"] = {}
_rgb_items: dict[str, list[dict]] = {}


def tokenize(text: str) -> list[str]:
    return [tok for tok in jieba.cut_for_search(text) if tok.strip()]


def _rrf(rank: int, k: int = 60) -> float:
    return 1.0 / (k + rank)


class HybridIndex:
    def __init__(self, docs: list[dict], tokens: list[list[str]] | None = None):
        self.docs = docs
        self.doc_by_id = {doc["id"]: doc for doc in docs}
        self.tokens = tokens or [tokenize(doc["text"]) for doc in docs]
        self.bm25 = BM25Okapi(self.tokens)
        self.chunks: list[dict] = []
        self.store: QdrantStore | None = None
        self.embed_model = MODEL_NAME
        self.vector_backend = "none"
        self.n_chunks = 0

    def _bm25_doc_ids(self, query: str, limit: int) -> list[str]:
        scores = self.bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out: list[str] = []
        for idx in order[:limit]:
            if float(scores[idx]) <= 0:
                continue
            out.append(self.docs[idx]["id"])
        return out

    def _fuse(self, left: list[str], right: list[str]) -> list[str]:
        fused: dict[str, float] = {}
        for rank, doc_id in enumerate(left, start=1):
            fused[doc_id] = fused.get(doc_id, 0.0) + _rrf(rank)
        for rank, doc_id in enumerate(right, start=1):
            fused[doc_id] = fused.get(doc_id, 0.0) + _rrf(rank)
        return [doc_id for doc_id, _ in sorted(fused.items(), key=lambda item: item[1], reverse=True)]

    def _hits_from_ids(self, doc_ids: list[str], k: int, scores: dict[str, float] | None = None) -> list[dict]:
        hits: list[dict] = []
        for rank, doc_id in enumerate(doc_ids[:k], start=1):
            doc = self.doc_by_id.get(doc_id)
            if not doc:
                continue
            score = 0.0 if scores is None else float(scores.get(doc_id, 0.0))
            if scores is None:
                score = 1.0 / rank
            hits.append(
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "text": doc["text"],
                    "score": round(score, 4),
                }
            )
        return hits

    def search(self, query: str, k: int = 5, mode: str = "hybrid") -> tuple[list[dict], float]:
        started = time.perf_counter()
        method = (mode or "hybrid").lower()
        take = max(k, 200)
        if method == "bm25":
            doc_ids = self._bm25_doc_ids(query, take)
        elif method == "vector":
            if self.store is None:
                raise RuntimeError("向量库尚未就绪")
            doc_ids = [doc_id for doc_id, _ in self.store.search(query, limit=take)]
        else:
            bm25_ids = self._bm25_doc_ids(query, take)
            vector_ids = [doc_id for doc_id, _ in self.store.search(query, limit=take)] if self.store else []
            doc_ids = self._fuse(bm25_ids, vector_ids)
            doc_ids = rerank_doc_ids(query, doc_ids, self.doc_by_id)
        hits = self._hits_from_ids(doc_ids, k)
        elapsed_ms = (time.perf_counter() - started) * 1000
        return hits, elapsed_ms

    def attach_vectors(self, cache_key: str, stamp: float) -> None:
        self.chunks = chunk_docs(self.docs)
        self.n_chunks = len(self.chunks)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        meta_path = CACHE_DIR / f"{cache_key}_vec.json"
        npz_path = CACHE_DIR / f"{cache_key}_vec.npz"
        expected = {
            "stamp": stamp,
            "model": MODEL_NAME,
            "dim": VECTOR_DIM,
            "n_chunks": self.n_chunks,
            "n_docs": len(self.docs),
        }
        vectors = None
        if meta_path.exists() and npz_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta == expected:
                payload = np.load(npz_path, allow_pickle=False)
                vectors = payload["vectors"]
                if len(vectors) != self.n_chunks:
                    vectors = None
        if vectors is None:
            print(f"正在为 {self.n_chunks} 个切块生成向量…", flush=True)
            vectors = embed_passages([chunk["text"] for chunk in self.chunks])
            np.savez(npz_path, vectors=vectors)
            meta_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8")
        self.store = QdrantStore(collection=cache_key, path=QDRANT_DIR)
        self.store.upsert(self.chunks, vectors)
        self.vector_backend = self.store.backend


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
    cache_path = CACHE_DIR / f"rgb_{split}_bm25.pkl"
    src = BASE_DIR / "data" / "rgb" / f"{split}.json"
    stamp = src.stat().st_mtime if src.exists() else 0
    if cache_path.exists():
        payload = pickle.loads(cache_path.read_bytes())
        if payload.get("stamp") == stamp:
            index = HybridIndex(payload["docs"], payload["tokens"])
            index.attach_vectors(f"rgb_{split}", stamp)
            return index
    items = load_rgb_items(split)
    docs = unique_docs(items)
    index = HybridIndex(docs)
    cache_path.write_bytes(
        pickle.dumps({"stamp": stamp, "docs": index.docs, "tokens": index.tokens})
    )
    index.attach_vectors(f"rgb_{split}", stamp)
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
            index = HybridIndex(_load_kb_docs())
            index.attach_vectors("kb", 1.0)
            _indexes[key] = index
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
