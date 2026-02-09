from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from litellm.llms.custom_httpx.http_handler import HTTPHandler

from doc_generator.tools import StructureExtractor, FileReader


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
    """Seven-layer documentation system."""

    agents: List[BaseAgent]
    tasks: List[Task]


    @property
    def ollama_cloud_llm(self) -> LLM:
        """Create and return Ollama Cloud LLM instance"""
        cloud_base_url = os.getenv('OLLAMA_CLOUD_BASE_URL', 'https://ollama.com')
        cloud_api_key = os.getenv('OLLAMA_API_KEY', '').strip()
        model_name = os.getenv('OLLAMA_CLOUD_MODEL', 'qwen3-coder-next:latest').replace('-cloud', '')
        
        os.environ['OLLAMA_API_KEY'] = cloud_api_key
        
        return LLM(
            model=f'ollama/{model_name}',
            base_url=cloud_base_url,
            api_key=cloud_api_key,
        )

    # Layer 1: Ingestion & Structural Understanding
    @agent
    def structural_scanner(self) -> Agent:
        return Agent(
            config=self.agents_config['structural_scanner'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def dependency_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['dependency_analyzer'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 2: Semantic Understanding
    @agent
    def api_semantics_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_semantics_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def architecture_reasoning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_reasoning_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 3: Documentation Assembly
    @agent
    def api_doc_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_doc_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def architecture_doc_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_doc_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def example_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['example_generator_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def getting_started_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['getting_started_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 6: Evaluation & Quality
    @agent
    def evaluation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['evaluation_agent'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 4: Final Assembly
    @agent
    def documentation_assembler(self) -> Agent:
        return Agent(
            config=self.agents_config['documentation_assembler'],
            llm=self.ollama_cloud_llm,
            tools=[StructureExtractor(), FileReader()],
            verbose=True,
            allow_delegation=False,
        )

    # Tasks
    @task
    def structural_scan_task(self) -> Task:
        return Task(
            config=self.tasks_config['structural_scan_task'],
            agent=self.structural_scanner(),
        )

    @task
    def dependency_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['dependency_analysis_task'],
            agent=self.dependency_analyzer(),
            context=[self.structural_scan_task()],
        )

    @task
    def api_semantics_task(self) -> Task:
        return Task(
            config=self.tasks_config['api_semantics_task'],
            agent=self.api_semantics_agent(),
            context=[self.structural_scan_task()],
        )

    @task
    def architecture_reasoning_task(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_reasoning_task'],
            agent=self.architecture_reasoning_agent(),
            context=[self.structural_scan_task(), self.dependency_analysis_task()],
        )

    @task
    def api_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config['api_documentation_task'],
            agent=self.api_doc_agent(),
            context=[self.api_semantics_task()],
        )

    @task
    def architecture_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_documentation_task'],
            agent=self.architecture_doc_agent(),
            context=[self.architecture_reasoning_task()],
        )

    @task
    def examples_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['examples_generation_task'],
            agent=self.example_generator_agent(),
            context=[self.api_documentation_task()],
        )

    @task
    def getting_started_task(self) -> Task:
        return Task(
            config=self.tasks_config['getting_started_task'],
            agent=self.getting_started_agent(),
            context=[self.architecture_documentation_task()],
        )

    @task
    def quality_evaluation_task(self) -> Task:
        return Task(
            config=self.tasks_config['quality_evaluation_task'],
            agent=self.evaluation_agent(),
            context=[self.api_documentation_task(), self.architecture_documentation_task()],
        )

    @task
    def final_assembly_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_assembly_task'],
            agent=self.documentation_assembler(),
            context=[
                self.structural_scan_task(),
                self.dependency_analysis_task(),
                self.api_semantics_task(),
                self.architecture_reasoning_task(),
                self.api_documentation_task(),
                self.architecture_documentation_task(),
                self.examples_generation_task(),
                self.getting_started_task(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        """Seven-layer documentation system."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disabled - requires OpenAI key for embeddings
        )
