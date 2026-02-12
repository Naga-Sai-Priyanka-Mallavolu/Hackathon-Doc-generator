"""
Config Parser Tool for Documentation Generator

Parses various configuration files to extract setup requirements,
dependencies, and configuration details.
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from xml.etree import ElementTree as ET
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ConfigInfo(BaseModel):
    """Configuration information extracted from config files."""
    file_type: str
    file_path: str
    build_tool: Optional[str] = None
    language_version: Optional[str] = None
    dependencies: List[Dict[str, str]] = Field(default_factory=list)
    dev_dependencies: List[Dict[str, str]] = Field(default_factory=list)
    scripts: Dict[str, str] = Field(default_factory=dict)
    repositories: List[Dict[str, str]] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    plugins: List[Dict[str, str]] = Field(default_factory=list)
    java_version: Optional[str] = None
    node_version: Optional[str] = None
    python_version: Optional[str] = None
    docker_required: bool = False
    database_required: bool = False
    environment_vars: List[str] = Field(default_factory=list)
    ports: List[str] = Field(default_factory=list)


class ConfigParser:
    """
    Parses various configuration file formats to extract setup information.
    
    Supports:
    - Maven (pom.xml)
    - Gradle (build.gradle, build.gradle.kts)
    - npm (package.json)
    - Python (requirements.txt, pyproject.toml, setup.py)
    - Docker (Dockerfile, docker-compose.yml)
    - Spring Boot (application.yml, application.properties)
    - General (.env files)
    """

    def __init__(self):
        """Initialize the config parser."""
        self.config_patterns = {
            'maven': ['pom.xml'],
            'gradle': ['build.gradle', 'build.gradle.kts', 'settings.gradle'],
            'npm': ['package.json'],
            'python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
            'docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
            'spring': ['application.yml', 'application.properties', 'application.yaml'],
            'env': ['.env', '.env.example', '.env.sample'],
            'make': ['Makefile'],
            'ci': ['.github/workflows/*.yml', '.github/workflows/*.yaml', '.gitlab-ci.yml'],
        }

    def parse_config_file(self, file_path: str) -> ConfigInfo:
        """
        Parse a single configuration file.
        
        Args:
            file_path: Path to the config file
            
        Returns:
            ConfigInfo with extracted data
        """
        path = Path(file_path)
        if not path.exists():
            return ConfigInfo(file_type="unknown", file_path=file_path)
        
        file_name = path.name.lower()
        file_type = self._detect_file_type(file_name)
        
        if file_type == 'maven':
            return self._parse_maven_pom(file_path)
        elif file_type == 'gradle':
            return self._parse_gradle(file_path)
        elif file_type == 'npm':
            return self._parse_npm_package(file_path)
        elif file_type == 'python':
            return self._parse_python_config(file_path)
        elif file_type == 'docker':
            return self._parse_docker_config(file_path)
        elif file_type == 'spring':
            return self._parse_spring_config(file_path)
        elif file_type == 'env':
            return self._parse_env_file(file_path)
        elif file_type == 'make':
            return self._parse_makefile(file_path)
        else:
            return ConfigInfo(file_type=file_type, file_path=file_path)

    def _detect_file_type(self, file_name: str) -> str:
        """Detect the type of config file based on its name."""
        for file_type, patterns in self.config_patterns.items():
            for pattern in patterns:
                if '*' in pattern:
                    if file_name.startswith(pattern.replace('*', '')):
                        return file_type
                elif file_name == pattern.lower():
                    return file_type
        return 'unknown'

    def _parse_maven_pom(self, file_path: str) -> ConfigInfo:
        """Parse Maven pom.xml file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Handle namespaces
            namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
            if root.tag.startswith('{'):
                namespace['maven'] = root.tag.split('}')[0][1:]
            
            def get_text(tag_path: str) -> Optional[str]:
                element = root.find(tag_path, namespace)
                return element.text if element is not None else None
            
            info = ConfigInfo(
                file_type='maven',
                file_path=file_path,
                build_tool='Maven',
                java_version=get_text('.//maven:java.version') or get_text('.//maven:maven.compiler.source'),
            )
            
            # Extract dependencies
            deps = root.findall('.//maven:dependency', namespace)
            for dep in deps:
                group_id = dep.find('maven:groupId', namespace)
                artifact_id = dep.find('maven:artifactId', namespace)
                version = dep.find('maven:version', namespace)
                
                if group_id is not None and artifact_id is not None:
                    info.dependencies.append({
                        'group': group_id.text or '',
                        'artifact': artifact_id.text or '',
                        'version': version.text if version is not None else None
                    })
            
            # Extract build plugins
            plugins = root.findall('.//maven:plugin', namespace)
            for plugin in plugins:
                artifact_id = plugin.find('maven:artifactId', namespace)
                version = plugin.find('maven:version', namespace)
                
                if artifact_id is not None:
                    info.plugins.append({
                        'artifact': artifact_id.text or '',
                        'version': version.text if version is not None else None
                    })
            
            # Extract properties
            properties = root.find('.//maven:properties', namespace)
            if properties is not None:
                for prop in properties:
                    if prop.text:
                        info.properties[prop.tag.split('}')[-1]] = prop.text
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='maven', file_path=file_path)

    def _parse_gradle(self, file_path: str) -> ConfigInfo:
        """Parse Gradle build file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            info = ConfigInfo(
                file_type='gradle',
                file_path=file_path,
                build_tool='Gradle'
            )
            
            # Extract Java version
            java_version_match = re.search(r'sourceCompatibility\s*=\s*["\']?([^"\']+)["\']?', content)
            if java_version_match:
                info.java_version = java_version_match.group(1)
            
            # Extract dependencies
            deps_pattern = r'(?:implementation|compile|api|testImplementation)\s+["\']([^"\']+)["\']'
            for match in re.finditer(deps_pattern, content):
                dep_string = match.group(1)
                parts = dep_string.split(':')
                if len(parts) >= 2:
                    info.dependencies.append({
                        'group': parts[0] if len(parts) > 2 else '',
                        'artifact': parts[1] if len(parts) > 2 else parts[0],
                        'version': parts[2] if len(parts) > 2 else parts[1]
                    })
            
            # Extract plugins
            plugins_pattern = r'(?:apply|plugins\s*\{)\s*(?:plugin:\s*)?["\']([^"\']+)["\']'
            for match in re.finditer(plugins_pattern, content):
                info.plugins.append({'artifact': match.group(1)})
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='gradle', file_path=file_path)

    def _parse_npm_package(self, file_path: str) -> ConfigInfo:
        """Parse npm package.json file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            info = ConfigInfo(
                file_type='npm',
                file_path=file_path,
                build_tool='npm',
                node_version=data.get('engines', {}).get('node')
            )
            
            # Extract dependencies
            for name, version in data.get('dependencies', {}).items():
                info.dependencies.append({'name': name, 'version': version})
            
            # Extract dev dependencies
            for name, version in data.get('devDependencies', {}).items():
                info.dev_dependencies.append({'name': name, 'version': version})
            
            # Extract scripts
            info.scripts = data.get('scripts', {})
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='npm', file_path=file_path)

    def _parse_python_config(self, file_path: str) -> ConfigInfo:
        """Parse Python configuration file."""
        try:
            path = Path(file_path)
            info = ConfigInfo(
                file_type='python',
                file_path=file_path,
                build_tool='pip'
            )
            
            if path.name == 'requirements.txt':
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('==')
                            if len(parts) == 2:
                                info.dependencies.append({'name': parts[0], 'version': parts[1]})
                            else:
                                info.dependencies.append({'name': line})
            
            elif path.name == 'pyproject.toml':
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Extract dependencies from project section
                project = data.get('project', {})
                deps = project.get('dependencies', [])
                for dep in deps:
                    if '==' in dep:
                        name, version = dep.split('==', 1)
                        info.dependencies.append({'name': name.strip(), 'version': version.strip()})
                    else:
                        info.dependencies.append({'name': dep.strip()})
                
                # Extract Python version
                requires_python = project.get('requires-python')
                if requires_python:
                    info.python_version = requires_python
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='python', file_path=file_path)

    def _parse_docker_config(self, file_path: str) -> ConfigInfo:
        """Parse Docker configuration file."""
        try:
            path = Path(file_path)
            info = ConfigInfo(
                file_type='docker',
                file_path=file_path,
                docker_required=True
            )
            
            if path.name == 'Dockerfile':
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Extract exposed ports
                ports = re.findall(r'EXPOSE\s+(\d+)', content)
                info.ports.extend(ports)
                
                # Extract base image to infer language/version
                from_match = re.search(r'FROM\s+([^\s:]+):?([^\s]*)', content)
                if from_match:
                    base_image = from_match.group(1)
                    version = from_match.group(2)
                    if 'node' in base_image.lower():
                        info.node_version = version or 'latest'
                    elif 'python' in base_image.lower():
                        info.python_version = version or 'latest'
                    elif 'java' in base_image.lower() or 'openjdk' in base_image.lower():
                        info.java_version = version or 'latest'
            
            elif path.name.startswith('docker-compose'):
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                services = data.get('services', {})
                for service_name, service_config in services.items():
                    # Extract ports
                    ports = service_config.get('ports', [])
                    for port in ports:
                        if isinstance(port, str) and ':' in port:
                            info.ports.append(port.split(':')[0])
                        elif isinstance(port, str):
                            info.ports.append(port)
                    
                    # Check for database services
                    if any(db in service_name.lower() for db in ['db', 'postgres', 'mysql', 'mongo']):
                        info.database_required = True
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='docker', file_path=file_path)

    def _parse_spring_config(self, file_path: str) -> ConfigInfo:
        """Parse Spring Boot configuration file."""
        try:
            path = Path(file_path)
            info = ConfigInfo(
                file_type='spring',
                file_path=file_path
            )
            
            if path.name.endswith('.yml') or path.name.endswith('.yaml'):
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Extract database configuration
                if 'spring' in data and 'datasource' in data['spring']:
                    info.database_required = True
                
                # Extract server port
                server_port = data.get('server', {}).get('port')
                if server_port:
                    info.ports.append(str(server_port))
                
            else:  # .properties
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Extract database URL
                if 'datasource' in content.lower() or 'jdbc' in content.lower():
                    info.database_required = True
                
                # Extract server port
                port_match = re.search(r'server\.port\s*=\s*(\d+)', content)
                if port_match:
                    info.ports.append(port_match.group(1))
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='spring', file_path=file_path)

    def _parse_env_file(self, file_path: str) -> ConfigInfo:
        """Parse .env file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            info = ConfigInfo(
                file_type='env',
                file_path=file_path
            )
            
            # Extract environment variable names
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    var_name = line.split('=')[0]
                    info.environment_vars.append(var_name)
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='env', file_path=file_path)

    def _parse_makefile(self, file_path: str) -> ConfigInfo:
        """Parse Makefile."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            info = ConfigInfo(
                file_type='make',
                file_path=file_path,
                build_tool='make'
            )
            
            # Extract targets
            targets = re.findall(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:', content, re.MULTILINE)
            for target in targets:
                info.scripts[target] = f"make {target}"
            
            return info
            
        except Exception as e:
            return ConfigInfo(file_type='make', file_path=file_path)

    def parse_all_configs(self, folder_path: str) -> List[ConfigInfo]:
        """
        Parse all configuration files in a folder.
        
        Args:
            folder_path: Path to the folder to scan
            
        Returns:
            List of ConfigInfo objects
        """
        configs = []
        folder = Path(folder_path)
        
        # Scan for config files
        for file_type, patterns in self.config_patterns.items():
            for pattern in patterns:
                if '*' in pattern:
                    # Handle glob patterns
                    matches = folder.glob(pattern)
                    for match in matches:
                        if match.is_file():
                            configs.append(self.parse_config_file(str(match)))
                else:
                    # Handle exact file names
                    file_path = folder / pattern
                    if file_path.is_file():
                        configs.append(self.parse_config_file(str(file_path)))
        
        return configs


# Tool class for CrewAI integration
class ConfigParserTool(BaseTool):
    """CrewAI tool wrapper for Config Parser."""

    name: str = "config_parser"
    description: str = "Parse configuration files to extract build tools, dependencies, and setup requirements"

    def _run(self, folder_path: str) -> str:
        """
        Parse all configuration files in the given folder.
        
        Args:
            folder_path: Path to the folder containing config files
            
        Returns:
            JSON string with configuration information
        """
        import json
        
        parser = ConfigParser()
        configs = parser.parse_all_configs(folder_path)
        
        # Convert to JSON-serializable format
        result = {
            "config_files": [],
            "summary": {
                "build_tools": [],
                "languages": [],
                "dependencies": [],
                "scripts": {},
                "docker_required": False,
                "database_required": False,
                "environment_vars": [],
                "ports": []
            }
        }
        
        build_tools = set()
        languages = set()
        all_deps = []
        all_scripts = {}
        all_env_vars = set()
        all_ports = set()
        docker_required = False
        database_required = False
        
        for config in configs:
            config_dict = {
                "file_type": config.file_type,
                "file_path": config.file_path,
                "build_tool": config.build_tool,
                "language_version": config.language_version,
                "java_version": config.java_version,
                "node_version": config.node_version,
                "python_version": config.python_version,
                "dependencies": config.dependencies,
                "dev_dependencies": config.dev_dependencies,
                "scripts": config.scripts,
                "plugins": config.plugins,
                "properties": config.properties,
                "environment_vars": config.environment_vars,
                "ports": config.ports,
                "docker_required": config.docker_required,
                "database_required": config.database_required
            }
            result["config_files"].append(config_dict)
            
            # Aggregate summary information
            if config.build_tool:
                build_tools.add(config.build_tool)
            if config.java_version:
                languages.add(f"Java {config.java_version}")
            if config.node_version:
                languages.add(f"Node.js {config.node_version}")
            if config.python_version:
                languages.add(f"Python {config.python_version}")
            
            all_deps.extend(config.dependencies)
            all_deps.extend(config.dev_dependencies)
            all_scripts.update(config.scripts)
            all_env_vars.update(config.environment_vars)
            all_ports.update(config.ports)
            
            if config.docker_required:
                docker_required = True
            if config.database_required:
                database_required = True
        
        # Build summary
        result["summary"]["build_tools"] = list(build_tools)
        result["summary"]["languages"] = list(languages)
        result["summary"]["dependencies"] = all_deps[:20]  # Limit to first 20
        result["summary"]["scripts"] = all_scripts
        result["summary"]["docker_required"] = docker_required
        result["summary"]["database_required"] = database_required
        result["summary"]["environment_vars"] = list(all_env_vars)[:10]  # Limit to first 10
        result["summary"]["ports"] = list(all_ports)
        
        return json.dumps(result, indent=2)
