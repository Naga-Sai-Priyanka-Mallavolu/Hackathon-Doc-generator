from dotenv import load_dotenv
import os
import ssl
import certifi
import json
import uuid
import shutil
import tempfile
import zipfile
import subprocess
import re
import concurrent.futures
import traceback
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from doc_generator.crew import DocGenerator
from doc_generator.tools.shared_memory import SharedMemory
from doc_generator.models import DocumentationOutput
from doc_generator.geval_metrics import evaluate_docs

# Fix for macOS SSLCertVerificationError - apply globally
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
ssl_context = ssl.create_default_context(cafile=certifi.where())
if hasattr(ssl, 'DefaultVerifyPaths'):
    ssl.get_default_verify_paths = lambda: ssl.DefaultVerifyPaths(
        cafile=certifi.where(),
        capath=None,
        openssl_cafile_env='SSL_CERT_FILE',
        openssl_capath_env='SSL_CERT_DIR',
        openssl_cafile=certifi.where(),
        openssl_capath=None
    )

load_dotenv()

# ─────────────────────────────────────────────────────────────




app = FastAPI(title="Documentation Generator API")

# Add middleware BEFORE mounting static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Expand for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("docs").mkdir(parents=True, exist_ok=True)
app.mount("/docs-static", StaticFiles(directory="docs"), name="docs")

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


def _count_endpoints(api_reference: str) -> dict[str, int]:
    """
    Extract endpoint counts by HTTP method from the API reference markdown.
    Returns: {"GET": n, "POST": m, ...}
    """
    http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    stats = {method: 0 for method in http_methods}
    
    for line in api_reference.split("\n"):
        for method in http_methods:
            # Match patterns like **GET** or `GET`
            if f"**{method}**" in line or f"`{method}" in line:
                stats[method] += 1
                break
    
    # Filter out zero counts
    return {k: v for k, v in stats.items() if v > 0}


def _calculate_file_stats(source_files: dict) -> list[dict]:
    """
    Calculate file statistics by extension.
    Returns a list of dicts: [{"name": ".py", "value": 10}, ...]
    """
    stats = {}
    for file_path in source_files.keys():
        ext = Path(file_path).suffix
        if not ext:
            ext = "no_extension"
        stats[ext] = stats.get(ext, 0) + 1
    
    # Convert to list for Recharts
    return [{"name": k, "value": v} for k, v in sorted(stats.items(), key=lambda x: x[1], reverse=True)]


def _get_structural_stats(shared_mem: SharedMemory) -> list[dict]:
    """Extract total counts for classes, functions, and imports."""
    classes = shared_mem.get("classes", {})
    functions = shared_mem.get("functions", {})
    imports = shared_mem.get("imports", {})

    total_classes = sum(len(v) for v in classes.values()) if isinstance(classes, dict) else 0
    total_funcs = sum(len(v) for v in functions.values()) if isinstance(functions, dict) else 0
    total_imports = sum(len(v) for v in imports.values()) if isinstance(imports, dict) else 0

    return [
        {"name": "Classes", "value": total_classes},
        {"name": "Functions", "value": total_funcs},
        {"name": "Imports", "value": total_imports},
    ]


def _get_section_stats(sections: dict) -> list[dict]:
    """Calculate character counts for each documentation section."""
    return [
        {"name": k.replace(".md", ""), "value": len(v)}
        for k, v in sections.items()
        if not k.endswith(".mermaid")
    ]


def _get_project_breadth_stats(shared_mem: SharedMemory) -> list[dict]:
    """Categorize files into Source, Config, and Tests."""
    source_files = shared_mem.get("source_files", {})
    categories = {"Source Code": 0, "Configuration": 0, "Tests": 0}
    
    config_exts = {".yaml", ".yml", ".json", ".toml", ".env", ".yaml", ".yml", ".ini", ".conf"}
    
    for file_path in source_files.keys():
        path_lower = file_path.lower()
        ext = Path(file_path).suffix.lower()
        
        if "test" in path_lower or "/tests/" in path_lower:
            categories["Tests"] += 1
        elif ext in config_exts:
            categories["Configuration"] += 1
        else:
            categories["Source Code"] += 1
            
    return [{"name": k, "value": v} for k, v in categories.items() if v > 0]


def _run_evaluation(output: str, folder_path: str) -> dict:
    """
    Minimal wrapper to run evaluation without blocking the server loop.
    """
    session_id = str(uuid.uuid4())[:8]
    print(f"\n[EVAL] Starting evaluation session {session_id}...")
    
    # Run in thread to avoid uvloop conflicts and blocking
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(evaluate_docs, output, folder_path)
        eval_result = future.result()
    
    # Display results in console
    for name, score in eval_result["scores"].items():
        print(f"  - {name.replace('_', ' ').title()}: {score}/10")

    return {
        "scores": eval_result["scores"],
        "average_score": eval_result["avg_score"],
        "session_id": session_id
    }


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
    
    try:
        crew_instance = DocGenerator().crew()
        result = crew_instance.kickoff(inputs=inputs)

        raw_output = _extract_final_output(crew_instance)
        if not raw_output:
            raw_output = str(result)

        sections = _split_sections(raw_output)

        shared_mem = SharedMemory()
        language = shared_mem.get("language", "unknown")

        endpoint_stats = _count_endpoints(sections.get("API_REFERENCE.md", ""))
        total_endpoints = sum(endpoint_stats.values())

        # -- Run Evaluation --
        print(f"Starting evaluation...")
        eval_data = _run_evaluation(raw_output, folder_path)
        print(f"Metrics: language={language}, files={len(shared_mem.get('source_files', {}))}, endpoints={total_endpoints}, score={eval_data['average_score']:.2f}")

        # Initialize stats variables with defaults to avoid UnboundLocalError
        file_stats = []
        endpoint_stats_list = []
        structural_stats = []

        # -- Inject Charts into Markdown --
        try:
            file_stats = _calculate_file_stats(shared_mem.get("source_files", {}))
            breadth_stats = _get_project_breadth_stats(shared_mem)
            endpoint_stats_list = [{"name": k, "value": v} for k, v in endpoint_stats.items()]
            structural_stats = _get_structural_stats(shared_mem)

            # 1. README: Project Breadth (High Level)
            readme = sections.get("README.md", DEFAULT_FILES["README.md"])
            readme_charts = ""
            if breadth_stats:
                readme_charts += f"### Project Composition\n```chart\n{json.dumps({'type': 'project_breadth', 'data': breadth_stats}, indent=2)}\n```\n\n"
            readme_charts += f"### File Extension Distribution\n```chart\n{json.dumps({'type': 'file_dist', 'data': file_stats}, indent=2)}\n```\n\n"
            readme = readme_charts + readme

            # 2. API Reference: Method Breakdown (Complexity chart removed as requested)
            api_ref = sections.get("API_REFERENCE.md", DEFAULT_FILES["API_REFERENCE.md"])
            api_charts = ""
            if endpoint_stats_list:
                api_charts += f"### API Method Distribution\n```chart\n{json.dumps({'type': 'api_methods', 'data': endpoint_stats_list}, indent=2)}\n```\n\n"
            api_ref = api_charts + api_ref

            # 3. Architecture: Structural Stats (Quality chart removed as requested)
            arch = sections.get("ARCHITECTURE.md", DEFAULT_FILES["ARCHITECTURE.md"])
            arch_charts = f"### Structural Analysis\n```chart\n{json.dumps({'type': 'structural', 'data': structural_stats}, indent=2)}\n```\n\n"
            arch = arch_charts + arch
        except Exception as chart_err:
            print(f"Warning: Failed to inject charts: {chart_err}")
            readme = sections.get("README.md", DEFAULT_FILES["README.md"])
            api_ref = sections.get("API_REFERENCE.md", DEFAULT_FILES["API_REFERENCE.md"])
            arch = sections.get("ARCHITECTURE.md", DEFAULT_FILES["ARCHITECTURE.md"])

        doc_output = DocumentationOutput(
            generated_at=datetime.now(),
            codebase_path=folder_path,
            language=language,
            readme=readme,
            api_reference=api_ref,
            architecture=arch,
            examples=sections.get("EXAMPLES.md", DEFAULT_FILES["EXAMPLES.md"]),
            test_documentation=sections.get("TEST_DOCUMENTATION.md", "# Test Documentation\n\nNo test files were found in the project."),
            architecture_diagram=sections.get("architecture.mermaid", DEFAULT_FILES["architecture.mermaid"]),
            summary=f"Generated documentation for {language} codebase",
            total_files=len(shared_mem.get("source_files", {})),
            total_endpoints=total_endpoints,
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
            f"## EXAMPLES\n{doc_output.examples}\n\n"
            f"## TEST DOCUMENTATION\n{doc_output.test_documentation}\n"
        )
        Path("technical_documentation.md").write_text(combined_content, encoding="utf-8")

        print(f"Documentation generated successfully for: {folder_path}")
        
        return {
            "language": doc_output.language,
            "total_files": doc_output.total_files,
            "total_endpoints": doc_output.total_endpoints,
            "docs_path": str(docs_dir.absolute()),
            "file_stats": file_stats,
            "endpoint_stats": endpoint_stats_list,
            "structural_stats": structural_stats,
            "section_stats": _get_section_stats(sections),
            "evaluation": eval_data
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e


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
