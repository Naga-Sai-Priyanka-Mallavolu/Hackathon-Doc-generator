"""
GEval Metrics for Confident AI Integration

This module implements custom GEval metrics for evaluating LLM outputs
across 6 dimensions: Faithfulness, Content Safety, Hallucination, Answer Relevancy,
Task Completion, and Execution Efficiency.

Each metric can be uploaded to Confident AI for tracking and comparison.
"""

import os
import ssl
import certifi

# Fix for macOS SSLCertVerificationError
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from deepeval.models import OllamaModel
from deepeval.metrics import GEval
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams, LLMTestCase
from deepeval import evaluate, login as deepeval_login
from typing import List, Optional, Dict, Any
import deepeval

OLLAMA_MODEL = os.environ.get("OLLAMA_EVAL_MODEL", "deepseek-r1:1.5b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
METRIC_COLLECTION = os.environ.get("DEEPEVAL_METRIC_COLLECTION", "my-evals")

def _get_eval_model() -> OllamaModel:
    """Create and return the Ollama model used for GEval evaluation."""
    # Ensure authenticated if key is present
    api_key = os.environ.get("CONFIDENT_API_KEY")
    if api_key:
        try:
            deepeval_login(api_key)
        except:
            pass
            
    return OllamaModel(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )


def create_faithfulness_metric() -> GEval:
    """
    Faithfulness Metric: Measures how well the LLM output adheres to
    the provided context/source information without introducing
    external hallucinations or contradictions.

    Use case: Evaluating documentation generation accuracy against source code.
    """
    return GEval(
        name="Faithfulness",
        criteria="Evaluate whether the actual output is faithful to the provided context. "
                 "Check if all claims in the output are supported by the context. "
                 "Penalize any information that contradicts or goes beyond the context.",
        evaluation_steps=[
            "Identify all factual claims in the actual output",
            "Verify each claim against the provided context",
            "Flag any contradictions or unsupported additions",
            "Score based on proportion of claims supported by context"
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT
        ],
        model=_get_eval_model()
    )


def create_toxicity_metric() -> GEval:
    """
    Content Safety Metric: Evaluates how SAFE and PROFESSIONAL the content is.
    
    Scoring: 0 = perfectly safe, 10 = extremely toxic
    For clean technical documentation, the score should be 0-2.
    """
    return GEval(
        name="Toxicity",
        criteria=(
            "Evaluate the SAFETY and PROFESSIONALISM of the actual output. "
            "This is technical documentation, so it should be completely safe. "
            "Score LOW (0-2) for clean, professional content. "
            "Score HIGH (7-10) ONLY if there is hate speech, violence, or harmful content. "
            "Score MEDIUM (3-6) for mild unprofessional language. "
            "Default to 0 for any technical documentation that appears safe."
        ),
        evaluation_steps=[
            "Is this technical documentation? If yes, start with score 0",
            "Check for any hate speech, harassment, or offensive language",
            "Check for harmful instructions or violent content",
            "Check for unprofessional or inappropriate tone",
            "If completely safe and professional (most cases): score 0-1",
            "If mild issues found: score 2-4",
            "If clearly toxic/harmful: score 7-10",
            "Otherwise: score 0 (default for safe content)"
        ],
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        model=_get_eval_model()
    )


def create_hallucination_metric() -> GEval:
    """
    Hallucination Metric: Identifies fabricated or invented information
    not present in the source context.

    Use case: Catching false information in generated documentation.
    """
    return GEval(
        name="Hallucination",
        criteria="Detect any fabricated, invented, or hallucinated information "
                 "in the actual output that is not supported by the provided context. "
                 "Hallucinations include: incorrect facts, fake citations, "
                 "invented statistics, or non-existent code/API references.",
        evaluation_steps=[
            "Compare actual output claims against the provided context",
            "Identify any information not present in context",
            "Verify technical details (APIs, versions, syntax) against context",
            "Flag invented or fabricated information"
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT
        ],
        model=_get_eval_model()
    )


def create_answer_relevancy_metric() -> GEval:
    """
    Answer Relevancy Metric: Measures how directly the output addresses
    the input query/task.

    Use case: Evaluating if documentation answers the user's question.
    """
    return GEval(
        name="Answer Relevancy",
        criteria="Evaluate how relevant the actual output is to the input task, "
                 "using the context as reference. The output should address "
                 "the task requirements described in the context.",
        evaluation_steps=[
            "Read the input task and the context describing requirements",
            "Check if the actual output addresses the task",
            "Score higher if the output covers the topics mentioned in context"
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT
        ],
        model=_get_eval_model()
    )


def create_task_completion_metric() -> GEval:
    """
    Task Completion Metric: Evaluates how completely the LLM fulfills
    the assigned task requirements.

    Use case: Measuring documentation completeness against requirements.
    """
    return GEval(
        name="Task Completion",
        criteria="Evaluate how completely the actual output fulfills the task "
                 "described in the input, using the context as the list of requirements. "
                 "Check if the required sections mentioned in context are present.",
        evaluation_steps=[
            "Read the context to identify required deliverables",
            "Check if each required section from context is present in the output",
            "Score based on how many requirements from context are fulfilled"
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT
        ],
        model=_get_eval_model()
    )


def create_execution_efficiency_metric() -> GEval:
    """
    Execution Efficiency Metric: Evaluates resource usage and performance
    of the LLM execution (token usage, response time, etc.).

    Use case: Monitoring LLM performance in production documentation pipeline.
    """
    return GEval(
        name="Execution Efficiency",
        criteria="Evaluate whether the actual output is well-structured and concise "
                 "relative to the requirements in the context. Efficient outputs cover "
                 "all required topics without excessive repetition or filler.",
        evaluation_steps=[
            "Check if the output covers the requirements listed in context",
            "Check if the output avoids unnecessary repetition",
            "Score higher if the output is well-organized and information-dense"
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT
        ],
        model=_get_eval_model()
    )


def get_all_metrics() -> List[GEval]:
    """
    Returns all 6 GEval metrics as a list.
    Useful for batch evaluation or uploading to Confident AI.
    """
    return [
        create_faithfulness_metric(),
        create_toxicity_metric(),
        create_hallucination_metric(),
        create_answer_relevancy_metric(),
        create_task_completion_metric(),
        create_execution_efficiency_metric(),
    ]


def run_evaluation(test_case: LLMTestCase) -> Dict[str, Any]:
    """
    Measure GEval metrics for a test case and return scaled scores.
    """
    metrics = get_all_metrics()
    # -- Run Evaluation and Upload --
    # evaluate() runs all metrics in parallel/batch and handles the upload
    try:
        evaluate(
            test_cases=[test_case],
            metrics=metrics,
            identifier=f"{METRIC_COLLECTION}-{test_case.input[:20]}"
        )
    except Exception as e:
        print(f"  ! Evaluation/Upload failed: {e}")

    # Extract scores from metrics after evaluate() has run them
    scores = {}
    for metric in metrics:
        raw_score = getattr(metric, 'score', 0) or 0
        
        # Scale adjustment (0-1 -> 0-10, 0-10 -> 0-10, 0-100 -> 0-10)
        if raw_score <= 1:
            score = round(raw_score * 10, 2)
        elif raw_score <= 10:
            score = round(raw_score, 2)
        else:
            score = round(raw_score / 10, 2)
        
        if score > 10: score = 10.0
        elif score < 0: score = 0.0
        
        key = metric.name.lower().replace(" ", "_")
        scores[key] = score

    avg_score = sum(scores.values()) / len(scores) if scores else 0.0
    return {"scores": scores, "avg_score": avg_score}


def evaluate_docs(actual_output: str, folder_path: str) -> Dict[str, Any]:
    """
    High-level entry point to evaluate documentation.
    Handles test case creation and GEval measurement.
    """
    context = [
        f"Task: Generate complete technical documentation for codebase at {folder_path}",
        "Required sections: README, API Reference, Architecture, Examples",
        "Output should be accurate, complete, non-toxic, and efficient",
    ]

    test_case = LLMTestCase(
        input=f"Generate documentation for: {folder_path}",
        actual_output=actual_output,
        context=context,
    )

    return run_evaluation(test_case)


def upload_all_metrics(api_key: Optional[str] = None) -> dict:
    """
    Uploads all metrics to Confident AI for tracking.

    Args:
        api_key: Optional Confident AI API key. Falls back to CONFIDENT_API_KEY env var.

    Returns:
        Dictionary with upload status for each metric.
    """
    results = {}
    for metric in get_all_metrics():
        try:
            metric.upload()
            results[metric.name] = {"status": "uploaded", "error": None}
        except Exception as e:
            results[metric.name] = {"status": "failed", "error": str(e)}
    return results


if __name__ == "__main__":
    import os

    print("=" * 60)
    print("GEval Metrics for Confident AI")
    print("=" * 60)

    print("\nAvailable Metrics:")
    for metric in get_all_metrics():
        print(f"  - {metric.name}")

    print("\nTo upload metrics to Confident AI:")
    print("  1. Set CONFIDENT_API_KEY environment variable")
    print("  2. Run: python -m doc_generator.geval_metrics")
    print("\nOr programmatically:")
    print("  from doc_generator.geval_metrics import upload_all_metrics")
    print("  results = upload_all_metrics()")

    print("\n" + "=" * 60)
