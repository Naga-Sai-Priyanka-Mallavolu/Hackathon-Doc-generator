#!/usr/bin/env python
"""
Documentation Generator – entry point.

WHERE TO FIND YOUR DATA IN CONFIDENT AI UI:
─────────────────────────────────────────────────────────────
  Traces  → app.confident-ai.com  → Observability → Traces
  Metrics → app.confident-ai.com  → Testing → Test Runs
─────────────────────────────────────────────────────────────

REQUIRED .env VARIABLES:
    CONFIDENT_API_KEY=ck_...        # Your project API key
    CONFIDENT_TRACE_FLUSH=YES       # Prevents traces being abandoned on exit
    CONFIDENT_METRIC_LOGGING_VERBOSE=1  # Shows upload confirmation in console
"""

import re
import sys
import warnings
import os
import uuid
import json
from pathlib import Path
from datetime import datetime

# ── Load .env FIRST before any deepeval import ─────────────────────────
# deepeval reads env vars at import time. If you load .env after importing
# deepeval, the API key is never picked up.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional — can also export env vars manually

from doc_generator.crew import DocGenerator
from doc_generator.tools.shared_memory import SharedMemory
from doc_generator.models import DocumentationOutput
from doc_generator.human_in_the_loop import (
    HumanInTheLoop,
    ApprovalStatus,
    apply_human_feedback,
)
from doc_generator.geval_metrics import (
    create_faithfulness_metric,
    create_toxicity_metric,
    create_hallucination_metric,
    create_answer_relevancy_metric,
    create_task_completion_metric,
    create_execution_efficiency_metric,
    METRIC_COLLECTION,
    evaluate_docs,
    run_evaluation,
    get_all_metrics,
)

# ── deepeval imports AFTER env is loaded ───────────────────────────────
import deepeval
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.tracing import observe, update_current_span

import subprocess
import tempfile
import shutil
import time

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# ── Authenticate ONCE at startup ───────────────────────────────────────
# deepeval.login() persists the key for the session.
# Must be called before any @observe or evaluate() call.
confident_api_key = os.environ.get("CONFIDENT_API_KEY")
if confident_api_key:
    try:
        deepeval.login(confident_api_key)
        print(f"   ✓ Confident AI authenticated")
        print(f"   ✓ Traces  → Observability → Traces tab")
        print(f"   ✓ Metrics → Testing → Test Runs tab")
        print(f"   ✓ Collection: {METRIC_COLLECTION}")
    except Exception as e:
        print(f"   ✗ Confident AI auth failed: {e}")
else:
    print("   ✗ CONFIDENT_API_KEY not set — data will NOT appear in dashboard")
    print("   ✗ Add to .env: CONFIDENT_API_KEY=ck_your_key_here")

# ── Thresholds ─────────────────────────────────────────────────────────
MIN_EVAL_SCORE = float(os.environ.get("MIN_EVAL_SCORE", "6.0"))
MAX_RETRY_ATTEMPTS = int(os.environ.get("MAX_RETRY_ATTEMPTS", "2"))

# ── Section splitter ───────────────────────────────────────────────────
SECTION_PATTERN = re.compile(r"^===SECTION:\s*(.+?)\s*===$", re.MULTILINE)

DEFAULT_FILES = {
    "README.md": "# README\n\nDocumentation was not generated for this section.",
    "API_REFERENCE.md": "# API Reference\n\nDocumentation was not generated for this section.",
    "ARCHITECTURE.md": "# Architecture\n\nDocumentation was not generated for this section.",
    "EXAMPLES.md": "# Examples\n\nDocumentation was not generated for this section.",
    "TEST_DOCUMENTATION.md": "# Test Documentation\n\nNo test files were found in the project.",
    "architecture.mermaid": "graph TD\n    A[No diagram generated]",
}

GIT_URL_REGEX = re.compile(
    r"^(https://github\.com/|git@github\.com:).+/.+(.git)?$"
)


def _is_git_url(value: str) -> bool:
    return bool(GIT_URL_REGEX.match(value))


def _clone_repo(repo_url: str) -> str:
    """Clone a public Git repository into a temporary directory."""
    temp_dir = tempfile.mkdtemp(prefix="docgen_repo_")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return temp_dir
    except subprocess.CalledProcessError:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(
            "Failed to clone repository. Ensure the repo is public and the URL is correct."
        )


def _split_sections(raw: str) -> dict[str, str]:
    """Split assembler output by ===SECTION: filename=== markers."""
    parts = SECTION_PATTERN.split(raw)
    sections: dict[str, str] = {}
    i = 1
    while i < len(parts) - 1:
        name = parts[i].strip()
        content = parts[i + 1].strip()
        if name and content:
            sections[name] = content
        i += 2
    return sections


def _extract_final_output(crew_instance) -> str:
    """Extract the final assembler output from the crew run."""
    for task in reversed(crew_instance.tasks):
        task_output = task.output
        if task_output:
            if hasattr(task_output, "raw") and task_output.raw:
                return task_output.raw
            if hasattr(task_output, "result"):
                return str(task_output.result)
            if isinstance(task_output, str):
                return task_output
            return str(task_output)
    return ""


def _count_endpoints(api_reference: str) -> int:
    """Count the number of API endpoints in the API reference."""
    http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    count = 0
    for line in api_reference.split("\n"):
        for method in http_methods:
            if f"**{method}**" in line or f"`{method}" in line or f"| {method}" in line:
                count += 1
                break
    return count


@observe()
def _run_crew_traced(inputs: dict) -> tuple:
    """
    Execute the crew inside an @observe span so the full agent
    flow (which agent ran, which tool was called, in what order)
    appears in Confident AI → Observability → Traces.
    
    Returns: (result, crew_instance, raw_output)
    """
    update_current_span(
        input=json.dumps({k: str(v)[:200] for k, v in inputs.items()}),
        output="crew_execution_pending",
    )
    
    doc_gen = DocGenerator()
    crew_instance = doc_gen.crew()
    result = crew_instance.kickoff(inputs=inputs)
    
    raw_output = _extract_final_output(crew_instance)
    if not raw_output:
        raw_output = getattr(result, "raw", None) or (
            result if isinstance(result, str) else str(result)
        )
    
    # Update span with actual result
    update_current_span(
        input=json.dumps({k: str(v)[:200] for k, v in inputs.items()}),
        output=f"Generated {len(raw_output)} chars of documentation",
    )
    
    return result, crew_instance, raw_output


def _run_evaluation_traced(output: str, folder_path: str, attempt: int = 1) -> dict:
    """
    Evaluate documentation quality and upload to Confident AI.

    Data destinations:
    ──────────────────────────────────────────────────────────────
    deepeval.evaluate()       → Testing → Test Runs tab
    local JSON file           → .deepeval/eval_results/
    ──────────────────────────────────────────────────────────────
    """
    session_id = str(uuid.uuid4())[:8]

    context = [
        f"Task: Generate complete technical documentation for codebase at {folder_path}",
        "Required sections: README, API Reference, Architecture, Examples",
        "Output should be accurate, complete, non-toxic, and efficient",
    ]

    # ── B: Build test case ─────────────────────────────────────────
    test_case = LLMTestCase(
        input=f"Generate documentation for: {folder_path}",
        actual_output=output,
        context=context,
    )

    # ── C: Create metrics and measure locally first ─────────────────
    metrics = [
        create_faithfulness_metric(),
        create_toxicity_metric(),
        create_hallucination_metric(),
        create_answer_relevancy_metric(),
        create_task_completion_metric(),
        create_execution_efficiency_metric(),
    ]

    # Measure locally to get actual scores (0-1 range)
    print(f"\n   Measuring 6 metrics locally...")
    
    # Use centralized evaluation logic
    eval_result = run_evaluation(test_case)
    results = eval_result["scores"]
    avg_score = eval_result["avg_score"]

    # Print results (similar to original logic for consistency)
    for key, score in results.items():
        print(f"   ✓ {key.replace('_', ' ').title()}: {score:.1f}/10")

    # -- D: Update metric objects with scaled scores before upload --------
    # Confident AI expects 0-1 scale, so convert our 0-10 scores
    metrics = get_all_metrics() # Get fresh instances to set scores on
    for metric in metrics:
        key = metric.name.lower().replace(" ", "_")
        if key in results:
            metric.score = results[key] / 10.0
    
    # -- E: Upload to Confident AI Testing → Test Runs ─────────────────
    try:
        evaluate(
            test_cases=[test_case],
            metrics=metrics,
            identifier=f"{METRIC_COLLECTION}-attempt-{attempt}-{session_id}",
        )
        print(f"   ✓ Uploaded → app.confident-ai.com → Testing → Test Runs")
    except Exception as e:
        print(f"   ✗ evaluate() upload failed: {e}")

    avg_score = sum(results.values()) / len(results) if results else 0.0
    print(f"\n   Average score: {avg_score:.2f}/10")

    # ── E: Local audit trail ───────────────────────────────────────
    eval_dir = Path(".deepeval/eval_results")
    eval_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    eval_file = eval_dir / f"eval_{session_id}_{timestamp}.json"
    with open(eval_file, "w") as f:
        json.dump({
            "session_id": session_id,
            "timestamp": timestamp,
            "folder_path": folder_path,
            "attempt": attempt,
            "results": results,
            "average_score": avg_score,
        }, f, indent=2)
    print(f"   ✓ Local copy: {eval_file}")

    return {"results": results, "avg_score": avg_score, "session_id": session_id}


def _flush_traces() -> None:
    """Block until all queued traces/metrics are sent to Confident AI."""
    print("\nFlushing data to Confident AI...")
    try:
        deepeval.flush()
        print("   ✓ All data flushed")
    except AttributeError:
        time.sleep(5)  # fallback for older deepeval versions


def _extract_sections_from_crew(crew_instance, raw_output: str) -> dict[str, str]:
    """Extract documentation sections from crew output."""
    sections = _split_sections(raw_output)

    if not sections:
        print("\nNote: Section markers not found. Building from individual task outputs...")
        file_map = {
            "getting_started": "README.md",
            "api_semantics": "API_REFERENCE.md",
            "architecture": "ARCHITECTURE.md",
            "examples_generation": "EXAMPLES.md",
        }
        for task in crew_instance.tasks:
            task_output = task.output
            if not task_output:
                continue
            text = ""
            if hasattr(task_output, "raw") and task_output.raw:
                text = task_output.raw
            elif hasattr(task_output, "result"):
                text = str(task_output.result)
            elif isinstance(task_output, str):
                text = task_output
            if not text.strip():
                continue
            task_desc = ""
            if task.config and isinstance(task.config, dict):
                task_desc = str(task.config.get("description", ""))
            for keyword, filename in file_map.items():
                if keyword in task_desc.lower():
                    sections[filename] = text
                    break
            mermaid_match = re.search(r"```mermaid\s*\n(.*?)```", text, re.DOTALL)
            if mermaid_match:
                sections["architecture.mermaid"] = mermaid_match.group(1).strip()

    return sections


def _write_final_docs(
    sections: dict[str, str], raw_output: str, folder_path: str, crew_instance
) -> None:
    """Create Pydantic output, save docs, and print summary."""
    shared_mem = SharedMemory()
    language = shared_mem.get("language", "unknown")

    doc_output = DocumentationOutput(
        generated_at=datetime.now(),
        codebase_path=folder_path,
        language=language,
        readme=sections.get("README.md", DEFAULT_FILES["README.md"]),
        api_reference=sections.get("API_REFERENCE.md", DEFAULT_FILES["API_REFERENCE.md"]),
        architecture=sections.get("ARCHITECTURE.md", DEFAULT_FILES["ARCHITECTURE.md"]),
        examples=sections.get("EXAMPLES.md", DEFAULT_FILES["EXAMPLES.md"]),
        test_documentation=sections.get("TEST_DOCUMENTATION.md", DEFAULT_FILES["TEST_DOCUMENTATION.md"]),
        architecture_diagram=sections.get(
            "architecture.mermaid", DEFAULT_FILES["architecture.mermaid"]
        ),
        summary=f"Generated documentation for {language} codebase",
        total_files=len(shared_mem.get("source_files", {})),
        total_endpoints=_count_endpoints(sections.get("API_REFERENCE.md", "")),
    )

    docs_dir = Path("docs")
    doc_output.save_to_folder(str(docs_dir))
    combined = Path("technical_documentation.md")
    combined.write_text(raw_output, encoding="utf-8")

    print(f"\n{'='*70}")
    print(f"Documentation generation completed!")
    print(f"{'='*70}")
    print(f"\nOutput directory: {docs_dir.absolute()}/")
    print(f"  ├── README.md")
    print(f"  ├── API_REFERENCE.md")
    print(f"  ├── ARCHITECTURE.md")
    print(f"  ├── EXAMPLES.md")
    print(f"  ├── TEST_DOCUMENTATION.md")
    print(f"  └── diagrams/")
    print(f"      └── architecture.mermaid")
    print(f"\nCombined: {combined.absolute()}")
    print(f"Language: {language} | Files: {doc_output.total_files} | Endpoints: {doc_output.total_endpoints}")
    print(f"{'='*70}\n")


def run():
    """
    Run the documentation generation crew.

    Pipeline:
      1. Execute crew (all agents + tasks)
      2. Capture trace → Confident AI → Observability → Traces
      3. Evaluate with GEval → Confident AI → Testing → Test Runs
      4. Retry if avg score < MIN_EVAL_SCORE (up to MAX_RETRY_ATTEMPTS)
      5. Write docs after evaluation passes or retries exhausted
      6. Flush all data to Confident AI
    """
    print(f"\n{'='*70}")
    print(f"DOCUMENTATION GENERATION SYSTEM")
    print(f"{'='*70}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Threshold: {MIN_EVAL_SCORE}/10 | Max retries: {MAX_RETRY_ATTEMPTS}")
    print(f"\nConfident AI:")
    print(f"  Traces  → Observability → Traces")
    print(f"  Metrics → Testing → Test Runs")
    print(f"{'='*70}\n")

    SharedMemory().clear()

    while True:
        folder_path = input(
            "Enter local folder path OR GitHub URL (Enter = current dir): "
        ).strip()

        if not folder_path:
            folder_path = os.getcwd()
            print(f"Using current directory: {folder_path}")
            break
        if _is_git_url(folder_path):
            print("Detected GitHub URL. Cloning...")
            folder_path = _clone_repo(folder_path)
            print(f"Cloned to: {folder_path}")
            break
        folder = Path(folder_path)
        if not folder.exists():
            print(f"Error: '{folder_path}' does not exist.\n")
            continue
        if not folder.is_dir():
            print(f"Error: '{folder_path}' is not a directory.\n")
            continue
        break

    folder_path = str(Path(folder_path).absolute())
    print(f"\n{'='*70}")
    print(f"Processing: {folder_path}")
    print(f"{'='*70}\n")

    inputs = {"folder_path": folder_path, "timestamp": datetime.now().isoformat()}

    try:
        # ── 1: Execute crew with full trace logging ────────────────────
        print("[1] Executing crew pipeline (traced)...")
        result, crew_instance, raw_output = _run_crew_traced(inputs)

        # ── 2: Evaluate ────────────────────────────────────────────────
        attempt = 1
        print(f"\n[2] Evaluating (attempt {attempt})...")
        eval_result = _run_evaluation_traced(raw_output, folder_path, attempt=attempt)
        avg_score = eval_result["avg_score"]

        best_output, best_score = raw_output, avg_score

        # ── 3: Retry if needed ─────────────────────────────────────────
        while avg_score < MIN_EVAL_SCORE and attempt < MAX_RETRY_ATTEMPTS:
            attempt += 1
            print(f"\n{'='*70}")
            print(f"Score {avg_score:.2f} below {MIN_EVAL_SCORE}. Retry {attempt}/{MAX_RETRY_ATTEMPTS}...")
            print(f"{'='*70}\n")

            try:
                retry_inputs = {"folder_path": folder_path, "timestamp": datetime.now().isoformat()}
                retry_result, retry_crew, raw_output = _run_crew_traced(retry_inputs)
                crew_instance = retry_crew
                result = retry_result
            except Exception as e:
                print(f"   Retry failed: {e}")
                break

            print(f"\n[2] Evaluating (attempt {attempt})...")
            eval_result = _run_evaluation_traced(raw_output, folder_path, attempt=attempt)
            avg_score = eval_result["avg_score"]

            if avg_score > best_score:
                best_score, best_output = avg_score, raw_output

        if best_score > avg_score:
            raw_output, avg_score = best_output, best_score

        # ── 4: Summary ─────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print(f"Final Score: {avg_score:.2f}/10 after {attempt} attempt(s)")
        if avg_score >= MIN_EVAL_SCORE:
            print(f"✓ PASSED")
            print(f"  → app.confident-ai.com → Observability → Traces")
            print(f"  → app.confident-ai.com → Testing → Test Runs")
        else:
            print(f"✗ BELOW THRESHOLD — using best available output")
        print(f"{'='*70}\n")

        # ── 5: Human-in-the-Loop Approval ──────────────────────────────
        sections = _extract_sections_from_crew(crew_instance, raw_output)

        # Initialize human-in-the-loop system
        hitl = HumanInTheLoop(auto_approve=False)

        # Request human approval before saving
        print("\n" + "=" * 70)
        print("INITIATING HUMAN-IN-THE-LOOP APPROVAL")
        print("=" * 70)

        approval_result = hitl.request_approval(sections, raw_output)

        if approval_result.status == ApprovalStatus.EDIT_REQUESTED:
            print("\n📝 Re-running agents with human feedback...")
            print(f"   Feedback: {approval_result.feedback[:100]}...")

            # Re-run crew with feedback (code_analyzer already ran, so we skip it)
            # The feedback is injected into the task descriptions for the downstream agents
            edit_inputs = {
                "folder_path": folder_path,
                "timestamp": datetime.now().isoformat(),
                "human_feedback": approval_result.feedback,
            }

            # Re-run the crew with feedback using the special edit iteration crew
            print("\n[1] Re-executing crew pipeline with feedback (skipping code analysis)...")
            
            doc_gen = DocGenerator()
            edit_crew = doc_gen.crew_for_edit_iteration(edit_inputs)
            result = edit_crew.kickoff(inputs=edit_inputs)
            
            # Extract output from edit crew
            raw_output = _extract_final_output(edit_crew)
            if not raw_output:
                raw_output = getattr(result, "raw", None) or (
                    result if isinstance(result, str) else str(result)
                )
            
            # Extract new sections
            sections = _extract_sections_from_crew(edit_crew, raw_output)

            print("\n✓ Agents re-run complete. Proceeding to save updated documentation...")

        else:  # APPROVED
            print("\n✅ Documentation approved by human operator. Proceeding to save...")

        # ── 6: Write docs ──────────────────────────────────────────────
        _write_final_docs(sections, raw_output, folder_path, crew_instance)

        # ── 7: Flush to Confident AI ───────────────────────────────────
        _flush_traces()

        return result

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """Train the crew for a given number of iterations."""
    if len(sys.argv) < 3:
        raise Exception("Usage: train <n_iterations> <filename> [folder_path]")
    folder_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Invalid folder: '{folder_path}'")
    try:
        DocGenerator().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs={"folder_path": str(folder.absolute()), "timestamp": datetime.now().isoformat()},
        )
    except Exception as e:
        raise Exception(f"Training failed: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    if len(sys.argv) < 2:
        raise Exception("Usage: replay <task_id>")
    try:
        DocGenerator().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"Replay failed: {e}")


def test():
    """Test the crew execution."""
    if len(sys.argv) < 3:
        raise Exception("Usage: test <n_iterations> <eval_llm> [folder_path]")
    folder_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Invalid folder: '{folder_path}'")
    try:
        DocGenerator().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs={"folder_path": str(folder.absolute()), "timestamp": datetime.now().isoformat()},
        )
    except Exception as e:
        raise Exception(f"Test failed: {e}")


def run_with_trigger():
    """Run the crew with a JSON trigger payload."""
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided.")
    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload")

    folder_path = trigger_payload.get("git_url") or trigger_payload.get("folder_path", os.getcwd())
    if _is_git_url(folder_path):
        folder_path = _clone_repo(folder_path)

    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Invalid folder: '{folder_path}'")

    SharedMemory().clear()
    try:
        return DocGenerator().crew().kickoff(inputs={
            "crewai_trigger_payload": trigger_payload,
            "folder_path": str(folder.absolute()),
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        raise Exception(f"Trigger run failed: {e}")