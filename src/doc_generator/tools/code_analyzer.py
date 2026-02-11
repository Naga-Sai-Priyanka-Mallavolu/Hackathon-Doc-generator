"""
Code Analyzer Tool – the first agent in the pipeline.

Parses the target codebase, builds AST-level data for every source file,
and stores everything in SharedMemory so downstream agents never need to
re-read or re-parse the code.

Stored keys in SharedMemory:
    project_root        – absolute path to the codebase
    language            – primary detected language
    file_tree           – list of relative paths
    source_files        – dict  {rel_path: full_source_code}
    config_files        – dict  {rel_path: content}
    ast_data            – dict  {rel_path: parsed AST info}
    imports             – dict  {rel_path: [import strings]}
    classes             – dict  {rel_path: [class dicts]}
    functions           – dict  {rel_path: [function dicts]}
    annotations         – dict  {rel_path: [annotation strings]}
    entry_points        – list  of entry-point file paths
    packages            – dict  of package/build metadata
"""

import ast as python_ast
import os
import re
import json
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Set

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from doc_generator.tools.shared_memory import SharedMemory


# ── Input schema ───────────────────────────────────────────────────────
class CodeAnalyzerInput(BaseModel):
    """Input schema for CodeAnalyzer."""
    folder_path: str = Field(..., description="Absolute path to the codebase folder to analyze")


# ── Language detection helpers ─────────────────────────────────────────
LANG_EXTENSIONS: Dict[str, List[str]] = {
    "java":       [".java"],
    "python":     [".py", ".pyw"],
    "javascript": [".js", ".jsx", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "go":         [".go"],
    "rust":       [".rs"],
    "ruby":       [".rb"],
    "php":        [".php"],
    "csharp":     [".cs"],
    "cpp":        [".cpp", ".cc", ".cxx", ".h", ".hpp"],
    "kotlin":     [".kt", ".kts"],
    "swift":      [".swift"],
}

SOURCE_EXTENSIONS: Set[str] = {ext for exts in LANG_EXTENSIONS.values() for ext in exts}

CONFIG_FILENAMES: Set[str] = {
    "pom.xml", "build.gradle", "build.gradle.kts",
    "pyproject.toml", "package.json", "Cargo.toml", "go.mod",
    "requirements.txt", "setup.py", "setup.cfg",
    "application.properties", "application.yml", "application.yaml",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", "Makefile", "Gemfile", "composer.json",
}

SKIP_DIRS: Set[str] = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".env", "dist", "build", ".pytest_cache", ".mypy_cache",
    ".idea", ".vscode", "target", "bin", "obj", ".gradle", ".mvn",
    ".settings", ".next", ".nuxt", "coverage",
}


# ── Java-specific AST-like parser ─────────────────────────────────────
def _parse_java_file(content: str) -> Dict[str, Any]:
    """Extract structural info from a Java source file."""
    info: Dict[str, Any] = {
        "package": None,
        "imports": [],
        "classes": [],
        "interfaces": [],
        "annotations": [],
        "methods": [],
    }

    # Package
    m = re.search(r"^package\s+([\w.]+)\s*;", content, re.MULTILINE)
    if m:
        info["package"] = m.group(1)

    # Imports
    info["imports"] = re.findall(r"^import\s+([\w.*]+)\s*;", content, re.MULTILINE)

    # Annotations (class-level and method-level)
    info["annotations"] = re.findall(r"@(\w+)(?:\([^)]*\))?", content)

    # Classes / interfaces
    for m in re.finditer(
        r"(?:public|private|protected)?\s*(?:abstract\s+)?(?:class|interface|enum)\s+(\w+)",
        content,
    ):
        info["classes"].append(m.group(1))

    # Methods
    method_pattern = re.compile(
        r"(?:@\w+(?:\([^)]*\))?\s*)*"                       # annotations
        r"(?:public|private|protected)\s+"                    # visibility
        r"(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?"   # modifiers
        r"([\w<>\[\]?,\s]+?)\s+"                              # return type
        r"(\w+)\s*"                                           # method name
        r"\(([^)]*)\)",                                       # params
        re.MULTILINE,
    )
    for m in method_pattern.finditer(content):
        return_type = m.group(1).strip()
        name = m.group(2).strip()
        raw_params = m.group(3).strip()
        params = []
        if raw_params:
            for p in raw_params.split(","):
                parts = p.strip().rsplit(None, 1)
                if len(parts) == 2:
                    params.append({"type": parts[0], "name": parts[1]})
                elif parts:
                    params.append({"type": "unknown", "name": parts[0]})
        info["methods"].append({
            "name": name,
            "return_type": return_type,
            "parameters": params,
        })

    return info


# ── Python AST parser ──────────────────────────────────────────────────
def _parse_python_file(content: str, filepath: str) -> Dict[str, Any]:
    """Extract structural info from a Python source file using the ast module."""
    info: Dict[str, Any] = {
        "imports": [],
        "classes": [],
        "functions": [],
        "decorators": [],
    }
    try:
        tree = python_ast.parse(content, filename=filepath)
    except SyntaxError:
        return info

    # Collect class-level method nodes so we can skip them later
    class_method_ids: set = set()

    for node in python_ast.walk(tree):
        if isinstance(node, python_ast.Import):
            for alias in node.names:
                info["imports"].append(alias.name)
        elif isinstance(node, python_ast.ImportFrom):
            if node.module:
                info["imports"].append(node.module)
        elif isinstance(node, python_ast.ClassDef):
            cls = {
                "name": node.name,
                "bases": [_node_name(b) for b in node.bases],
                "methods": [],
                "decorators": [_node_name(d) for d in node.decorator_list],
                "docstring": python_ast.get_docstring(node) or "",
                "line_start": node.lineno,
            }
            for item in node.body:
                if isinstance(item, (python_ast.FunctionDef, python_ast.AsyncFunctionDef)):
                    cls["methods"].append(_extract_py_func(item))
                    class_method_ids.add(id(item))
            info["classes"].append(cls)

    # Second pass: collect only top-level functions (not class methods)
    for node in python_ast.iter_child_nodes(tree):
        if isinstance(node, (python_ast.FunctionDef, python_ast.AsyncFunctionDef)):
            if id(node) not in class_method_ids:
                info["functions"].append(_extract_py_func(node))

    return info


def _extract_py_func(node) -> Dict[str, Any]:
    """Extract function/method info from a Python AST node."""
    params = []
    for arg in node.args.args:
        params.append({
            "name": arg.arg,
            "type": _node_name(arg.annotation) if arg.annotation else "unknown",
        })
    return {
        "name": node.name,
        "parameters": params,
        "return_type": _node_name(node.returns) if node.returns else "unknown",
        "decorators": [_node_name(d) for d in node.decorator_list],
        "docstring": python_ast.get_docstring(node) or "",
        "is_async": isinstance(node, python_ast.AsyncFunctionDef),
        "line_start": node.lineno,
    }


def _node_name(node) -> str:
    """Best-effort name extraction from an AST node."""
    if node is None:
        return "unknown"
    if isinstance(node, python_ast.Name):
        return node.id
    if isinstance(node, python_ast.Attribute):
        return f"{_node_name(node.value)}.{node.attr}"
    if isinstance(node, python_ast.Constant):
        return str(node.value)
    if isinstance(node, python_ast.Subscript):
        return f"{_node_name(node.value)}[{_node_name(node.slice)}]"
    return python_ast.dump(node)


# ── Generic / JS / TS regex-based parser ───────────────────────────────
def _parse_generic_file(content: str) -> Dict[str, Any]:
    """Regex-based extraction for JS/TS/Go/etc."""
    info: Dict[str, Any] = {
        "imports": [],
        "classes": [],
        "functions": [],
        "exports": [],
    }
    # ES imports
    info["imports"] = re.findall(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", content)
    # require
    info["imports"] += re.findall(r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", content)
    # Classes
    info["classes"] = re.findall(r"class\s+(\w+)", content)
    # Functions
    info["functions"] = re.findall(r"(?:function|const|let|var)\s+(\w+)\s*(?:=\s*(?:async\s*)?\(|[\(])", content)
    # Exports
    info["exports"] = re.findall(r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)", content)
    return info


# ── Main tool ──────────────────────────────────────────────────────────
class CodeAnalyzer(BaseTool):
    """
    Parses the entire codebase, builds AST data, and stores everything in
    SharedMemory so that downstream agents can read without re-parsing.
    """

    name: str = "Code Analyzer"
    description: str = (
        "Parses a codebase folder: detects language, reads every source & config file, "
        "builds AST-level structural data (classes, methods, imports, annotations), "
        "and stores everything in shared memory. Returns a summary of what was stored. "
        "Downstream agents should use the 'Shared Memory Reader' tool to access the data."
    )
    args_schema: type[BaseModel] = CodeAnalyzerInput

    SKIP_DIRS: ClassVar[Set[str]] = SKIP_DIRS
    SOURCE_EXTENSIONS: ClassVar[Set[str]] = SOURCE_EXTENSIONS
    CONFIG_FILENAMES: ClassVar[Set[str]] = CONFIG_FILENAMES

    def _run(self, folder_path: str) -> str:
        """Parse codebase and populate SharedMemory."""
        mem = SharedMemory()
        mem.clear()  # fresh run

        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return f"Error: '{folder_path}' is not a valid directory."

        mem.set("project_root", str(folder.absolute()))

        # ── Walk the tree ──────────────────────────────────────────────
        source_files: Dict[str, str] = {}
        config_files: Dict[str, str] = {}
        file_tree: List[str] = []
        lang_counts: Dict[str, int] = {}

        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for fname in sorted(files):
                fpath = Path(root) / fname
                rel = str(fpath.relative_to(folder))
                file_tree.append(rel)
                ext = fpath.suffix.lower()

                # Detect language
                for lang, exts in LANG_EXTENSIONS.items():
                    if ext in exts:
                        lang_counts[lang] = lang_counts.get(lang, 0) + 1

                # Read source files
                if ext in self.SOURCE_EXTENSIONS:
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        source_files[rel] = content
                    except Exception:
                        pass

                # Read config files
                if fname in self.CONFIG_FILENAMES:
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        config_files[rel] = content
                    except Exception:
                        pass

        # Primary language
        primary_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "unknown"
        mem.set("language", primary_lang)
        mem.set("language_stats", lang_counts)
        mem.set("file_tree", file_tree)
        mem.set("source_files", source_files)
        mem.set("config_files", config_files)

        # ── Parse AST per file ─────────────────────────────────────────
        ast_data: Dict[str, Any] = {}
        all_imports: Dict[str, List[str]] = {}
        all_classes: Dict[str, List[Dict]] = {}
        all_functions: Dict[str, List[Dict]] = {}
        all_annotations: Dict[str, List[str]] = {}
        entry_points: List[str] = []

        for rel, content in source_files.items():
            ext = Path(rel).suffix.lower()

            if ext in (".py", ".pyw"):
                parsed = _parse_python_file(content, rel)
            elif ext == ".java":
                parsed = _parse_java_file(content)
            else:
                parsed = _parse_generic_file(content)

            ast_data[rel] = parsed
            all_imports[rel] = parsed.get("imports", [])
            all_classes[rel] = parsed.get("classes", [])
            all_functions[rel] = parsed.get("functions", parsed.get("methods", []))
            all_annotations[rel] = parsed.get("annotations", parsed.get("decorators", []))

            # Heuristic entry-point detection
            lower = rel.lower()
            if any(kw in lower for kw in ("main", "app", "index", "server", "bootstrap")):
                entry_points.append(rel)
            # Java: class with main method
            if ext == ".java" and "public static void main" in content:
                entry_points.append(rel)
            # Python: if __name__ == "__main__"
            if ext in (".py", ".pyw") and '__name__' in content and '__main__' in content:
                entry_points.append(rel)

        mem.set("ast_data", ast_data)
        mem.set("imports", all_imports)
        mem.set("classes", all_classes)
        mem.set("functions", all_functions)
        mem.set("annotations", all_annotations)
        mem.set("entry_points", list(set(entry_points)))

        # ── Package / build metadata ───────────────────────────────────
        packages: Dict[str, Any] = {}
        for rel, content in config_files.items():
            fname = Path(rel).name
            if fname == "pom.xml":
                packages["build_tool"] = "maven"
                packages["pom_xml"] = content
            elif fname.startswith("build.gradle"):
                packages["build_tool"] = "gradle"
                packages["build_gradle"] = content
            elif fname == "package.json":
                packages["build_tool"] = "npm"
                try:
                    packages["package_json"] = json.loads(content)
                except json.JSONDecodeError:
                    packages["package_json_raw"] = content
            elif fname == "pyproject.toml":
                packages["build_tool"] = "python"
                packages["pyproject_toml"] = content
            elif fname == "requirements.txt":
                packages["requirements_txt"] = content
            elif fname in ("application.properties", "application.yml", "application.yaml"):
                packages.setdefault("app_config", {})[fname] = content
            elif fname in ("Dockerfile", "docker-compose.yml", "docker-compose.yaml"):
                packages.setdefault("docker", {})[fname] = content

        mem.set("packages", packages)

        # ── Build summary ──────────────────────────────────────────────
        total_classes = sum(len(v) for v in all_classes.values())
        total_functions = sum(len(v) for v in all_functions.values())
        total_imports = sum(len(v) for v in all_imports.values())

        summary = (
            f"Code Analysis Complete\n"
            f"{'=' * 60}\n"
            f"Project root : {folder.absolute()}\n"
            f"Primary lang : {primary_lang}\n"
            f"Language stats: {json.dumps(lang_counts)}\n"
            f"Source files  : {len(source_files)}\n"
            f"Config files  : {len(config_files)}\n"
            f"Total classes : {total_classes}\n"
            f"Total funcs   : {total_functions}\n"
            f"Total imports : {total_imports}\n"
            f"Entry points  : {entry_points}\n"
            f"{'=' * 60}\n"
            f"\nAll data has been stored in shared memory. "
            f"Downstream agents should use the 'Shared Memory Reader' tool "
            f"with the appropriate key to access parsed data.\n"
            f"\nAvailable memory keys: {mem.keys()}"
        )
        return summary
