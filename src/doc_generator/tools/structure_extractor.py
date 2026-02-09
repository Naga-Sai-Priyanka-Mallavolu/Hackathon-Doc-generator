"""Structural extraction tools for code analysis."""

import os
import ast
from pathlib import Path
from typing import Dict, List, Optional, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from doc_generator.models.code_structure import (
    LanguageType,
    FileInfo,
    ModuleInfo,
    ClassInfo,
    FunctionInfo,
    Visibility,
    ProjectStructure,
    LanguageInfo,
    CodeStructure,
)


class StructureExtractorInput(BaseModel):
    """Input schema for StructureExtractor."""
    folder_path: str = Field(..., description="Path to the source code folder to analyze")


class StructureExtractor(BaseTool):
    """Extracts structural information from codebase (AST parsing, file analysis)."""
    
    name: str = "Structure Extractor"
    description: str = (
        "Performs deep structural analysis of a codebase. Extracts classes, functions, "
        "modules, dependencies, and architectural patterns. Returns a structured JSON-like "
        "representation of the code structure. This is deterministic extraction - no LLM interpretation."
    )
    args_schema: type[BaseModel] = StructureExtractorInput

    def _extract_python_structure(self, file_path: Path) -> Optional[ModuleInfo]:
        """Extract structure from a Python file using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            module = ModuleInfo(
                name=file_path.stem,
                path=str(file_path),
                imports=[],
                classes=[],
                functions=[],
            )
            
            # Extract docstring
            if ast.get_docstring(tree):
                module.docstring = ast.get_docstring(tree)
            
            # Use a visitor pattern to track context
            extractor_ref = self  # Reference to outer class methods
            
            class StructureVisitor(ast.NodeVisitor):
                def __init__(self, module_ref, extractor):
                    self.module = module_ref
                    self.extractor = extractor
                    self.in_class = False
                
                def visit_Import(self, node):
                    for alias in node.names:
                        self.module.imports.append(alias.name)
                    self.generic_visit(node)
                
                def visit_ImportFrom(self, node):
                    module_name = node.module or ""
                    for alias in node.names:
                        self.module.imports.append(f"{module_name}.{alias.name}")
                    self.generic_visit(node)
                
                def visit_ClassDef(self, node):
                    class_info = ClassInfo(
                        name=node.name,
                        base_classes=[self.extractor._get_node_name(base) for base in node.bases],
                        docstring=ast.get_docstring(node),
                        line_start=node.lineno,
                        line_end=node.end_lineno if hasattr(node, 'end_lineno') else None,
                    )
                    
                    # Mark we're in a class
                    old_in_class = self.in_class
                    self.in_class = True
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                            method = self.extractor._extract_function(item)
                            class_info.methods.append(method)
                    
                    self.module.classes.append(class_info)
                    self.generic_visit(node)
                    self.in_class = old_in_class
                
                def visit_FunctionDef(self, node):
                    if not self.in_class:
                        func = self.extractor._extract_function(node)
                        self.module.functions.append(func)
                    self.generic_visit(node)
                
                def visit_AsyncFunctionDef(self, node):
                    if not self.in_class:
                        func = self.extractor._extract_function(node)
                        self.module.functions.append(func)
                    self.generic_visit(node)
            
            visitor = StructureVisitor(module, extractor_ref)
            visitor.visit(tree)
            
            return module
            
        except Exception as e:
            return None
    
    def _extract_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract function information from AST node."""
        params = []
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type': self._get_node_name(arg.annotation) if arg.annotation else None,
            }
            params.append(param_info)
        
        return_type = self._get_node_name(node.returns) if node.returns else None
        
        decorators = [self._get_node_name(d) for d in node.decorator_list]
        
        return FunctionInfo(
            name=node.name,
            parameters=params,
            return_type=return_type,
            docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators,
            line_start=node.lineno,
            line_end=node.end_lineno if hasattr(node, 'end_lineno') else None,
        )
    
    def _get_node_name(self, node) -> str:
        """Get string representation of AST node."""
        if node is None:
            return ""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    
    def _detect_entry_points(self, folder: Path) -> List[str]:
        """Detect entry points in the project."""
        entry_points = []
        
        # Common entry point files
        entry_patterns = [
            'main.py', '__main__.py', 'app.py', 'run.py', 'server.py',
            'index.js', 'main.js', 'app.js', 'server.js',
            'main.ts', 'app.ts', 'index.ts',
            'Main.java', 'Application.java',
            'main.go', 'main.rs', 'main.cpp',
        ]
        
        for pattern in entry_patterns:
            for file_path in folder.rglob(pattern):
                entry_points.append(str(file_path.relative_to(folder)))
        
        return entry_points
    
    def _run(self, folder_path: str) -> str:
        """Extract structure from the codebase."""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                return f"Error: Folder path '{folder_path}' does not exist."
            
            project_structure = ProjectStructure(root_path=str(folder))
            
            # Language detection
            language_stats: Dict[LanguageType, LanguageInfo] = {}
            files_by_lang: Dict[LanguageType, List[FileInfo]] = {}
            
            # Walk through directory
            for root, dirs, files in os.walk(folder):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules',
                                                         '.venv', 'venv', 'env', '.env', 'dist',
                                                         'build', '.pytest_cache', '.mypy_cache',
                                                         '.idea', '.vscode', 'target', 'bin', 'obj'}]
                
                for file in files:
                    file_path = Path(root) / file
                    ext = file_path.suffix.lower()
                    
                    # Detect language
                    detected_lang = None
                    for lang, extensions in {
                        LanguageType.PYTHON: ['.py', '.pyw'],
                        LanguageType.JAVASCRIPT: ['.js', '.jsx', '.mjs'],
                        LanguageType.TYPESCRIPT: ['.ts', '.tsx'],
                        LanguageType.JAVA: ['.java'],
                        LanguageType.GO: ['.go'],
                        LanguageType.RUST: ['.rs'],
                    }.items():
                        if ext in extensions:
                            detected_lang = lang
                            break
                    
                    if detected_lang:
                        # Get file stats
                        size = file_path.stat().st_size
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                line_count = len(lines)
                        except Exception:
                            line_count = 0
                        
                        # Extract structure (currently only Python)
                        module = None
                        if detected_lang == LanguageType.PYTHON:
                            module = self._extract_python_structure(file_path)
                        
                        file_info = FileInfo(
                            path=str(file_path.relative_to(folder)),
                            name=file_path.name,
                            language=detected_lang,
                            size_bytes=size,
                            line_count=line_count,
                            module=module,
                            is_test_file=any(pattern in str(file_path).lower() for pattern in ['test', 'spec', '__test__']),
                        )
                        
                        project_structure.files.append(file_info)
                        
                        if detected_lang not in files_by_lang:
                            files_by_lang[detected_lang] = []
                        files_by_lang[detected_lang].append(file_info)
            
            # Build language info
            total_files = len(project_structure.files)
            for lang, file_list in files_by_lang.items():
                total_lines = sum(f.line_count for f in file_list)
                language_info = LanguageInfo(
                    language=lang,
                    file_count=len(file_list),
                    total_lines=total_lines,
                    files=[f.path for f in file_list],
                    percentage=(len(file_list) / total_files * 100) if total_files > 0 else 0,
                )
                project_structure.languages.append(language_info)
            
            # Detect entry points
            project_structure.entry_points = self._detect_entry_points(folder)
            
            # Build summary output
            result = [
                "=" * 70,
                "CODEBASE STRUCTURE ANALYSIS",
                "=" * 70,
                f"\nRoot Path: {folder_path}",
                f"Total Files: {len(project_structure.files)}",
                f"Languages Detected: {len(project_structure.languages)}",
            ]
            
            result.append("\nLanguages:")
            for lang_info in sorted(project_structure.languages, key=lambda x: x.file_count, reverse=True):
                result.append(f"  - {lang_info.language.value}: {lang_info.file_count} files, {lang_info.total_lines:,} lines ({lang_info.percentage:.1f}%)")
            
            result.append(f"\nEntry Points: {len(project_structure.entry_points)}")
            for ep in project_structure.entry_points[:5]:
                result.append(f"  - {ep}")
            
            # Module/Class/Function counts
            total_classes = sum(len(f.module.classes) if f.module else 0 for f in project_structure.files)
            total_functions = sum(
                (len(f.module.functions) if f.module else 0) + 
                sum(len(c.methods) for c in (f.module.classes if f.module else []))
                for f in project_structure.files
            )
            
            result.append(f"\nStructural Elements:")
            result.append(f"  - Classes: {total_classes}")
            result.append(f"  - Functions/Methods: {total_functions}")
            
            result.append("\n" + "=" * 70)
            result.append("Detailed structure available in structured format.")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error during structure extraction: {str(e)}"
