"""Common structural representation models for code analysis."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class LanguageType(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    UNKNOWN = "unknown"


class Visibility(str, Enum):
    """Code visibility/access modifiers."""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    INTERNAL = "internal"


@dataclass
class FunctionInfo:
    """Information about a function/method."""
    name: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    visibility: Visibility = Visibility.PUBLIC
    is_async: bool = False
    is_static: bool = False
    is_abstract: bool = False
    decorators: List[str] = field(default_factory=list)
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    complexity: Optional[int] = None


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    visibility: Visibility = Visibility.PUBLIC
    is_abstract: bool = False
    is_interface: bool = False
    methods: List[FunctionInfo] = field(default_factory=list)
    properties: List[Dict[str, Any]] = field(default_factory=list)
    line_start: Optional[int] = None
    line_end: Optional[int] = None


@dataclass
class ModuleInfo:
    """Information about a module/namespace."""
    name: str
    path: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class FileInfo:
    """Information about a source code file."""
    path: str
    name: str
    language: LanguageType
    size_bytes: int
    line_count: int
    module: Optional[ModuleInfo] = None
    encoding: str = "utf-8"
    is_entry_point: bool = False
    is_test_file: bool = False


@dataclass
class LanguageInfo:
    """Information about languages detected in the project."""
    language: LanguageType
    file_count: int
    total_lines: int
    files: List[str] = field(default_factory=list)
    percentage: float = 0.0


@dataclass
class ProjectStructure:
    """Complete project structure representation."""
    root_path: str
    languages: List[LanguageInfo] = field(default_factory=list)
    files: List[FileInfo] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    architecture_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeStructure:
    """Unified code structure container."""
    project: ProjectStructure
    timestamp: str = ""
    version: str = "1.0.0"
