from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Optional, Dict, Any
import os
import uuid
import json
from datetime import datetime
from pathlib import Path

# from litellm.llms.custom_httpx.http_handler import HTTPHandler
from deepeval.integrations.crewai import instrument_crewai
from deepeval.test_case import LLMTestCase
from doc_generator.tools import CodeAnalyzer, SharedMemoryReader, GuardrailsTool
from doc_generator.geval_metrics import (
    create_faithfulness_metric,
    create_toxicity_metric,
    create_hallucination_metric,
    create_answer_relevancy_metric,
    create_task_completion_metric,
    create_execution_efficiency_metric,
    upload_all_metrics,
)


instrument_crewai()

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
    
    def _guardrails_tool(self) -> GuardrailsTool:
        return GuardrailsTool()

    # ═══════════════════════════════════════════════════════════════════
    # Agent 1 – Code Analyzer
    # ═══════════════════════════════════════════════════════════════════
    @agent
    def code_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['code_analyzer'],
            # llm=self.ollama_cloud_llm,
            tools=[self._code_analyzer_tool(), self._memory_reader_tool(), self._guardrails_tool()],
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
            tools=[self._memory_reader_tool(), self._guardrails_tool()],
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
            tools=[self._memory_reader_tool(), self._guardrails_tool()],
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
            tools=[self._memory_reader_tool(), self._guardrails_tool()],
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
            tools=[self._memory_reader_tool(), self._guardrails_tool()],
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

    def _get_evaluation_metrics(self) -> Dict[str, Any]:
        """Initialize GEval metrics for evaluation."""
        return {
            "faithfulness": create_faithfulness_metric(),
            "toxicity": create_toxicity_metric(),
            "hallucination": create_hallucination_metric(),
            "answer_relevancy": create_answer_relevancy_metric(),
            "task_completion": create_task_completion_metric(),
            "execution_efficiency": create_execution_efficiency_metric(),
        }

    def _evaluate_output(
        self,
        input_text: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Dict]:
        """
        Evaluate crew output using GEval metrics.

        Args:
            input_text: The input query
            actual_output: The generated output
            expected_output: Reference/ground truth (used as context)
            session_id: Session ID for tracking

        Returns:
            Dictionary of metric results
        """
        session_id = session_id or str(uuid.uuid4())
        metrics = self._get_evaluation_metrics()
        results = {}
        timestamp = datetime.utcnow().isoformat()

        context = [expected_output] if expected_output else [
            f"Task: {input_text}",
            "Output should be accurate, complete, non-toxic, and efficient",
        ]

        for metric_name, metric in metrics.items():
            try:
                test_case = LLMTestCase(
                    input=input_text,
                    actual_output=actual_output,
                    context=context,
                )
                metric.measure(test_case)
                results[metric_name] = {
                    "session_id": session_id,
                    "metric_name": metric_name,
                    "score": metric.score,
                    "success": True,
                    "timestamp": timestamp,
                }
            except Exception as e:
                results[metric_name] = {
                    "session_id": session_id,
                    "metric_name": metric_name,
                    "score": 0.0,
                    "success": False,
                    "error": str(e),
                    "timestamp": timestamp,
                }

        return {"session_id": session_id, "results": results}

    def _store_results_locally(
        self,
        eval_result: Dict,
        output_dir: Optional[str] = None,
    ) -> str:
        """Store evaluation results locally."""
        output_dir = output_dir or ".deepeval/eval_results"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        session_id = eval_result["session_id"]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"eval_{session_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        output_data = {
            **eval_result,
            "stored_at": timestamp,
            "average_score": sum(
                r["score"] for r in eval_result["results"].values() if r["success"]
            ) / len(eval_result["results"]) if eval_result["results"] else 0,
        }

        with open(filepath, "w") as f:
            json.dump(output_data, f, indent=2)

        return filepath

    def _upload_metrics_to_confident_ai(self) -> Dict[str, Dict]:
        """Upload all GEval metrics to Confident AI."""
        return upload_all_metrics()

    def run_with_evaluation(
        self,
        inputs: Dict[str, Any],
        expected_output: Optional[str] = None,
        session_id: Optional[str] = None,
        store_locally: bool = True,
        upload_metrics: bool = True,
    ) -> Dict[str, Any]:
        """
        Run crew with integrated evaluation.

        Flow:
        1. Execute crew
        2. Evaluate output with GEval metrics
        3. Store results locally
        4. Upload metrics to Confident AI

        Args:
            inputs: Input dictionary for crew
            expected_output: Reference output for comparison
            session_id: Optional session ID for tracking
            store_locally: Store results locally
            upload_metrics: Upload metrics to Confident AI

        Returns:
            Dictionary with output, evaluation results, and file paths
        """
        session_id = session_id or str(uuid.uuid4())

        print(f"\n{'='*60}")
        print(f"Running CrewAI with Evaluation (Session: {session_id[:8]})")
        print(f"{'='*60}")

        print("\n[1/4] Executing crew...")
        output = self.crew().kickoff(inputs)
        print("   ✓ Crew execution complete")

        print("\n[2/4] Running GEval metrics...")
        eval_result = self._evaluate_output(
            input_text=str(inputs),
            actual_output=output,
            expected_output=expected_output,
            session_id=session_id,
        )
        print(f"   ✓ Evaluation complete ({len(eval_result['results'])} metrics)")

        stored_file = None
        if store_locally:
            print("\n[3/4] Storing results locally...")
            stored_file = self._store_results_locally(eval_result)
            print(f"   ✓ Stored: {stored_file}")

        if upload_metrics:
            print("\n[4/4] Uploading metrics to Confident AI...")
            try:
                upload_results = self._upload_metrics_to_confident_ai()
                print(f"   ✓ Uploaded {len(upload_results)} metrics")
            except Exception as e:
                print(f"   ✗ Upload failed: {e}")

        avg_score = sum(
            r["score"] for r in eval_result["results"].values() if r["success"]
        ) / len(eval_result["results"]) if eval_result["results"] else 0

        print(f"\n{'='*60}")
        print(f"Evaluation Complete - Average Score: {avg_score:.2f}")
        print(f"{'='*60}")

        return {
            "session_id": session_id,
            "output": output,
            "evaluation": eval_result,
            "stored_file": stored_file,
            "average_score": avg_score,
        }

    async def run_async_with_evaluation(
        self,
        inputs: Dict[str, Any],
        expected_output: Optional[str] = None,
        session_id: Optional[str] = None,
        store_locally: bool = True,
        upload_metrics: bool = True,
    ) -> Dict[str, Any]:
        """
        Run crew async with integrated evaluation.
        """
        session_id = session_id or str(uuid.uuid4())

        print(f"\n[1/4] Executing crew async...")
        output = await self.crew().kickoff_async(inputs)

        print("\n[2/4] Running GEval metrics...")
        eval_result = self._evaluate_output(
            input_text=str(inputs),
            actual_output=output,
            expected_output=expected_output,
            session_id=session_id,
        )

        stored_file = None
        if store_locally:
            print("\n[3/4] Storing results locally...")
            stored_file = self._store_results_locally(eval_result)

        if upload_metrics:
            print("\n[4/4] Uploading metrics to Confident AI...")
            self._upload_metrics_to_confident_ai()

        avg_score = sum(
            r["score"] for r in eval_result["results"].values() if r["success"]
        ) / len(eval_result["results"]) if eval_result["results"] else 0

        return {
            "session_id": session_id,
            "output": output,
            "evaluation": eval_result,
            "stored_file": stored_file,
            "average_score": avg_score,
        }

    @crew
    def crew(self) -> Crew:
        """Multi-agent documentation pipeline."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            tracing=True,
        )
