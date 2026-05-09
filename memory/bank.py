"""
memory/bank.py
Persistent memory bank of verified (program description, PlusCal spec, invariant) triples.
Grows monotonically with successful episodes. Supports similarity-based retrieval.
"""

import json
import os
from typing import List

BANK_PATH = "memory/bank.json"


class MemoryBank:
    def __init__(self, path: str = BANK_PATH):
        self.path = path
        self._entries: List[dict] = []
        self._load()

    def store(self, description: str, spec: str, invariant: str):
        """Add a newly verified triple to the bank and persist to disk."""
        entry = {"description": description, "spec": spec, "invariant": invariant}
        self._entries.append(entry)
        self._save()

    def retrieve(self, query_description: str, k: int = 3, weights: dict = None) -> List[dict]:
        """
        Return the k most relevant entries for a given program description.
        Currently uses simple keyword overlap; plug in sentence-transformers for
        dense retrieval in production.
        """
        if not self._entries:
            return []

        scored = [
            (self._similarity(query_description, e["description"], weights), e)
            for e in self._entries
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:k]]

    def __len__(self):
        return len(self._entries)

    # ── internal ──────────────────────────────────────────────────────────

    @staticmethod
    def _similarity(q: str, d: str, weights: dict = None) -> float:
        """Token overlap similarity (placeholder for learned dense retrieval)."""
        q_tokens = set(q.lower().split())
        d_tokens = set(d.lower().split())
        if not q_tokens:
            return 0.0
        return len(q_tokens & d_tokens) / len(q_tokens)

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                self._entries = json.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self._entries, f, indent=2)
