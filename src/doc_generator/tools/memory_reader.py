"""
Shared Memory Reader Tool – used by all downstream agents.

Allows agents to read parsed code data from SharedMemory without
re-reading or re-parsing the codebase.

Available keys (populated by Code Analyzer):
    project_root, language, language_stats, file_tree,
    source_files, config_files, ast_data, imports, classes,
    functions, annotations, entry_points, packages
"""

import json
from typing import Any

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from doc_generator.tools.shared_memory import SharedMemory


class MemoryReaderInput(BaseModel):
    """Input schema for SharedMemoryReader."""
    key: str = Field(
        ...,
        description=(
            "The memory key to read. Available keys: "
            "project_root, language, language_stats, file_tree, "
            "source_files, config_files, ast_data, imports, classes, "
            "functions, annotations, entry_points, packages. "
            "Use 'all_keys' to list available keys. "
            "Use 'summary' for a quick overview."
        ),
    )
    sub_key: str = Field(
        default="",
        description=(
            "Optional sub-key for nested dicts. For example if key='source_files', "
            "sub_key can be a relative file path like 'src/main/java/App.java' "
            "to get just that file's content."
        ),
    )


class SharedMemoryReader(BaseTool):
    """Reads data from the shared in-memory store populated by Code Analyzer."""

    name: str = "Shared Memory Reader"
    description: str = (
        "Reads parsed code data from shared memory. The Code Analyzer agent "
        "has already parsed the entire codebase and stored AST data, source code, "
        "imports, classes, functions, annotations, config files, and more. "
        "Use key='all_keys' to see what is available, or key='summary' for an overview. "
        "Use a specific key like 'classes', 'functions', 'imports', 'ast_data', "
        "'source_files', 'config_files', 'packages', 'entry_points', etc. "
        "Optionally provide sub_key for a specific file path within a dict."
    )
    args_schema: type[BaseModel] = MemoryReaderInput

    def _run(self, key: str, sub_key: str = "") -> str:
        """Read from shared memory."""
        mem = SharedMemory()

        # Special meta-keys
        if key == "all_keys":
            keys = mem.keys()
            return f"Available memory keys: {json.dumps(keys, indent=2)}"

        if key == "summary":
            return mem.summary()

        value = mem.get(key)
        if value is None:
            available = mem.keys()
            return (
                f"Key '{key}' not found in shared memory.\n"
                f"Available keys: {json.dumps(available)}"
            )

        # Sub-key access for nested dicts
        if sub_key and isinstance(value, dict):
            sub_value = value.get(sub_key)
            if sub_value is None:
                # Try partial match
                matches = [k for k in value.keys() if sub_key in k]
                if matches:
                    return (
                        f"Exact sub_key '{sub_key}' not found. "
                        f"Partial matches: {json.dumps(matches[:20])}"
                    )
                return (
                    f"Sub-key '{sub_key}' not found under '{key}'.\n"
                    f"Available sub-keys (first 30): {json.dumps(list(value.keys())[:30])}"
                )
            return _serialize(sub_value)

        return _serialize(value)


def _serialize(value: Any) -> str:
    """Best-effort serialization to string."""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, indent=2, default=str)
    except TypeError:
        return str(value)
