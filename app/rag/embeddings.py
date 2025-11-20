from __future__ import annotations

import hashlib
import importlib
import importlib.util
from typing import List, Tuple

import numpy as np

from ..config import get_settings

settings = get_settings()

faiss_spec = importlib.util.find_spec("faiss")
faiss = importlib.import_module("faiss") if faiss_spec else None  # type: ignore

_index = None
_id_map: list[int] = []


def _ensure_index():
    global _index
    if _index is None:
        dimension = settings.embedding_dim
        if faiss:
            _index = faiss.IndexFlatL2(dimension)
        else:
            _index = []  # type: ignore
    return _index


def embed_text(text: str) -> np.ndarray:
    text = text or ""
    hashed = hashlib.sha256(text.encode("utf-8")).digest()
    data = np.frombuffer(hashed, dtype=np.uint8)
    repeats = int(np.ceil(settings.embedding_dim / len(data)))
    tiled = np.tile(data, repeats)[: settings.embedding_dim]
    vector = tiled.astype("float32")
    norm = np.linalg.norm(vector) or 1.0
    return vector / norm


def blend_vectors(segments: list[str]) -> np.ndarray:
    """Average multiple text segments to smooth noisy inputs."""

    valid_segments = [seg for seg in segments if seg]
    if not valid_segments:
        return embed_text("")
    vectors = [embed_text(seg) for seg in valid_segments]
    mean = np.mean(np.stack(vectors, axis=0), axis=0)
    norm = np.linalg.norm(mean) or 1.0
    return mean / norm


def init_index():
    global _index, _id_map
    _index = None
    _id_map = []
    _ensure_index()


def add_vector(item_id: int, vector: np.ndarray):
    index = _ensure_index()
    if faiss:
        index.add(np.array([vector]).astype("float32"))
    else:
        index.append(vector.astype("float32"))  # type: ignore
    _id_map.append(item_id)


def search(vector: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
    index = _ensure_index()
    if faiss:
        distances, indices = index.search(np.array([vector]).astype("float32"), k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            results.append((_id_map[idx], float(dist)))
        return results
    else:
        if not index:
            return []
        similarities = []
        for stored_vec, stored_id in zip(index, _id_map):  # type: ignore
            dist = float(np.linalg.norm(stored_vec - vector))
            similarities.append((stored_id, dist))
        similarities.sort(key=lambda x: x[1])
        return similarities[:k]
