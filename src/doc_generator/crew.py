from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
# from litellm.llms.custom_httpx.http_handler import HTTPHandler

from doc_generator.tools import CodeAnalyzer, SharedMemoryReader, GuardrailsTool


# ── Context Compression Helper ─────────────────────────────────────────
def _compress_context(text: str, max_chars: int = 8000) -> str:
    """
    Compress context by truncating to max_chars and adding ellipsis.
    Preserves structure by keeping first and last sections.
    """
    if len(text) <= max_chars:
        return text
    
    # Keep first 60% and last 40% of the limit
    first_part = int(max_chars * 0.6)
    last_part = int(max_chars * 0.4)
    
    return (
        text[:first_part] + 
        "\n\n[... content truncated for context size ...]\n\n" + 
        text[-(last_part):]
    )


# Store original post method
# _original_post = HTTPHandler.post

# def _patched_post(self, *args, **kwargs):
#     """Patch HTTPHandler.post to add Authorization header for Ollama Cloud"""
#     api_key = os.getenv('OLLAMA_API_KEY', '').strip()
    
#     # Try to get URL from various possible locations
#     url = kwargs.get('url', '') or kwargs.get('api_base', '') or (args[0] if args else '')
    
#     # Check if this is an Ollama Cloud request
#     is_ollama_cloud = api_key and ('ollama.com' in str(url) or hasattr(self, 'base_url') and 'ollama.com' in str(getattr(self, 'base_url', '')))
    
#     # If this is an Ollama Cloud request and we have an API key
#     if is_ollama_cloud:
#         # Ensure headers exist
#         if 'headers' not in kwargs:
#             kwargs['headers'] = {}
#         elif kwargs['headers'] is None:
#             kwargs['headers'] = {}
        
#         # Add Authorization header if not already present
#         if 'Authorization' not in kwargs['headers']:
#             kwargs['headers']['Authorization'] = f'Bearer {api_key}'
    
#     return _original_post(self, *args, **kwargs)

# # Apply the patch
# HTTPHandler.post = _patched_post


@CrewBase
class DocGenerator():
    """
    Multi-agent documentation pipeline.

    Architecture (matches the diagram):

        Code Analyzer ──► shared memory
              │
              ├──► API Semantics Agent ──┐
              │                          ├──► Examples Agent ──► Getting Started Agent ──► Document Assembler
              └──► Architecture Agent ───┘
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    # @property
    # def ollama_cloud_llm(self) -> LLM:
    #     """Create and return Ollama Cloud LLM instance"""
    #     cloud_base_url = os.getenv('OLLAMA_CLOUD_BASE_URL', 'https://ollama.com')
    #     cloud_api_key = os.getenv('OLLAMA_API_KEY', '').strip()
    #     model_name = os.getenv('OLLAMA_CLOUD_MODEL', 'qwen3-coder-next:latest').replace('-cloud', '')
        
    #     os.environ['OLLAMA_API_KEY'] = cloud_api_key
        
    #     return LLM(
    #         model=f'ollama/{model_name}',
    #         base_url=cloud_base_url,
    #         api_key=cloud_api_key,
    #     )

    # ── Shared tool instances (created once, reused) ───────────────────
    def _code_analyzer_tool(self) -> CodeAnalyzer:
        return CodeAnalyzer()

    def _memory_reader_tool(self) -> SharedMemoryReader:
        return SharedMemoryReader()

    # ═══════════════════════════════════════════════════════════════════
    # Agent 1 – Code Analyzer
    # ═══════════════════════════════════════════════════════════════════
    @agent
    def code_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['code_analyzer'],
            # llm=self.ollama_cloud_llm,
            tools=[self._code_analyzer_tool(), self._memory_reader_tool()],
            verbose=True,
            allow_delegation=False,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Agent 2 – API Semantics Agent
    # ═══════════════════════════════════════════════════════════════════
    @agent
    def api_semantics_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_semantics_agent'],
            # llm=self.ollama_cloud_llm,
            tools=[self._memory_reader_tool()],
            verbose=True,
            allow_delegation=False,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Agent 3 – Architecture Reasoning Agent
    # ═══════════════════════════════════════════════════════════════════
    @agent
    def architecture_reasoning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_reasoning_agent'],
            # llm=self.ollama_cloud_llm,
            tools=[self._memory_reader_tool()],
            verbose=True,
            allow_delegation=False,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Agent 4 – Examples Agent
    # ═══════════════════════════════════════════════════════════════════
    @agent
    def example_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['example_generator_agent'],
            # llm=self.ollama_cloud_llm,
            tools=[self._memory_reader_tool()],
            verbose=True,
            allow_delegation=False,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Agent 5 – Getting Started Agent
    # ═══════════════════════════════════════════════════════════════════
    @agent
    def getting_started_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['getting_started_agent'],
            # llm=self.ollama_cloud_llm,
            tools=[self._memory_reader_tool()],
            verbose=True,
            allow_delegation=False,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Agent 6 – Document Assembler
    # ═══════════════════════════════════════════════════════════════════
    @agent
    def document_assembler(self) -> Agent:
        return Agent(
            config=self.agents_config['document_assembler'],
            # llm=self.ollama_cloud_llm,
            tools=[self._memory_reader_tool(), GuardrailsTool()],
            verbose=True,
            allow_delegation=False,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Tasks  (sequential pipeline with context dependencies)
    # ═══════════════════════════════════════════════════════════════════

    # Task 1: Code Analyzer parses codebase → shared memory
    @task
    def code_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_analysis_task'],
            agent=self.code_analyzer(),
        )

    # Task 2: API Semantics reads from shared memory (depends on Task 1)
    @task
    def api_semantics_task(self) -> Task:
        return Task(
            config=self.tasks_config['api_semantics_task'],
            agent=self.api_semantics_agent(),
            context=[self.code_analysis_task()],
        )

    # Task 3: Architecture reads from shared memory (depends on Task 1)
    @task
    def architecture_reasoning_task(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_reasoning_task'],
            agent=self.architecture_reasoning_agent(),
            context=[self.code_analysis_task()],
        )

    # Task 4: Examples depends on API Semantics + Architecture
    @task
    def examples_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['examples_generation_task'],
            agent=self.example_generator_agent(),
            context=[self.api_semantics_task(), self.architecture_reasoning_task()],
        )

    # Task 5: Getting Started depends on Architecture + Examples
    @task
    def getting_started_task(self) -> Task:
        return Task(
            config=self.tasks_config['getting_started_task'],
            agent=self.getting_started_agent(),
            context=[self.architecture_reasoning_task(), self.examples_generation_task()],
        )

    # Task 6: Document Assembler depends on ALL previous tasks
    @task
    def document_assembly_task(self) -> Task:
        return Task(
            config=self.tasks_config['document_assembly_task'],
            agent=self.document_assembler(),
            context=[
                self.code_analysis_task(),
                self.api_semantics_task(),
                self.architecture_reasoning_task(),
                self.examples_generation_task(),
                self.getting_started_task(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        """Multi-agent documentation pipeline."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Using custom SharedMemory instead
        )
