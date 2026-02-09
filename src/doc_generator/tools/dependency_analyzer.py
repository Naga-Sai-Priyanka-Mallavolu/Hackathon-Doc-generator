"""Dependency analysis tool."""

from pathlib import Path
from typing import Dict, List, Set
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
        "Identifies import relationships, package dependencies, and architectural layers. "
        "Returns a dependency graph representation."
    )
    args_schema: type[BaseModel] = DependencyAnalyzerInput

    def _analyze_python_dependencies(self, folder: Path) -> Dict[str, List[str]]:
        """Analyze Python dependencies."""
        dependencies: Dict[str, List[str]] = {}
        
        for py_file in folder.rglob("*.py"):
            if any(part in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'} for part in py_file.parts):
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

    def _run(self, folder_path: str) -> str:
        """Analyze dependencies in the codebase."""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                return f"Error: Folder path '{folder_path}' does not exist."
            
            # Analyze Python dependencies
            dependencies = self._analyze_python_dependencies(folder)
            
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
                    # Check if it's an external dependency (not a local module)
                    if not any(dep.startswith(local) for local in ['src', 'lib', 'utils', 'core']):
                        external_deps.add(dep.split('.')[0])
                    else:
                        internal_deps.add(dep)
            
            result.append(f"\nExternal Dependencies: {len(external_deps)}")
            for dep in sorted(external_deps)[:20]:
                result.append(f"  - {dep}")
            if len(external_deps) > 20:
                result.append(f"  ... and {len(external_deps) - 20} more")
            
            result.append(f"\nInternal Dependencies: {len(internal_deps)}")
            result.append("\nSample dependency relationships:")
            for file_path, deps in list(dependencies.items())[:10]:
                result.append(f"\n  {file_path}:")
                for dep in deps[:5]:
                    result.append(f"    → {dep}")
                if len(deps) > 5:
                    result.append(f"    ... and {len(deps) - 5} more")
            
            result.append("\n" + "=" * 70)
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error during dependency analysis: {str(e)}"
