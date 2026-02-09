"""Language detection tool for codebase analysis."""

import os
from pathlib import Path
from typing import Dict, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from doc_generator.models.code_structure import LanguageType, LanguageInfo


class LanguageDetectorInput(BaseModel):
    """Input schema for LanguageDetector."""
    folder_path: str = Field(..., description="Path to the source code folder to analyze")


# Language detection patterns
LANGUAGE_EXTENSIONS = {
    LanguageType.PYTHON: ['.py', '.pyw', '.pyx', '.pyi'],
    LanguageType.JAVASCRIPT: ['.js', '.jsx', '.mjs', '.cjs'],
    LanguageType.TYPESCRIPT: ['.ts', '.tsx'],
    LanguageType.JAVA: ['.java'],
    LanguageType.CPP: ['.cpp', '.cc', '.cxx', '.c++', '.hpp', '.h', '.hxx'],
    LanguageType.CSHARP: ['.cs'],
    LanguageType.GO: ['.go'],
    LanguageType.RUST: ['.rs'],
    LanguageType.RUBY: ['.rb'],
    LanguageType.PHP: ['.php', '.php3', '.php4', '.php5', '.phtml'],
    LanguageType.SWIFT: ['.swift'],
    LanguageType.KOTLIN: ['.kt', '.kts'],
}

# Test file patterns
TEST_PATTERNS = [
    'test', 'spec', '__test__', '__tests__', 'tests', 'testing'
]


class LanguageDetector(BaseTool):
    """Detects and classifies programming languages in a codebase."""
    
    name: str = "Language Detector"
    description: str = (
        "Analyzes a codebase folder and detects all programming languages present. "
        "Returns language statistics including file counts, line counts, and file lists. "
        "This tool provides deterministic, evidence-based language classification."
    )
    args_schema: type[BaseModel] = LanguageDetectorInput

    def _run(self, folder_path: str) -> str:
        """Detect languages in the given folder path."""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                return f"Error: Folder path '{folder_path}' does not exist."
            
            if not folder.is_dir():
                return f"Error: '{folder_path}' is not a directory."
            
            # Count files by language
            language_stats: Dict[LanguageType, Dict] = {}
            total_files = 0
            total_lines = 0
            
            # Walk through the directory
            for root, dirs, files in os.walk(folder):
                # Skip common ignored directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 
                                                         '.venv', 'venv', 'env', '.env', 'dist', 
                                                         'build', '.pytest_cache', '.mypy_cache'}]
                
                for file in files:
                    file_path = Path(root) / file
                    ext = file_path.suffix.lower()
                    
                    # Detect language by extension
                    detected_lang = None
                    for lang, extensions in LANGUAGE_EXTENSIONS.items():
                        if ext in extensions:
                            detected_lang = lang
                            break
                    
                    if detected_lang:
                        # Count lines
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                line_count = sum(1 for _ in f)
                        except Exception:
                            line_count = 0
                        
                        if detected_lang not in language_stats:
                            language_stats[detected_lang] = {
                                'files': [],
                                'total_lines': 0,
                                'file_count': 0
                            }
                        
                        language_stats[detected_lang]['files'].append(str(file_path.relative_to(folder)))
                        language_stats[detected_lang]['total_lines'] += line_count
                        language_stats[detected_lang]['file_count'] += 1
                        total_files += 1
                        total_lines += line_count
            
            # Build result
            result_lines = [
                f"Language Detection Results for: {folder_path}",
                f"=" * 60,
                f"Total files analyzed: {total_files}",
                f"Total lines of code: {total_lines:,}",
                f"\nDetected Languages:",
                f"-" * 60
            ]
            
            # Sort by file count
            sorted_langs = sorted(
                language_stats.items(),
                key=lambda x: x[1]['file_count'],
                reverse=True
            )
            
            for lang, stats in sorted_langs:
                percentage = (stats['file_count'] / total_files * 100) if total_files > 0 else 0
                result_lines.append(f"\n{lang.value.upper()}:")
                result_lines.append(f"  Files: {stats['file_count']} ({percentage:.1f}%)")
                result_lines.append(f"  Lines: {stats['total_lines']:,}")
                result_lines.append(f"  Sample files (first 5):")
                for file in stats['files'][:5]:
                    result_lines.append(f"    - {file}")
                if len(stats['files']) > 5:
                    result_lines.append(f"    ... and {len(stats['files']) - 5} more")
            
            if not language_stats:
                result_lines.append("\nNo supported programming languages detected.")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error during language detection: {str(e)}"
