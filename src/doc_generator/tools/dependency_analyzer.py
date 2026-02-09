"""Dependency analysis tool."""

import re
from pathlib import Path
from typing import ClassVar, Dict, List, Set
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DependencyAnalyzerInput(BaseModel):
    """Input schema for DependencyAnalyzer."""
    folder_path: str = Field(..., description="Path to the source code folder to analyze")


class DependencyAnalyzer(BaseTool):
    """Analyzes dependencies and relationships between modules/files."""
    
    name: str = "Dependency Analyzer"
    description: str = (
        "Analyzes dependencies between modules, files, and components in a codebase. "
        "Identifies import relationships for Python and Java, package dependencies, "
        "and architectural layers. Returns a dependency report for LLM analysis."
    )
    args_schema: type[BaseModel] = DependencyAnalyzerInput

    SKIP_DIRS: ClassVar[Set[str]] = {
        '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.env',
        'dist', 'build', '.pytest_cache', '.mypy_cache', '.idea', '.vscode',
        'target', 'bin', 'obj', '.gradle', '.mvn', '.settings'
    }

    def _analyze_python_dependencies(self, folder: Path) -> Dict[str, List[str]]:
        """Analyze Python dependencies."""
        dependencies: Dict[str, List[str]] = {}
        
        for py_file in folder.rglob("*.py"):
            if any(part in self.SKIP_DIRS for part in py_file.parts):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                import ast
                tree = ast.parse(content, filename=str(py_file))
                
                file_deps = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_deps.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_deps.append(node.module)
                
                if file_deps:
                    rel_path = str(py_file.relative_to(folder))
                    dependencies[rel_path] = file_deps
                    
            except Exception:
                continue
        
        return dependencies

    def _analyze_java_dependencies(self, folder: Path) -> Dict[str, List[str]]:
        """Analyze Java dependencies from import statements."""
        dependencies: Dict[str, List[str]] = {}

        for java_file in folder.rglob("*.java"):
            if any(part in self.SKIP_DIRS for part in java_file.parts):
                continue

            try:
                with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                file_deps = []
                for match in re.finditer(r'import\s+([\w.*]+)\s*;', content):
                    file_deps.append(match.group(1))

                if file_deps:
                    rel_path = str(java_file.relative_to(folder))
                    dependencies[rel_path] = file_deps

            except Exception:
                continue

        return dependencies

    def _run(self, folder_path: str) -> str:
        """Analyze dependencies in the codebase."""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                return f"Error: Folder path '{folder_path}' does not exist."
            
            # Analyze both Python and Java dependencies
            py_deps = self._analyze_python_dependencies(folder)
            java_deps = self._analyze_java_dependencies(folder)
            dependencies = {**py_deps, **java_deps}
            
            # Build result
            result = [
                "=" * 70,
                "DEPENDENCY ANALYSIS",
                "=" * 70,
                f"\nAnalyzed: {folder_path}",
                f"Files with dependencies: {len(dependencies)}",
            ]
            
            # Count dependency types
            external_deps: Set[str] = set()
            internal_deps: Set[str] = set()
            
            for file_path, deps in dependencies.items():
                for dep in deps:
                    top_level = dep.split('.')[0]
                    # Heuristic: if it starts with common project packages, it's internal
                    if any(dep.startswith(prefix) for prefix in ['com.', 'org.', 'net.', 'io.']):
                        # Check if it's a well-known external package
                        if any(dep.startswith(ext) for ext in [
                            'org.springframework', 'javax.', 'jakarta.',
                            'com.fasterxml', 'org.hibernate', 'org.apache',
                            'com.google', 'org.junit', 'org.slf4j', 'org.mockito'
                        ]):
                            external_deps.add(dep)
                        else:
                            internal_deps.add(dep)
                    elif top_level in {'java', 'javax', 'jakarta'}:
                        external_deps.add(dep)
                    else:
                        external_deps.add(top_level)
            
            result.append(f"\nExternal Dependencies: {len(external_deps)}")
            for dep in sorted(external_deps)[:30]:
                result.append(f"  - {dep}")
            if len(external_deps) > 30:
                result.append(f"  ... and {len(external_deps) - 30} more")
            
            result.append(f"\nInternal Dependencies: {len(internal_deps)}")
            for dep in sorted(internal_deps)[:20]:
                result.append(f"  - {dep}")
            
            result.append("\nPer-file dependency details:")
            for file_path, deps in sorted(dependencies.items()):
                result.append(f"\n  {file_path}:")
                for dep in deps[:10]:
                    result.append(f"    → {dep}")
                if len(deps) > 10:
                    result.append(f"    ... and {len(deps) - 10} more")
            
            result.append("\n" + "=" * 70)
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error during dependency analysis: {str(e)}"
