from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import tempfile
import zipfile
import subprocess
import re
from datetime import datetime
import os

from doc_generator.crew import DocGenerator
from doc_generator.tools.shared_memory import SharedMemory
from doc_generator.models import DocumentationOutput
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI(title="Documentation Generator API")

Path("docs").mkdir(parents=True, exist_ok=True)
app.mount("/docs-static", StaticFiles(directory="docs"), name="docs")
# ─────────────────────────────────────────────────────────────
# SECTION SPLITTING LOGIC (Same as main.py)
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    count = 0
    for line in api_reference.split("\n"):
        for method in http_methods:
            if f"**{method}**" in line or f"`{method}" in line:
                count += 1
                break
    return count


# ─────────────────────────────────────────────────────────────
# CORE DOCUMENT GENERATION FUNCTION
# ─────────────────────────────────────────────────────────────

def generate_docs(folder_path: str):
    # Optional: Clear SharedMemory if still used by some internal tools
    SharedMemory().clear()

    folder_path = str(Path(folder_path).absolute())

    inputs = {
        "folder_path": folder_path,
        "timestamp": datetime.now().isoformat(),
    }

    print(f"Starting documentation generation for: {folder_path}")
    crew_instance = DocGenerator().crew()
    result = crew_instance.kickoff(inputs=inputs)

    raw_output = _extract_final_output(crew_instance)
    if not raw_output:
        raw_output = str(result)

    sections = _split_sections(raw_output)

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

    # Save to the docs folder
    docs_dir = Path("docs")
    doc_output.save_to_folder(str(docs_dir))

    # Also save the raw markdown to a single file for reference
    combined_content = (
        f"# Technical Documentation\n\n"
        f"## README\n{doc_output.readme}\n\n"
        f"## API REFERENCE\n{doc_output.api_reference}\n\n"
        f"## ARCHITECTURE\n{doc_output.architecture}\n\n"
        f"## EXAMPLES\n{doc_output.examples}\n"
    )
    Path("technical_documentation.md").write_text(combined_content, encoding="utf-8")

    print(f"Documentation generated successfully for: {folder_path}")
    print(f"Metrics: language={doc_output.language}, files={doc_output.total_files}, endpoints={doc_output.total_endpoints}")

    return {
        "language": doc_output.language,
        "total_files": doc_output.total_files,
        "total_endpoints": doc_output.total_endpoints,
        "docs_path": str(docs_dir.absolute()),
    }


# ─────────────────────────────────────────────────────────────
# GIT REPOSITORY ENDPOINT
# ─────────────────────────────────────────────────────────────

@app.post("/generate-from-git")
async def generate_from_git(git_url: str = Form(...)):
    temp_dir = tempfile.mkdtemp(prefix="docgen_")

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", git_url, temp_dir],
            check=True,
        )

        metrics = generate_docs(temp_dir)

        return JSONResponse({
            "status": "success",
            "metrics": metrics
        })

    except Exception as e:
        print(f"Error in generate_from_git: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/generate-from-path")
async def generate_from_path(folder_path: str = Form(...)):
    try:
        folder = Path(folder_path)

        if not folder.exists():
            return JSONResponse(
                {"error": f"Path does not exist: {folder_path}"},
                status_code=400
            )

        if not folder.is_dir():
            return JSONResponse(
                {"error": f"Path is not a directory: {folder_path}"},
                status_code=400
            )

        metrics = generate_docs(str(folder.absolute()))

        return JSONResponse({
            "status": "success",
            "metrics": metrics
        })

    except Exception as e:
        print(f"Error in generate_from_path: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/traces")
async def get_traces():
    """Fetch all agent traces from PostgreSQL."""
    try:
        shared_mem = SharedMemory()
        traces = shared_mem.get("agent_traces", [])
        return JSONResponse({"status": "success", "traces": traces})
    except Exception as e:
        print(f"Error fetching traces: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)
