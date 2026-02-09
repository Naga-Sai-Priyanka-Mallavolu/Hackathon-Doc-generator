"""Structural extraction tools for code analysis.

These tools are DATA PROVIDERS - they read and return source code contents
so that LLM agents can analyze them intelligently. The tools handle file I/O,
directory walking, and basic file metadata. The LLM does the understanding.
"""

import os
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Any, Set
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from doc_generator.models.code_structure import LanguageType


class StructureExtractorInput(BaseModel):
    """Input schema for StructureExtractor."""
    folder_path: str = Field(..., description="Path to the source code folder to analyze")


class FileReaderInput(BaseModel):
    """Input schema for FileReader."""
    file_path: str = Field(..., description="Absolute path to the source file to read")


class StructureExtractor(BaseTool):
    """Reads and returns source code from a codebase for LLM analysis.
    
    This tool walks the codebase directory, identifies source files,
    and returns their contents so the LLM agent can analyze the code
    structure, APIs, patterns, and relationships.
    """
    
    name: str = "Structure Extractor"
    description: str = (
        "Reads source code files from a codebase folder and returns their contents. "
        "Returns a listing of all source files with their full source code so you can "
        "analyze classes, methods, API endpoints, annotations, and patterns. "
        "Use this tool to READ the actual code - then YOU (the LLM agent) analyze it."
    )
    args_schema: type[BaseModel] = StructureExtractorInput

    # Directories to skip
    SKIP_DIRS: ClassVar[Set[str]] = {
        '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.env',
        'dist', 'build', '.pytest_cache', '.mypy_cache', '.idea', '.vscode',
        'target', 'bin', 'obj', '.gradle', '.mvn', '.settings'
    }

    # Supported source file extensions
    SOURCE_EXTENSIONS: ClassVar[Set[str]] = {
        '.py', '.java', '.js', '.jsx', '.ts', '.tsx', '.go', '.rs',
        '.rb', '.php', '.cs', '.cpp', '.c', '.h', '.hpp', '.kt', '.swift',
    }

    # Config/build files worth reading
    CONFIG_FILES: ClassVar[Set[str]] = {
        'pom.xml', 'build.gradle', 'build.gradle.kts', 'pyproject.toml',
        'package.json', 'Cargo.toml', 'go.mod', 'requirements.txt',
        'application.properties', 'application.yml', 'application.yaml',
    }

    def _run(self, folder_path: str) -> str:
        """Read source code from the codebase and return contents for LLM analysis."""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                return f"Error: Folder path '{folder_path}' does not exist."

            source_files = []
            config_files = []
            total_lines = 0

            for root, dirs, files in os.walk(folder):
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

                for file_name in sorted(files):
                    file_path = Path(root) / file_name
                    ext = file_path.suffix.lower()
                    rel_path = str(file_path.relative_to(folder))

                    if ext in self.SOURCE_EXTENSIONS:
                        source_files.append((rel_path, file_path))
                    elif file_name in self.CONFIG_FILES:
                        config_files.append((rel_path, file_path))

            # Build output
            result = []
            result.append("=" * 70)
            result.append("CODEBASE SOURCE CODE")
            result.append("=" * 70)
            result.append(f"Root: {folder_path}")
            result.append(f"Source files found: {len(source_files)}")
            result.append(f"Config files found: {len(config_files)}")

            # Read config files first (they're small and give project context)
            if config_files:
                result.append("\n" + "=" * 70)
                result.append("BUILD/CONFIG FILES")
                result.append("=" * 70)
                for rel_path, file_path in config_files:
                    content = self._read_file(file_path, max_lines=100)
                    if content:
                        result.append(f"\n--- {rel_path} ---")
                        result.append(content)

            # Read all source files
            result.append("\n" + "=" * 70)
            result.append("SOURCE FILES")
            result.append("=" * 70)

            for rel_path, file_path in source_files:
                content = self._read_file(file_path, max_lines=500)
                if content:
                    line_count = content.count('\n') + 1
                    total_lines += line_count
                    result.append(f"\n--- {rel_path} ({line_count} lines) ---")
                    result.append(content)

            result.append(f"\n{'=' * 70}")
            result.append(f"SUMMARY: {len(source_files)} source files, {total_lines} total lines")
            result.append("=" * 70)

            return "\n".join(result)

        except Exception as e:
            return f"Error during structure extraction: {str(e)}"

    def _read_file(self, file_path: Path, max_lines: int = 500) -> Optional[str]:
        """Read file contents, truncating if too long."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if len(lines) > max_lines:
                content = ''.join(lines[:max_lines])
                content += f"\n... (truncated, {len(lines) - max_lines} more lines)"
                return content
            return ''.join(lines)
        except Exception:
            return None


class FileReader(BaseTool):
    """Reads a single source file and returns its full contents."""

    name: str = "File Reader"
    description: str = (
        "Reads a single source file and returns its full contents. "
        "Use this when you need to read a specific file in detail. "
        "Provide the absolute file path."
    )
    args_schema: type[BaseModel] = FileReaderInput

    def _run(self, file_path: str) -> str:
        """Read a single file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File '{file_path}' does not exist."
            if not path.is_file():
                return f"Error: '{file_path}' is not a file."

            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            return f"--- {path.name} ({len(content.splitlines())} lines) ---\n{content}"

        except Exception as e:
            return f"Error reading file: {str(e)}"
