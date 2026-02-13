"""
Shared In-Memory Store for the Documentation Generator Pipeline.

The Code Analyzer agent parses the codebase, builds AST trees, and stores
all parsed data here. Downstream agents (API Semantics, Architecture, Examples,
Getting Started, Document Assembler) read from this shared memory instead of
re-reading/re-parsing the codebase each time.
"""

import json
import threading
from typing import Any, Dict, List, Optional


class SharedMemory:
    """Thread-safe singleton in-memory store shared across all agents."""

    _instance: Optional["SharedMemory"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "SharedMemory":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._store: Dict[str, Any] = {}
            return cls._instance

    # ── write ──────────────────────────────────────────────────────────
    def set(self, key: str, value: Any) -> None:
        """Store a value under *key*."""
        with self._lock:
            self._store[key] = value

    # ── read ───────────────────────────────────────────────────────────
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve the value stored under *key*."""
        with self._lock:
            return self._store.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Return a shallow copy of the entire store."""
        with self._lock:
            return dict(self._store)

    def keys(self) -> List[str]:
        """Return all keys currently in the store."""
        with self._lock:
            return list(self._store.keys())

    # ── helpers ────────────────────────────────────────────────────────
    def clear(self) -> None:
        """Wipe the store (useful between runs)."""
        with self._lock:
            self._store.clear()

    def summary(self) -> str:
        """Return a human-readable summary of what is stored."""
        with self._lock:
            lines = ["=== Shared Memory Contents ==="]
            for key, value in self._store.items():
                if isinstance(value, str):
                    lines.append(f"  {key}: {len(value)} chars")
                elif isinstance(value, (list, dict)):
                    lines.append(f"  {key}: {type(value).__name__} with {len(value)} items")
                else:
                    lines.append(f"  {key}: {type(value).__name__}")
            return "\n".join(lines)

    def to_json(self) -> str:
        """Serialize the store to a JSON string (best-effort)."""
        with self._lock:
            try:
                return json.dumps(self._store, indent=2, default=str)
            except TypeError:
                # Fallback for non-serializable objects
                safe = {}
                for k, v in self._store.items():
                    try:
                        json.dumps(v)
                        safe[k] = v
                    except TypeError:
                        safe[k] = str(v)
                return json.dumps(safe, indent=2)

    @classmethod
    def reset(cls) -> None:
        """Destroy the singleton (for testing)."""
        with cls._lock:
            cls._instance = None
