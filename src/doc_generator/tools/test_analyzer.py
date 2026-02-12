"""
Test Analyzer Tool for Documentation Generator

Analyzes test files to extract testing information,
coverage details, and generate test documentation.
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


def has_test_files(folder_path: str) -> bool:
    """
    Check if the folder contains any test files.
    
    Args:
        folder_path: Path to the folder to check
        
    Returns:
        True if test files exist, False otherwise
    """
    folder = Path(folder_path)
    
    # Common test file patterns
    test_patterns = [
        "**/test_*.py",
        "**/*_test.py",
        "**/tests/**/*.py",
        "**/test/**/*.py",
        "**/*Test.java",
        "**/test/**/*.java",
        "**/tests/**/*.java",
        "**/*.test.js",
        "**/*.test.ts",
        "**/test/**/*.js",
        "**/test/**/*.ts",
        "**/tests/**/*.js",
        "**/tests/**/*.ts",
        "**/__tests__/**/*.js",
        "**/__tests__/**/*.ts"
    ]
    
    for pattern in test_patterns:
        if list(folder.glob(pattern)):
            return True
    
    return False


class TestInfo(BaseModel):
    """Information about a test file or test case."""
    file_path: str
    file_type: str
    file_description: Optional[str] = None  # Description of what the test file covers
    test_framework: Optional[str] = None
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    setup_methods: List[str] = Field(default_factory=list)
    teardown_methods: List[str] = Field(default_factory=list)
    fixtures: List[str] = Field(default_factory=list)
    mocks: List[str] = Field(default_factory=list)
    coverage_areas: List[str] = Field(default_factory=list)
    test_types: List[str] = Field(default_factory=list)  # unit, integration, e2e
    dependencies: List[str] = Field(default_factory=list)


class TestSummary(BaseModel):
    """Summary of all tests in the project."""
    total_test_files: int
    total_test_cases: int
    test_frameworks: List[str]
    test_types: Dict[str, int]
    coverage_areas: List[str]
    setup_commands: List[str]
    test_commands: List[str]
    test_structure: Dict[str, List[str]]


class TestAnalyzer:
    """
    Analyzes test files to extract testing information.
    
    Supports:
    - Python (unittest, pytest, unittest.mock)
    - Java (JUnit, Mockito, Spring Test)
    - JavaScript/Node.js (Jest, Mocha, Chai)
    - General test patterns
    """

    def __init__(self):
        """Initialize the test analyzer."""
        self.test_patterns = {
            'python': [
                'test_*.py', '*_test.py', 'tests/*.py', 'test/**/*.py',
                'conftest.py', 'pytest.ini', 'tox.ini'
            ],
            'java': [
                '*Test.java', '*Tests.java', '**/Test*.java',
                'src/test/java/**/*.java'
            ],
            'javascript': [
                '*.test.js', '*.spec.js', 'test/**/*.js',
                'tests/**/*.js', '__tests__/**/*.js'
            ],
            'typescript': [
                '*.test.ts', '*.spec.ts', 'test/**/*.ts',
                'tests/**/*.ts', '__tests__/**/*.ts'
            ],
            'config': [
                'jest.config.js', 'jest.config.json', 'mocha.opts',
                'karma.conf.js', 'pytest.ini', 'tox.ini'
            ]
        }

    def analyze_test_file(self, file_path: str) -> TestInfo:
        """
        Analyze a single test file.
        
        Args:
            file_path: Path to the test file
            
        Returns:
            TestInfo with extracted data
        """
        path = Path(file_path)
        if not path.exists():
            return TestInfo(file_path=file_path, file_type='unknown')
        
        file_ext = path.suffix.lower()
        file_name = path.name.lower()
        
        if file_ext == '.py':
            return self._analyze_python_test(file_path)
        elif file_ext == '.java':
            return self._analyze_java_test(file_path)
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            return self._analyze_javascript_test(file_path)
        else:
            return TestInfo(file_path=file_path, file_type=file_ext)

    def _analyze_python_test(self, file_path: str) -> TestInfo:
        """Analyze Python test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            info = TestInfo(
                file_path=file_path,
                file_type='python'
            )
            
            # Detect test framework
            if 'import unittest' in content or 'from unittest' in content:
                info.test_framework = 'unittest'
            elif 'import pytest' in content or 'from pytest' in content:
                info.test_framework = 'pytest'
            elif 'import nose' in content or 'from nose' in content:
                info.test_framework = 'nose'
            
            # Parse AST for more detailed analysis
            try:
                tree = ast.parse(content)
                # Extract file-level docstring
                if (tree.body and 
                    isinstance(tree.body[0], ast.Expr) and 
                    isinstance(tree.body[0].value, ast.Constant) and 
                    isinstance(tree.body[0].value.value, str)):
                    info.file_description = tree.body[0].value.value.strip()
                elif ast.get_docstring(tree):
                    info.file_description = ast.get_docstring(tree).strip()
                
                self._extract_python_test_info(tree, info)
            except SyntaxError:
                # Fallback to regex analysis
                self._extract_python_test_info_regex(content, info)
            
            # Extract test types from file path and content
            if 'integration' in file_path.lower() or 'integration' in content.lower():
                info.test_types.append('integration')
            elif 'e2e' in file_path.lower() or 'end_to_end' in content.lower():
                info.test_types.append('e2e')
            else:
                info.test_types.append('unit')
            
            return info
            
        except Exception as e:
            return TestInfo(file_path=file_path, file_type='python')

    def _extract_python_test_info(self, tree: ast.AST, info: TestInfo):
        """Extract test information from Python AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Test methods
                if node.name.startswith('test_'):
                    # Extract docstring as description
                    description = None
                    if (node.body and 
                        isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        description = node.body[0].value.value.strip()
                    
                    test_case = {
                        'name': node.name,
                        'line': node.lineno,
                        'description': description,
                        'docstring': ast.get_docstring(node) or '',
                    }
                    
                    # Extract test description from docstring
                    if test_case['docstring']:
                        test_case['description'] = test_case['docstring'].split('\n')[0]
                    
                    info.test_cases.append(test_case)
                
                # Setup/teardown methods
                elif node.name in ['setUp', 'setUpClass', 'setUpModule']:
                    info.setup_methods.append(node.name)
                elif node.name in ['tearDown', 'tearDownClass', 'tearDownModule']:
                    info.teardown_methods.append(node.name)
                elif node.name.startswith('test_') and 'setup' in node.name.lower():
                    info.setup_methods.append(node.name)
                elif node.name.startswith('test_') and 'teardown' in node.name.lower():
                    info.teardown_methods.append(node.name)
            
            elif isinstance(node, ast.ClassDef):
                # Test classes
                if node.name.startswith('Test') or 'Test' in node.name:
                    info.coverage_areas.append(node.name.replace('Test', ''))
            
            elif isinstance(node, ast.Import):
                # Test dependencies
                for alias in node.names:
                    name = alias.name
                    if 'test' in name.lower() or 'mock' in name.lower() or 'pytest' in name.lower():
                        info.dependencies.append(name)
            
            elif isinstance(node, ast.ImportFrom):
                # Test dependencies from modules
                if node.module:
                    module = node.module
                    if 'test' in module.lower() or 'mock' in module.lower() or 'pytest' in module.lower():
                        info.dependencies.append(module)
                    elif module == 'unittest.mock':
                        info.mocks.extend([alias.name for alias in node.names if alias.name])
                    elif module == 'pytest':
                        info.fixtures.extend([alias.name for alias in node.names if alias.name])

    def _extract_python_test_info_regex(self, content: str, info: TestInfo):
        """Extract test information using regex (fallback)."""
        # Find test functions
        test_pattern = r'def\s+(test_[a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        for match in re.finditer(test_pattern, content):
            test_name = match.group(1)
            info.test_cases.append({'name': test_name})
        
        # Find imports
        import_pattern = r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
        for match in re.finditer(import_pattern, content):
            module = match.group(1)
            if any(keyword in module.lower() for keyword in ['test', 'mock', 'pytest', 'unittest']):
                info.dependencies.append(module)

    def _analyze_java_test(self, file_path: str) -> TestInfo:
        """Analyze Java test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            info = TestInfo(
                file_path=file_path,
                file_type='java'
            )
            
            # Detect test framework
            if 'import org.junit.' in content:
                info.test_framework = 'JUnit'
            elif 'import org.testng.' in content:
                info.test_framework = 'TestNG'
            
            # Extract class-level Javadoc comment
            class_pattern = r'/\*\*\s*\n(.*?)\s*\*/\s*public\s+class\s+(\w+)'
            class_match = re.search(class_pattern, content, re.DOTALL)
            if class_match:
                javadoc = class_match.group(1).strip()
                # Clean up Javadoc
                javadoc = re.sub(r'\s*\*\s?', ' ', javadoc)
                javadoc = re.sub(r'\s+', ' ', javadoc).strip()
                info.file_description = javadoc
            
            # Extract test methods with Javadoc
            test_method_pattern = r'(/\*\*\s*\n(.*?)\s*\*/\s*)?@Test\s+public\s+(\w+)\s*\([^)]*\)\s*\{'
            for match in re.finditer(test_method_pattern, content, re.DOTALL):
                method_name = match.group(3)
                javadoc = match.group(2)
                
                # Clean up Javadoc
                description = None
                if javadoc:
                    description = javadoc.strip()
                    description = re.sub(r'\s*\*\s?', ' ', description)
                    description = re.sub(r'\s+', ' ', description).strip()
                    # Take only the first sentence
                    if '.' in description:
                        description = description.split('.')[0] + '.'
                
                test_case = {
                    'name': method_name,
                    'description': description
                }
                info.test_cases.append(test_case)
            
            # Find setup/teardown methods
            setup_pattern = r'@(?:Before|BeforeEach|BeforeAll|BeforeClass)'
            teardown_pattern = r'@(?:After|AfterEach|AfterAll|AfterClass)'
            
            if re.search(setup_pattern, content):
                info.setup_methods.append('setup')
            if re.search(teardown_pattern, content):
                info.teardown_methods.append('teardown')
            
            # Find mocks
            mock_pattern = r'@Mock|@Spy|@InjectMocks'
            if re.search(mock_pattern, content):
                info.mocks.append('Mockito')
            
            # Find test class
            class_pattern = r'public\s+class\s+(\w*(?:Test|Tests)?)'
            class_match = re.search(class_pattern, content)
            if class_match:
                info.coverage_areas.append(class_match.group(1))
            
            # Determine test type
            if 'integration' in file_path.lower() or 'IntegrationTest' in content:
                info.test_types.append('integration')
            elif 'e2e' in file_path.lower() or 'E2ETest' in content:
                info.test_types.append('e2e')
            else:
                info.test_types.append('unit')
            
            return info
            
        except Exception as e:
            return TestInfo(file_path=file_path, file_type='java')

    def _analyze_javascript_test(self, file_path: str) -> TestInfo:
        """Analyze JavaScript/TypeScript test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            info = TestInfo(
                file_path=file_path,
                file_type='javascript'
            )
            
            # Detect test framework
            if "require('jest')" in content or "import.*from.*jest" in content or 'describe(' in content:
                info.test_framework = 'Jest'
            elif "require('mocha')" in content or "import.*from.*mocha" in content:
                info.test_framework = 'Mocha'
            
            # Find test cases
            test_patterns = [
                r"it\s*\(\s*['\"]([^'\"]+)['\"]",
                r"test\s*\(\s*['\"]([^'\"]+)['\"]",
                r"specify\s*\(\s*['\"]([^'\"]+)['\"]"
            ]
            
            for pattern in test_patterns:
                for match in re.finditer(pattern, content):
                    test_name = match.group(1)
                    info.test_cases.append({'name': test_name, 'description': test_name})
            
            # Find describe blocks (test suites)
            describe_pattern = r"describe\s*\(\s*['\"]([^'\"]+)['\"]"
            for match in re.finditer(describe_pattern, content):
                suite_name = match.group(1)
                info.coverage_areas.append(suite_name)
            
            # Find setup/teardown
            if re.search(r'beforeEach|beforeAll', content):
                info.setup_methods.append('setup')
            if re.search(r'afterEach|afterAll', content):
                info.teardown_methods.append('teardown')
            
            # Find mocks
            if re.search(r'jest\.mock|mock|sinon', content):
                info.mocks.append('mock')
            
            # Determine test type
            if 'integration' in file_path.lower() or 'e2e' in file_path.lower():
                info.test_types.append('integration' if 'integration' in file_path.lower() else 'e2e')
            else:
                info.test_types.append('unit')
            
            return info
            
        except Exception as e:
            return TestInfo(file_path=file_path, file_type='javascript')

    def analyze_all_tests(self, folder_path: str) -> Tuple[List[TestInfo], TestSummary]:
        """
        Analyze all test files in a folder.
        
        Args:
            folder_path: Path to the folder to scan
            
        Returns:
            Tuple of (list of TestInfo, TestSummary)
        """
        folder = Path(folder_path)
        test_files = []
        
        # Find all test files
        for file_type, patterns in self.test_patterns.items():
            for pattern in patterns:
                matches = folder.glob(pattern)
                for match in matches:
                    if match.is_file():
                        test_files.append(str(match))
        
        # Analyze each test file
        test_infos = []
        for file_path in test_files:
            test_info = self.analyze_test_file(file_path)
            test_infos.append(test_info)
        
        # Create summary
        summary = self._create_summary(test_infos)
        
        return test_infos, summary

    def _create_summary(self, test_infos: List[TestInfo]) -> TestSummary:
        """Create a summary of all test information."""
        total_files = len(test_infos)
        total_cases = sum(len(info.test_cases) for info in test_infos)
        
        frameworks = set()
        test_types = {}
        coverage_areas = set()
        all_deps = set()
        
        for info in test_infos:
            if info.test_framework:
                frameworks.add(info.test_framework)
            
            for test_type in info.test_types:
                test_types[test_type] = test_types.get(test_type, 0) + 1
            
            coverage_areas.update(info.coverage_areas)
            all_deps.update(info.dependencies)
        
        # Determine setup and test commands based on frameworks and files
        setup_commands = []
        test_commands = []
        
        if 'pytest' in frameworks:
            setup_commands.append('pip install pytest pytest-cov')
            test_commands.extend(['pytest', 'pytest --cov', 'pytest -v'])
        if 'unittest' in frameworks:
            test_commands.append('python -m unittest discover')
        if 'JUnit' in frameworks:
            test_commands.append('mvn test')
            setup_commands.append('Add JUnit dependency to pom.xml')
        if 'Jest' in frameworks:
            setup_commands.append('npm install --save-dev jest')
            test_commands.extend(['npm test', 'npm run test', 'jest'])
        if 'Mocha' in frameworks:
            setup_commands.append('npm install --save-dev mocha chai')
            test_commands.extend(['npm test', 'npm run test', 'mocha'])
        
        # Group tests by directory structure
        test_structure = {}
        for info in test_infos:
            dir_path = str(Path(info.file_path).parent)
            if dir_path not in test_structure:
                test_structure[dir_path] = []
            test_structure[dir_path].append(Path(info.file_path).name)
        
        return TestSummary(
            total_test_files=total_files,
            total_test_cases=total_cases,
            test_frameworks=list(frameworks),
            test_types=test_types,
            coverage_areas=list(coverage_areas),
            setup_commands=setup_commands,
            test_commands=test_commands,
            test_structure=test_structure
        )


# Tool class for CrewAI integration
class TestAnalyzerTool(BaseTool):
    """CrewAI tool wrapper for Test Analyzer."""

    name: str = "test_analyzer"
    description: str = "Analyze test files to extract testing information and generate test documentation"

    def _run(self, folder_path: str) -> str:
        """
        Analyze all test files in the given folder.
        
        Args:
            folder_path: Path to the folder containing test files
            
        Returns:
            JSON string with test analysis information
        """
        import json
        
        # First check if test files exist
        if not has_test_files(folder_path):
            return json.dumps({
                "summary": {
                    "total_test_files": 0,
                    "total_test_cases": 0,
                    "test_frameworks": [],
                    "test_types": {},
                    "coverage_areas": [],
                    "setup_commands": [],
                    "test_commands": [],
                    "test_structure": {}
                },
                "test_files": [],
                "message": "No test files found in the project"
            }, indent=2)
        
        analyzer = TestAnalyzer()
        test_infos, summary = analyzer.analyze_all_tests(folder_path)
        
        # Convert to JSON-serializable format
        result = {
            "summary": {
                "total_test_files": summary.total_test_files,
                "total_test_cases": summary.total_test_cases,
                "test_frameworks": summary.test_frameworks,
                "test_types": summary.test_types,
                "coverage_areas": summary.coverage_areas,
                "setup_commands": summary.setup_commands,
                "test_commands": summary.test_commands,
                "test_structure": summary.test_structure
            },
            "test_files": []
        }
        
        for info in test_infos:
            test_dict = {
                "file_path": info.file_path,
                "file_type": info.file_type,
                "test_framework": info.test_framework,
                "test_cases": info.test_cases,
                "setup_methods": info.setup_methods,
                "teardown_methods": info.teardown_methods,
                "fixtures": info.fixtures,
                "mocks": info.mocks,
                "coverage_areas": info.coverage_areas,
                "test_types": info.test_types,
                "dependencies": info.dependencies
            }
            result["test_files"].append(test_dict)
        
        return json.dumps(result, indent=2)


class TestDocsTool(BaseTool):
    """CrewAI tool wrapper for generating test documentation markdown."""

    name: str = "test_docs_generator"
    description: str = "Generate markdown documentation for tests from test analysis"

    def _run(self, folder_path: str) -> str:
        """
        Generate test documentation in markdown format.
        
        Args:
            folder_path: Path to the folder containing test files
            
        Returns:
            Markdown string with test documentation
        """
        # First check if test files exist
        if not has_test_files(folder_path):
            return "# Test Documentation\n\nNo test files were found in the project.\n\nThis appears to be a project without automated tests. Consider adding tests to ensure code quality and reliability.\n"
        
        analyzer = TestAnalyzer()
        test_infos, summary = analyzer.analyze_all_tests(folder_path)
        
        # Generate markdown documentation
        docs = []
        docs.append("# Testing Documentation\n")
        docs.append("## Overview\n")
        docs.append(f"- **Total Test Files**: {summary.total_test_files}")
        docs.append(f"- **Total Test Cases**: {summary.total_test_cases}")
        frameworks = ', '.join(summary.test_frameworks) if summary.test_frameworks else 'None detected'
        docs.append(f"- **Test Frameworks**: {frameworks}\n")
        
        # Test types
        if summary.test_types:
            docs.append("## Test Types\n")
            for test_type, count in summary.test_types.items():
                docs.append(f"- **{test_type.title()}**: {count} test files")
            docs.append("")
        
        # Setup instructions
        if summary.setup_commands:
            docs.append("## Setup\n")
            docs.append("### Install Dependencies\n")
            for cmd in summary.setup_commands:
                docs.append("```bash")
                docs.append(cmd)
                docs.append("```")
                docs.append("")
        
        # Running tests
        if summary.test_commands:
            docs.append("## Running Tests\n")
            docs.append("### Test Commands\n")
            for cmd in summary.test_commands:
                docs.append("```bash")
                docs.append(cmd)
                docs.append("```")
                docs.append("")
        
        # Test coverage areas
        if summary.coverage_areas:
            docs.append("## Test Coverage Areas\n")
            for area in sorted(set(summary.coverage_areas)):
                docs.append(f"- {area}")
            docs.append("")
        
        # Test structure
        if summary.test_structure:
            docs.append("## Test Structure\n")
            for dir_path, files in summary.test_structure.items():
                docs.append(f"### {dir_path}")
                for file in files:
                    docs.append(f"- {file}")
                docs.append("")
        
        # Detailed test file information
        if test_infos:
            docs.append("## Test Files Details\n")
            for info in test_infos[:10]:  # Limit to first 10 files
                docs.append(f"### {info.file_path}")
                
                # File description
                if info.file_description:
                    docs.append(f"**Description**: {info.file_description}")
                
                if info.test_framework:
                    docs.append(f"**Framework**: {info.test_framework}")
                if info.test_types:
                    docs.append(f"**Type**: {', '.join(info.test_types)}")
                if info.test_cases:
                    docs.append(f"**Test Cases**: {len(info.test_cases)}")
                    for case in info.test_cases[:10]:  # Show up to 10 test cases
                        name = case.get('name', 'Unknown')
                        desc = case.get('description')
                        if desc:
                            docs.append(f"- **{name}**: {desc}")
                        else:
                            docs.append(f"- {name}")
                docs.append("")
        
        return "\n".join(docs)

    def generate_test_docs(self, folder_path: str) -> str:
        """
        Generate test documentation in markdown format.
        
        Args:
            folder_path: Path to the folder containing test files
            
        Returns:
            Markdown string with test documentation
        """
        import json
        
        analyzer = TestAnalyzer()
        test_infos, summary = analyzer.analyze_all_tests(folder_path)
        
        # Generate markdown documentation
        docs = []
        docs.append("# Testing Documentation\n")
        docs.append("## Overview\n")
        docs.append(f"- **Total Test Files**: {summary.total_test_files}")
        docs.append(f"- **Total Test Cases**: {summary.total_test_cases}")
        docs.append(f"- **Test Frameworks**: {', '.join(summary.test_frameworks) or 'None detected'}\n")
        
        # Test types
        if summary.test_types:
            docs.append("## Test Types\n")
            for test_type, count in summary.test_types.items():
                docs.append(f"- **{test_type.title()}**: {count} test files")
            docs.append("")
        
        # Setup instructions
        if summary.setup_commands:
            docs.append("## Setup\n")
            docs.append("### Install Dependencies\n")
            for cmd in summary.setup_commands:
                docs.append(f"```bash\n{cmd}\n```")
            docs.append("")
        
        # Running tests
        if summary.test_commands:
            docs.append("## Running Tests\n")
            docs.append("### Test Commands\n")
            for cmd in summary.test_commands:
                docs.append(f"```bash\n{cmd}\n```")
            docs.append("")
        
        # Test coverage areas
        if summary.coverage_areas:
            docs.append("## Test Coverage Areas\n")
            for area in sorted(set(summary.coverage_areas)):
                docs.append(f"- {area}")
            docs.append("")
        
        # Test structure
        if summary.test_structure:
            docs.append("## Test Structure\n")
            for dir_path, files in summary.test_structure.items():
                docs.append(f"### {dir_path}")
                for file in files:
                    docs.append(f"- {file}")
                docs.append("")
        
        # Detailed test file information
        if test_infos:
            docs.append("## Test Files Details\n")
            for info in test_infos[:10]:  # Limit to first 10 files
                docs.append(f"### {info.file_path}")
                
                # File description
                if info.file_description:
                    docs.append(f"**Description**: {info.file_description}")
                
                if info.test_framework:
                    docs.append(f"**Framework**: {info.test_framework}")
                if info.test_types:
                    docs.append(f"**Type**: {', '.join(info.test_types)}")
                if info.test_cases:
                    docs.append(f"**Test Cases**: {len(info.test_cases)}")
                    for case in info.test_cases[:10]:  # Show up to 10 test cases
                        name = case.get('name', 'Unknown')
                        desc = case.get('description')
                        if desc:
                            docs.append(f"- **{name}**: {desc}")
                        else:
                            docs.append(f"- {name}")
                docs.append("")
        
        return "\n".join(docs)
