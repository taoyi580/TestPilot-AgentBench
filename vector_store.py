"""Qdrant 向量库。本地文件模式不可用时退回内存库，检索路径仍走 Qdrant。"""

from __future__ import annotations

import atexit
import uuid
from pathlib import Path

import numpy as np

from embedder import VECTOR_DIM, embed_query

_CLIENT = None
_BACKEND = "qdrant-memory"


def _shared_client(path: Path):
    global _CLIENT, _BACKEND
    if _CLIENT is not None:
        return _CLIENT
    from qdrant_client import QdrantClient

    try:
        path.mkdir(parents=True, exist_ok=True)
        _CLIENT = QdrantClient(path=str(path))
        _BACKEND = "qdrant-local"
    except Exception as exc:
        print(f"Qdrant 本地目录不可用，改用内存库：{exc}")
        _CLIENT = QdrantClient(":memory:")
        _BACKEND = "qdrant-memory"
    return _CLIENT


def _close_client() -> None:
    global _CLIENT
    if _CLIENT is None:
        return
    try:
        _CLIENT.close()
    except Exception:
        pass
    _CLIENT = None


atexit.register(_close_client)


class QdrantStore:
    def __init__(self, collection: str, path: Path):
        self.collection = collection
        self.dim = VECTOR_DIM
        self.client = _shared_client(path)
        self.backend = _BACKEND
        self._vectors: np.ndarray | None = None
        self._doc_ids: list[str] = []
        self._payloads: list[dict] = []

    def _ensure_collection(self, recreate: bool) -> None:
        from qdrant_client.models import Distance, VectorParams

        exists = self.client.collection_exists(self.collection)
        if exists and recreate:
            self.client.delete_collection(self.collection)
            exists = False
        if not exists:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
            )

    def _points_count(self) -> int:
        try:
            info = self.client.get_collection(self.collection)
            return int(getattr(info, "points_count", 0) or 0)
        except Exception:
            return 0

    def upsert(self, chunks: list[dict], vectors: np.ndarray, force: bool = False) -> None:
        from qdrant_client.models import PointStruct

        self._vectors = np.asarray(vectors, dtype=np.float32)
        self._doc_ids = [item["doc_id"] for item in chunks]
        self._payloads = chunks
        n = len(chunks)
        self._ensure_collection(recreate=force or self._points_count() != n)
        if self._points_count() == n and not force:
            return
        points = []
        for i, chunk in enumerate(chunks):
            points.append(
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["chunk_id"])),
                    vector=self._vectors[i].tolist(),
                    payload={
                        "doc_id": chunk["doc_id"],
                        "chunk_id": chunk["chunk_id"],
                        "title": chunk["title"],
                        "text": chunk["text"],
                    },
                )
            )
        batch = 256
        for start in range(0, len(points), batch):
            self.client.upsert(collection_name=self.collection, points=points[start : start + batch])

    def search(self, query: str, limit: int = 200) -> list[tuple[str, float]]:
        """按块检索，折叠成文档 id，保留首次出现顺序。"""
        qvec = embed_query(query)
        ranked: list[tuple[str, float]] = []
        try:
            ranked = self._qdrant_search(qvec, limit * 3)
        except Exception as exc:
            print(f"Qdrant 查询失败，改用内存余弦：{exc}")
            ranked = self._numpy_search(qvec, limit * 3)
        seen: set[str] = set()
        out: list[tuple[str, float]] = []
        for doc_id, score in ranked:
            if doc_id in seen:
                continue
            seen.add(doc_id)
            out.append((doc_id, score))
            if len(out) >= limit:
                break
        return out

    def _qdrant_search(self, qvec: np.ndarray, limit: int) -> list[tuple[str, float]]:
        response = self.client.query_points(
            collection_name=self.collection,
            query=qvec.tolist(),
            limit=limit,
            with_payload=True,
        )
        rows: list[tuple[str, float]] = []
        for point in response.points:
            payload = point.payload or {}
            doc_id = str(payload.get("doc_id") or "")
            if not doc_id:
                continue
            rows.append((doc_id, float(point.score)))
        return rows

    def _numpy_search(self, qvec: np.ndarray, limit: int) -> list[tuple[str, float]]:
        if self._vectors is None or not len(self._vectors):
            return []
        scores = self._vectors @ qvec
        take = min(limit, len(scores))
        if take <= 0:
            return []
        idx = np.argpartition(-scores, take - 1)[:take]
        idx = idx[np.argsort(-scores[idx])]
        return [(self._doc_ids[i], float(scores[i])) for i in idx]
