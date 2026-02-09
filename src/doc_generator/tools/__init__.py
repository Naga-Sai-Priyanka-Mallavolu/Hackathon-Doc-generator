"""Tools for code analysis and documentation generation."""

from .language_detector import LanguageDetector
from .structure_extractor import StructureExtractor
from .dependency_analyzer import DependencyAnalyzer

__all__ = [
    "LanguageDetector",
    "StructureExtractor",
    "DependencyAnalyzer",
]
