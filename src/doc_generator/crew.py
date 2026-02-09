from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from litellm.llms.custom_httpx.http_handler import HTTPHandler

from doc_generator.tools import LanguageDetector, StructureExtractor, DependencyAnalyzer


# Store original post method
_original_post = HTTPHandler.post

def _patched_post(self, *args, **kwargs):
    """Patch HTTPHandler.post to add Authorization header for Ollama Cloud"""
    api_key = os.getenv('OLLAMA_API_KEY', '').strip()
    
    # Try to get URL from various possible locations
    url = kwargs.get('url', '') or kwargs.get('api_base', '') or (args[0] if args else '')
    
    # Check if this is an Ollama Cloud request
    is_ollama_cloud = api_key and ('ollama.com' in str(url) or hasattr(self, 'base_url') and 'ollama.com' in str(getattr(self, 'base_url', '')))
    
    # If this is an Ollama Cloud request and we have an API key
    if is_ollama_cloud:
        # Ensure headers exist
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        elif kwargs['headers'] is None:
            kwargs['headers'] = {}
        
        # Add Authorization header if not already present
        if 'Authorization' not in kwargs['headers']:
            kwargs['headers']['Authorization'] = f'Bearer {api_key}'
    
    return _original_post(self, *args, **kwargs)

# Apply the patch
HTTPHandler.post = _patched_post

@CrewBase
class DocGenerator():
    """Multi-agent documentation generation crew."""

    agents: List[BaseAgent]
    tasks: List[Task]


    @property
    def ollama_cloud_llm(self) -> LLM:
        """Create and return Ollama Cloud LLM instance using official Ollama Cloud SDK pattern"""
        cloud_base_url = os.getenv('OLLAMA_CLOUD_BASE_URL', 'https://ollama.com')
        cloud_api_key = os.getenv('OLLAMA_API_KEY', '').strip()
        model_name = os.getenv('OLLAMA_CLOUD_MODEL', 'qwen3-coder-next:latest').replace('-cloud', '')
        
        os.environ['OLLAMA_API_KEY'] = cloud_api_key
        
        return LLM(
            model=f'ollama/{model_name}',  # litellm requires 'ollama/' prefix for native format
            base_url=cloud_base_url,
            api_key=cloud_api_key,  # Pass API key - may need custom header configuration
        )
    # Layer 1: Structural Understanding Agents
    @agent
    def language_detector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['structural_scanner'],
            llm=self.ollama_cloud_llm,
            tools=[LanguageDetector()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def structural_scanner(self) -> Agent:
        return Agent(
            config=self.agents_config['structural_scanner'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def dependency_analyzer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['dependency_analyzer_agent'],
            llm=self.ollama_cloud_llm,
            tools=[DependencyAnalyzer()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 2: Semantic Understanding Agents
    @agent
    def api_semantics_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_semantics_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def architecture_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_agent'],
            llm=self.ollama_cloud_llm,
            tools=[DependencyAnalyzer()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 3: Documentation Generation Agents
    @agent
    def api_doc_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_doc_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def architecture_doc_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_doc_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def example_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['example_generator_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def getting_started_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['getting_started_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 4: Evaluation Agent
    @agent
    def evaluation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['evaluation_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    # Tasks - Layer 1: Structural Analysis
    @task
    def language_detection_task(self) -> Task:
        return Task(
            description=f"IMPORTANT: You MUST actually CALL the Language Detector tool with folder_path={{folder_path}} to detect languages. Do NOT just describe the tool - execute it and use the results. Use the Language Detector tool to identify all programming languages in the codebase. Provide a summary based on ACTUAL tool output.",
            expected_output="A summary of detected programming languages with file counts and percentages based on actual tool execution results.",
            agent=self.language_detector_agent(),
        )

    @task
    def structural_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['structural_analysis_task'],
            agent=self.structural_scanner(),
            context=[self.language_detection_task()],
        )

    @task
    def dependency_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['dependency_analysis_task'],
            agent=self.dependency_analyzer_agent(),
            context=[self.language_detection_task(), self.structural_analysis_task()],
        )

    # Tasks - Layer 2: Semantic Understanding
    @task
    def semantic_understanding_task(self) -> Task:
        return Task(
            config=self.tasks_config['semantic_understanding_task'],
            agent=self.api_semantics_agent(),
            context=[self.language_detection_task(), self.structural_analysis_task(), self.dependency_analysis_task()],
        )

    @task
    def architecture_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_analysis_task'],
            agent=self.architecture_agent(),
            context=[self.language_detection_task(), self.structural_analysis_task(), self.dependency_analysis_task(), self.semantic_understanding_task()],
        )

    # Tasks - Layer 3: Documentation Generation
    @task
    def api_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config['api_documentation_task'],
            agent=self.api_doc_agent(),
            context=[self.language_detection_task(), self.structural_analysis_task(), self.semantic_understanding_task()],
        )

    @task
    def architecture_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_documentation_task'],
            agent=self.architecture_doc_agent(),
            context=[self.architecture_analysis_task(), self.dependency_analysis_task(), self.semantic_understanding_task()],
        )

    @task
    def example_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['example_generation_task'],
            agent=self.example_generator_agent(),
            context=[self.api_documentation_task()],
        )

    @task
    def getting_started_task(self) -> Task:
        return Task(
            config=self.tasks_config['getting_started_task'],
            agent=self.getting_started_agent(),
            context=[self.language_detection_task(), self.structural_analysis_task(), self.dependency_analysis_task()],
        )

    # Tasks - Layer 4: Evaluation
    @task
    def evaluation_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluation_task'],
            agent=self.evaluation_agent(),
            context=[
                self.api_documentation_task(),
                self.architecture_documentation_task(),
                self.example_generation_task(),
                self.getting_started_task(),
            ],
        )

    # Final Assembly Task
    @task
    def final_documentation_assembly_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_documentation_assembly_task'],
            agent=self.api_doc_agent(),
            context=[
                self.api_documentation_task(),
                self.architecture_documentation_task(),
                self.example_generation_task(),
                self.getting_started_task(),
                self.evaluation_task(),
            ],
            output_file='technical_documentation.json',
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DocGenerator crew with multi-agent architecture."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Sequential processing ensures proper context flow
            verbose=True,
            memory=False,  # Disabled to work with local Ollama models (no OpenAI embeddings needed)
        )
