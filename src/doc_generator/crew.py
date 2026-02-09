from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from doc_generator.tools import LanguageDetector, StructureExtractor, DependencyAnalyzer


@CrewBase
class DocGenerator():
    """Multi-agent documentation generation crew."""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Layer 1: Structural Understanding Agents
    @agent
    def language_detector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['structural_scanner'],
            tools=[LanguageDetector()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def structural_scanner(self) -> Agent:
        return Agent(
            config=self.agents_config['structural_scanner'],
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def dependency_analyzer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['dependency_analyzer_agent'],
            tools=[DependencyAnalyzer()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 2: Semantic Understanding Agents
    @agent
    def api_semantics_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_semantics_agent'],
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def architecture_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_agent'],
            tools=[DependencyAnalyzer()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 3: Documentation Generation Agents
    @agent
    def api_doc_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_doc_agent'],
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def architecture_doc_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_doc_agent'],
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def example_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['example_generator_agent'],
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def getting_started_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['getting_started_agent'],
            tools=[StructureExtractor()],
            verbose=True,
            allow_delegation=False,
        )

    # Layer 4: Evaluation Agent
    @agent
    def evaluation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['evaluation_agent'],
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
