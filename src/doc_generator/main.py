#!/usr/bin/env python
"""
Documentation Generator – entry point.

Runs the multi-agent pipeline and writes the output into a `docs/` folder:

    docs/
    ├── README.md              (Overview + Getting Started)
    ├── API_REFERENCE.md       (All endpoints)
    ├── ARCHITECTURE.md        (System design + Mermaid)
    ├── EXAMPLES.md            (Code samples)
    └── diagrams/
         └── architecture.mermaid
"""

import re
import sys
import warnings
import os
from pathlib import Path
from datetime import datetime

from doc_generator.crew import DocGenerator
from doc_generator.tools.shared_memory import SharedMemory
from doc_generator.models import DocumentationOutput

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


# ── Section splitter ───────────────────────────────────────────────────
SECTION_PATTERN = re.compile(r"^===SECTION:\s*(.+?)\s*===$", re.MULTILINE)

DEFAULT_FILES = {
    "README.md": "# README\n\nDocumentation was not generated for this section.",
    "API_REFERENCE.md": "# API Reference\n\nDocumentation was not generated for this section.",
    "ARCHITECTURE.md": "# Architecture\n\nDocumentation was not generated for this section.",
    "EXAMPLES.md": "# Examples\n\nDocumentation was not generated for this section.",
    "architecture.mermaid": "graph TD\n  A[No diagram generated]",
}


def _split_sections(raw: str) -> dict[str, str]:
    """
    Split the Document Assembler output by ===SECTION: filename=== markers.
    Returns a dict mapping filename → content.
    """
    parts = SECTION_PATTERN.split(raw)
    sections: dict[str, str] = {}

    # parts looks like: [preamble, name1, content1, name2, content2, ...]
    i = 1
    while i < len(parts) - 1:
        name = parts[i].strip()
        content = parts[i + 1].strip()
        if name and content:
            sections[name] = content
        i += 2

    return sections


def _write_docs(sections: dict[str, str], output_dir: Path) -> list[str]:
    """
    Write each section to the appropriate file inside `output_dir`.
    Returns list of files written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    diagrams_dir = output_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []

    for filename, default_content in DEFAULT_FILES.items():
        content = sections.get(filename, default_content)

        if filename == "architecture.mermaid":
            filepath = diagrams_dir / filename
        else:
            filepath = output_dir / filename

        filepath.write_text(content, encoding="utf-8")
        written.append(str(filepath))

    return written


def _extract_final_output(crew_instance) -> str:
    """Extract the final assembler output from the crew run."""
    # Try to get the last task (document_assembly_task) output
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
    """Count the number of API endpoints documented in the API reference."""
    # Count lines starting with "###" or "####" (markdown headers for endpoints)
    # or count HTTP method patterns like "GET /", "POST /", etc.
    http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    count = 0
    for line in api_reference.split("\n"):
        for method in http_methods:
            if f"**{method}**" in line or f"`{method}" in line or f"| {method}" in line:
                count += 1
                break
    return count


# ── Main entry points ─────────────────────────────────────────────────

def run():
    """
    Run the documentation generation crew.
    Prompts user for folder path to process the entire codebase.
    Uses Pydantic DocumentationOutput for structured output.
    """
    print(f"\n{'='*70}")
    print(f"DOCUMENTATION GENERATION SYSTEM")
    print(f"{'='*70}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    # Clear shared memory from any previous run
    SharedMemory().clear()

    # Prompt user for folder path
    while True:
        folder_path = input(
            "Enter the path to the codebase folder (or press Enter for current directory): "
        ).strip()

        if not folder_path:
            folder_path = os.getcwd()
            print(f"Using current directory: {folder_path}")
            break

        folder = Path(folder_path)
        if not folder.exists():
            print(f"Error: Folder path '{folder_path}' does not exist. Please try again.\n")
            continue
        if not folder.is_dir():
            print(f"Error: '{folder_path}' is not a directory. Please try again.\n")
            continue
        break

    folder_path = str(Path(folder_path).absolute())

    print(f"\n{'='*70}")
    print(f"Processing codebase at: {folder_path}")
    print(f"{'='*70}\n")

    inputs = {
        "folder_path": folder_path,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        crew_instance = DocGenerator().crew()
        result = crew_instance.kickoff(inputs=inputs)

        # ── Extract final output ───────────────────────────────────────
        raw_output = _extract_final_output(crew_instance)
        if not raw_output:
            if hasattr(result, "raw"):
                raw_output = result.raw
            elif isinstance(result, str):
                raw_output = result
            else:
                raw_output = str(result)

        # ── Split into sections and write docs/ folder ─────────────────
        sections = _split_sections(raw_output)

        # Fallback: if the assembler didn't use section markers, try to
        # build sections from individual task outputs
        if not sections:
            print("\nNote: Section markers not found. Building docs from individual task outputs...")
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

                # Match task to output file
                task_desc = ""
                if task.config and isinstance(task.config, dict):
                    task_desc = str(task.config.get("description", ""))
                for keyword, filename in file_map.items():
                    if keyword in task_desc.lower():
                        sections[filename] = text
                        break

                # Extract mermaid diagram if present
                mermaid_match = re.search(
                    r"```mermaid\s*\n(.*?)```", text, re.DOTALL
                )
                if mermaid_match:
                    sections["architecture.mermaid"] = mermaid_match.group(1).strip()

        # ── Create Pydantic DocumentationOutput ─────────────────────────
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
            architecture_diagram=sections.get("architecture.mermaid", DEFAULT_FILES["architecture.mermaid"]),
            summary=f"Generated documentation for {language} codebase",
            total_files=len(shared_mem.get("source_files", {})),
            total_endpoints=_count_endpoints(sections.get("API_REFERENCE.md", "")),
        )

        # ── Save to organized folder structure ──────────────────────────
        docs_dir = Path("docs")
        doc_output.save_to_folder(str(docs_dir))

        # Also write a combined file for backward compatibility
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
        print(f"  └── diagrams/")
        print(f"      └── architecture.mermaid")
        print(f"\nCombined output: {combined.absolute()}")
        print(f"Language detected: {language}")
        print(f"Total files analyzed: {doc_output.total_files}")
        print(f"Total endpoints documented: {doc_output.total_endpoints}")
        print(f"Tasks executed: {len(crew_instance.tasks)}")
        print(f"{'='*70}\n")
        return result

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    if len(sys.argv) < 3:
        raise Exception("Usage: train <n_iterations> <filename> [folder_path]")

    folder_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Error: Invalid folder path '{folder_path}'")

    inputs = {
        "folder_path": str(folder.absolute()),
        "timestamp": datetime.now().isoformat(),
    }

    try:
        DocGenerator().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    if len(sys.argv) < 2:
        raise Exception("Usage: replay <task_id>")

    try:
        DocGenerator().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    if len(sys.argv) < 3:
        raise Exception("Usage: test <n_iterations> <eval_llm> [folder_path]")

    folder_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Error: Invalid folder path '{folder_path}'")

    inputs = {
        "folder_path": str(folder.absolute()),
        "timestamp": datetime.now().isoformat(),
    }

    try:
        DocGenerator().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    folder_path = trigger_payload.get("folder_path", os.getcwd())
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        raise Exception(f"Error: Invalid folder path '{folder_path}'")

    SharedMemory().clear()

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "folder_path": str(folder.absolute()),
        "timestamp": datetime.now().isoformat(),
    }

    try:
        result = DocGenerator().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
