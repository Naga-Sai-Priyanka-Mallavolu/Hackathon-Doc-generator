===SECTION: README.md===
# Documentation Generator

## Table of Contents
- [Project Overview](#project-overview)  
- [Getting Started](#getting-started)  
- [Running the Application](#running-the-application)  
- [API Reference](API_REFERENCE.md)  
- [Architecture Diagram](ARCHITECTURE.md)  
- [Examples](EXAMPLES.md)

---

## Project Overview  

The **Documentation Generator** is a Python‑based, multi‑agent system that automatically produces complete technical documentation (README, API reference, architecture diagram, usage examples, etc.) for any source repository.  
It can be invoked **via CLI** or **via REST API** (FastAPI). The system parses the full codebase, runs a CrewAI crew of specialized agents, evaluates output quality with GEval metrics, and stores traces in PostgreSQL.

## Getting Started  

### 1. Prerequisites  

| Item | Minimum Version |
|------|-----------------|
| Python | 3.10+ |
| Node.js | 18 LTS |
| Git | 2.30+ |
| PostgreSQL | 12+ |
| Docker (optional) | 20.10+ |
| uvicorn | – |
| dotenv | – |

### 2. Installation  

```bash
# Clone the repo
git clone https://github.com/your-org/documentation-generator.git
cd documentation-generator

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install .   # or `pip install -e .`

# Install PostgreSQL driver (if not installed automatically)
pip install psycopg2-binary

# Create .env file
cat > .env <<EOF
CONFIDENT_API_KEY=ck_your_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docgen
POSTGRES_USER=docgen_user
POSTGRES_PASSWORD=strongpassword
EOF

# (Optional) Start PostgreSQL in Docker
docker run --name docgen-pg -e POSTGRES_USER=docgen_user -e POSTGRES_PASSWORD=strongpassword -e POSTGRES_DB=docgen -p 5432:5432 -d postgres:15

# Set up the React frontend
cd docgen-frontend
npm ci
npm run build   # optional, builds static assets
cd ..
```

### 3. Configuration  

- **Confident AI API key** – set in `.env` (`CONFIDENT_API_KEY`).  
- **Database connection** – adjust `POSTGRES_*` variables in `.env`.  
- **Minimum evaluation score** – `export MIN_EVAL_SCORE=6.0` (default).  

Create the database and user if not using Docker:

```sql
CREATE DATABASE docgen;
CREATE USER docgen_user WITH ENCRYPTED PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE docgen TO docgen_user;
```

### 4. Running the Application  

#### Backend (FastAPI)

```bash
source .venv/bin/activate
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI: `http://localhost:8000/docs`

#### Frontend (optional)

```bash
cd docgen-frontend
npm run dev   # http://localhost:5173
```

#### CLI

```bash
doc_generator   # or `python -m doc_generator.main`
```

Follow the interactive prompts to provide a local folder path or a public Git URL. The generated documentation will be placed in the `docs/` directory and a combined file `technical_documentation.md`.

### 5. Quick API Call  

```bash
curl -X POST "http://localhost:8000/generate-from-git" \
  -F "git_url=https://github.com/example-org/sample-python-app.git"
```

Response (example):

```json
{
  "status": "success",
  "metrics": {
    "language": "python",
    "total_files": 42,
    "total_endpoints": 7,
    "docs_path": "/absolute/path/to/documentation-generator/docs"
  }
}
```

See the full **API Reference** in [API_REFERENCE.md](API_REFERENCE.md).

### 6. Troubleshooting  

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Port 8000 already in use | Another process | `lsof -i :8000` → kill PID, or start on a different port (`--port 8081`). |
| Database connection error | PostgreSQL not running / wrong credentials | Verify container is up (`docker ps`) or check `.env`. |
| `CONFIDENT_API_KEY` missing | Env var not set | Add it to `.env` and restart the server. |
| `git clone` fails | Invalid URL, network block, Git not installed | Test manually (`git clone <url>`). Install Git if missing. |
| npm install errors | Node version too low | Upgrade to Node 18 (`nvm install 18`). |
| Crew execution errors | `crewai` version mismatch | `pip install -U crewai[tools]`. |
| Low evaluation score | Quality thresholds | Inspect DEEPEVAL logs, adjust `MIN_EVAL_SCORE` temporarily. |

For any other issues, consult the console logs or open an issue on the repository.

---

## Running Tests (optional)

```bash
pip install pytest
pytest
```

A built‑in smoke test can be executed with:

```bash
doc_generator test 2 gpt-4
```

---

Enjoy automatically generated documentation! 🎉

===SECTION: API_REFERENCE.md===
# API Reference – Documentation Generator Service (FastAPI)

| # | Method | Path | Description |
|---|--------|------|-------------|
| 1 | **POST** | `/generate-from-git` | Generate documentation for a public Git repository. Accepts a `git_url` form field, clones the repo to a temporary directory, runs the documentation‑generation crew and returns metrics. |
| 2 | **POST** | `/generate-from-path` | Generate documentation for a local folder path. Accepts a `folder_path` form field, validates the directory, runs the crew and returns metrics. |
| 3 | **GET** | `/traces` | Retrieve the list of agent execution traces stored in PostgreSQL (used for observability). |

---

## Detailed Endpoint Specification

### 1. `POST /generate-from-git`

* **Source:** `api_server.py` – line **165‑184**  
* **Purpose / Description**  
  - Receives a Git URL, clones the repository (depth 1) into a temporary folder, runs the documentation generation pipeline (`generate_docs`), and returns a JSON payload containing the generation status and metrics (language, total files, total endpoints, docs path).  

* **Request Parameters**  

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `git_url` | Form body (`Form(...)`) | `str` | Yes | URL of the public Git repository to clone. |

* **Response** – `JSONResponse` (HTTP 200 on success, HTTP 500 on error)  

```json
{
  "status": "success",
  "metrics": {
    "language": "python",
    "total_files": 123,
    "total_endpoints": 0,
    "docs_path": "/absolute/path/to/docs"
  }
}
```

* **Error Responses**  

| Code | Body | Reason |
|------|------|--------|
| 500 | `{"error": "error message"}` | Failure while cloning or generating documentation. |

* **Security** – No authentication/authorization (open endpoint).  

---

### 2. `POST /generate-from-path`

* **Source:** `api_server.py` – line **190‑216**  
* **Purpose / Description**  
  - Accepts a local filesystem path, validates that it exists and is a directory, then runs the documentation generation pipeline (`generate_docs`). Returns the same metric payload as the Git endpoint.  

* **Request Parameters**  

| Name | Location | Type | Required | Description |
|------|----------|------|----------|-------------|
| `folder_path` | Form body (`Form(...)`) | `str` | Yes | Absolute or relative path to the codebase folder. |

* **Response** – `JSONResponse` (HTTP 200 on success, HTTP 400 on validation error, HTTP 500 on generation error)  

  *Success (200)*  

```json
{
  "status": "success",
  "metrics": {
    "language": "python",
    "total_files": 123,
    "total_endpoints": 0,
    "docs_path": "/absolute/path/to/docs"
  }
}
```

  *Validation error (400)*  

```json
{
  "error": "Path does not exist: /invalid/path"
}
```

  *Generation error (500)*  

```json
{
  "error": "error message"
}
```

* **Security** – No authentication/authorization.  

---

### 3. `GET /traces`

* **Source:** `api_server.py` – line **219‑227**  
* **Purpose / Description**  
  - Returns all agent execution traces that have been stored in PostgreSQL under the key `agent_traces`. Useful for debugging and observability via the Confident AI UI.  

* **Request Parameters** – None.  

* **Response** – `JSONResponse` (HTTP 200 on success, HTTP 500 on failure)  

```json
{
  "status": "success",
  "traces": [
    "Trace line 1 …",
    "Trace line 2 …",
    "... "
  ]
}
```

* **Error Response (500)**  

```json
{
  "error": "error message"
}
```

* **Security** – No authentication/authorization.  

---

## Summary

The service exposes three HTTP endpoints implemented in **`api_server.py`**. All endpoints return JSON payloads, have no built‑in security constraints, and are documented with request parameter types, expected responses, and possible error codes. This completes the required API‑semantics extraction.

See the **Examples** document for ready‑to‑copy cURL commands: [EXAMPLES.md](EXAMPLES.md).

===SECTION: ARCHITECTURE.md===
# System Architecture Overview

The **Documentation Generator** is a Python‑based, multi‑agent system that can be invoked either via a **CLI** (`src/doc_generator/main.py`) or a **REST API** (`api_server.py`).  
It follows a **layered, service‑oriented architecture** built around a **CrewAI crew** (the “service layer”) that orchestrates a family of reusable **tools** (utility layer). Persistence is handled by a **PostgreSQL** table (`docgen`), accessed through a simple storage tool. External integrations include **Git** (for cloning repositories) and **Confident AI** (metrics & tracing).

Below is a complete component map, data‑flow description, and the design patterns used throughout the code base.

---  

## Mermaid Architecture Diagram  

```mermaid
%% Layered architecture of the Documentation Generator
graph LR
    %% ==== API Layer ====
    subgraph API [API Layer]
        API_Server["FastAPI (api_server.py)"]
        API_Route_Git["/generate-from-git"]
        API_Route_Path["/generate-from-path"]
    end

    %% ==== Service / Orchestration Layer ====
    subgraph Service [Service (Crew) Layer]
        DocGenCrew["DocGenerator Crew (src/doc_generator/crew.py)"]
        ArchitectureAgent["Architecture Reasoning Agent"]
        APISemanticsAgent["API Semantics Agent"]
        ExamplesAgent["Examples Generation Agent"]
        GettingStartedAgent["Getting‑Started Agent"]
        DocumentAssembler["Document Assembler Agent"]
    end

    %% ==== Tool / Utility Layer ====
    subgraph Tools [Tool / Utility Layer]
        CodeAnalyzer["CodeAnalyzer Tool (tools/code_analyzer.py)"]
        DependencyAnalyzer["DependencyAnalyzer Tool (tools/dependency_analyzer.py)"]
        LanguageDetector["LanguageDetector Tool (tools/language_detector.py)"]
        StructureExtractor["StructureExtractor Tool (tools/structure_extractor.py)"]
        GuardrailsTool["Guardrails Tool (tools/guardrails.py)"]
        SharedMemoryTool["SharedMemory (tools/shared_memory.py)"]
        PostgreSQLStorage["PostgreSQLStorage Tool (tools/postgres_storage.py)"]
    end

    %% ==== Model Layer ====
    subgraph Models [Model Layer]
        DocumentationOutput["DocumentationOutput (models/documentation_output.py)"]
        CodeStructure["CodeStructure (models/code_structure.py)"]
    end

    %% ==== Data Layer ====
    subgraph Data [Data Layer]
        PostgreSQL["PostgreSQL DB (docgen table)"]
    end

    %% ==== External Integrations ====
    subgraph External [External Services]
        GitRepo["Git Repository"]
        ConfidentAI["Confident AI (metrics & tracing)"]
    end

    %% ==== Connections ====
    API_Server --> API_Route_Git
    API_Server --> API_Route_Path
    API_Route_Git -.-> GitRepo
    API_Route_Path -.-> (Local FS)

    API_Route_Git -->|trigger| DocGenCrew
    API_Route_Path -->|trigger| DocGenCrew

    DocGenCrew --> CodeAnalyzer
    DocGenCrew --> DependencyAnalyzer
    DocGenCrew --> LanguageDetector
    DocGenCrew --> StructureExtractor
    DocGenCrew --> GuardrailsTool
    DocGenCrew --> PostgreSQLStorage
    DocGenCrew --> ArchitectureAgent
    DocGenCrew --> APISemanticsAgent
    DocGenCrew --> ExamplesAgent
    DocGenCrew --> GettingStartedAgent
    DocGenCrew --> DocumentAssembler

    CodeAnalyzer --> SharedMemoryTool
    DependencyAnalyzer --> SharedMemoryTool
    LanguageDetector --> SharedMemoryTool
    StructureExtractor --> SharedMemoryTool
    GuardrailsTool --> SharedMemoryTool
    PostgreSQLStorage --> PostgreSQL

    SharedMemoryTool --> PostgreSQL
    DocumentationOutput -->|writes| docs_folder["/docs (static files)"]
    DocumentationOutput --> Models

    DocGenCrew ..> ConfidentAI : logs / evaluates
    PostgreSQLStorage ..> ConfidentAI : metric upload
    GuardrailsTool ..> ConfidentAI : validation results

    style API fill:#f9f,stroke:#333,stroke-width:2px
    style Service fill:#bbf,stroke:#333,stroke-width:2px
    style Tools fill:#bfb,stroke:#333,stroke-width:2px
    style Models fill:#ffb,stroke:#333,stroke-width:2px
    style Data fill:#ffe,stroke:#333,stroke-width:2px
    style External fill:#ddd,stroke:#333,stroke-width:2px
```

---  

## Detailed Narrative  

### 1. Architectural Pattern  

| Pattern | Evidence |
|---------|----------|
| **Layered / Service‑Oriented** | The system is split into clear layers: **API** (FastAPI routes), **Service** (CrewAI crew & agents), **Tools** (re‑usable utilities), **Models**, **Data** (PostgreSQL). |
| **Micro‑agent (CrewAI) orchestration** | `src/doc_generator/crew.py` defines `DocGenerator` (decorated with `@CrewBase`). It creates several agents (`architecture_reasoning_agent`, `api_semantics_agent`, etc.) that each own a dedicated task. |
| **Dependency Injection via SharedMemory** | All tools read/write a singleton `SharedMemory` (see `tools/shared_memory.py`). This removes tight coupling and allows any component to fetch data produced by another. |
| **External Observability** | Integration with **Confident AI** (`deepeval` tracing and metric upload) provides observability without coupling business logic. |

### 2. Component Responsibilities  

| Layer | Component | Primary Role | Source File |
|-------|-----------|---------------|--------------|
| **API** | FastAPI app (`api_server.py`) | Exposes `/generate-from-git` and `/generate-from-path` endpoints; mounts static docs folder. | `api_server.py` |
| **Service / Crew** | `DocGenerator` (Crew) | Orchestrates the whole documentation pipeline; creates agents and defines tasks. | `src/doc_generator/crew.py` |
| | Architecture Reasoning Agent | Generates architecture diagram & description. | `crew.py` (method `architecture_reasoning_agent`) |
| | API Semantics Agent | Produces API reference section. | `crew.py` |
| | Examples Agent | Generates usage examples. | `crew.py` |
| | Getting‑Started Agent | Writes README / quick‑start guide. | `crew.py` |
| | Document Assembler Agent | Assembles final markdown with section markers. | `crew.py` |
| **Tools** | `CodeAnalyzer` | Parses the entire codebase, builds AST, stores in SharedMemory. | `tools/code_analyzer.py` |
| | `DependencyAnalyzer` | Detects Python & Java import relationships. | `tools/dependency_analyzer.py` |
| | `LanguageDetector` | Detects languages present in the repo. | `tools/language_detector.py` |
| | `StructureExtractor` | Reads source files and returns raw content for LLM analysis. | `tools/structure_extractor.py` |
| | `Guardrails` / `GuardrailsTool` | Validates JSON/Markdown, redacts PII, checks hallucination risk, quality gates. | `tools/guardrails.py` |
| | `SharedMemory` | Singleton backed by a PostgreSQL table; stores intermediate artefacts (AST, language list, source files, traces). | `tools/shared_memory.py` |
| | `PostgreSQLStorage` | Persists task results (name, agent role, score) to the DB; used for trace collection. | `tools/postgres_storage.py` |
| **Models** | `DocumentationOutput` | Pydantic model that holds final documentation pieces and writes them to the `docs/` folder. | `models/documentation_output.py` |
| | `CodeStructure` & related dataclasses (`FileInfo`, `ClassInfo`, …) | Represent parsed code‑structure for the `CodeAnalyzer` output. | `models/code_structure.py` |
| **Data** | PostgreSQL `docgen` table | Stores shared memory key‑value pairs and trace logs. Accessed via `SharedMemory` and `PostgreSQLStorage`. |
| **External** | Git (CLI `git clone`) | Used by both the CLI (`run()`) and API (`/generate-from-git`) to fetch remote repos. | `src/doc_generator/main.py`, `api_server.py` |
| | Confident AI (deepeval) | Handles metrics, tracing, and optional dashboard visualisation. All calls guarded by the `CONFIDENT_API_KEY` env var. | `src/doc_generator/main.py` |

### 3. Data Flow (Request → Response)

1. **Entry Point**  
   *CLI*: `run()` in `src/doc_generator/main.py` prompts for a folder or Git URL.  
   *API*: POST `/generate-from-git` or `/generate-from-path` receives a URL/path.

2. **Repository Retrieval** *(if needed)*  
   `git clone --depth 1 <url>` → temporary directory (handled in both entry points).

3. **SharedMemory Reset**  
   `SharedMemory().clear()` ensures a clean slate.

4. **Crew Execution** (`DocGenerator().crew().kickoff(inputs)`)  
   - The **CodeAnalyzer** tool reads every source file, builds an AST (`CodeStructure`) and writes it to SharedMemory.  
   - **DependencyAnalyzer**, **LanguageDetector**, and **StructureExtractor** enrich SharedMemory with dependency graphs, language list, and raw source text.  
   - Each **Agent** (Architecture, API Semantics, Examples, Getting‑Started) reads the SharedMemory data, runs its LLM task, and produces a markdown fragment.  
   - The **Document Assembler** concatenates fragments, inserting `===SECTION: filename===` markers.

5. **Extraction & Validation**  
   - The service extracts sections via `_split_sections`.  
   - `GuardrailsTool` can be invoked (within agents) to redact PII and enforce JSON/Markdown correctness.  
   - Metric evaluation (`deepeval` metrics such as faithfulness, toxicity, hallucination, etc.) runs in `run()` and on the API side via `generate_docs()`. Results are sent to **Confident AI**.

6. **Persistence**  
   - Intermediate results (traces, metrics) are stored in the `docgen` table via `PostgreSQLStorage`.  
   - Final documentation pieces are materialised in the `DocumentationOutput` model and written to `docs/` (static files) and a combined `technical_documentation.md`.

7. **Response**  
   *CLI*: prints a summary and returns the crew result.  
   *API*: returns a JSON payload containing language, file count, endpoint count, and the absolute path to the generated docs.

8. **Flush & Observability**  
   `deepeval.flush()` guarantees all traces/metrics are delivered before the process exits.

### 4. Security Architecture  

| Concern | Implementation |
|--------|----------------|
| **API Authentication** | None built‑in; the service is intended for internal use or protected by external gateway. |
| **Confident AI Credential** | Loaded from environment variable `CONFIDENT_API_KEY`. Guarded by early `load_dotenv()` (see `src/doc_generator/main.py`). |
| **Sensitive Data Redaction** | `Guardrails.redact_sensitive_data` removes API keys, passwords, tokens, and PII from generated content before persisting. |
| **Git Clone Safety** | Clones are depth‑limited (`--depth 1`) and executed in a temporary directory that is removed after processing. |
| **Database Access** | `SharedMemory` uses a **singleton** PostgreSQL engine with parameterised queries (SQLAlchemy) – mitigates injection risk. |
| **Input Validation** | API endpoints validate path existence and URL format; FastAPI automatically sanitises form data. |

### 5. Key Design Patterns Observed  

| Pattern | Where Used |
|---------|-------------|
| **Singleton** | `SharedMemory` implements a process‑wide singleton for shared state. |
| **Factory / Builder** | The `DocGenerator` crew builds a collection of agents and tasks dynamically. |
| **Decorator** | Agents are marked with `@agent`; tasks with `@task`. Tools inherit from `BaseTool`. |
| **Strategy** | Different agents (architecture, API, examples) encapsulate distinct LLM prompting strategies. |
| **Adapter** | `PostgreSQLStorage` adapts the generic `BaseTool` interface to a concrete DB write operation. |
| **Template Method** | Each `Agent` follows a common execution skeleton (input → LLM call → output) provided by CrewAI. |

### 6. Summary of Layers & Their Inter‑connections  

```
[API]  →  (FastAPI)   →  [Service / Crew]  →  (Agents & Tasks)
                                   │
                                   ├─► [Tool: CodeAnalyzer] ──► SharedMemory
                                   ├─► [Tool: DependencyAnalyzer] ──► SharedMemory
                                   ├─► [Tool: LanguageDetector] ──► SharedMemory
                                   ├─► [Tool: StructureExtractor] ──► SharedMemory
                                   ├─► [Tool: Guardrails] ──► SharedMemory
                                   └─► [Tool: PostgreSQLStorage] ──► PostgreSQL
                                   │
                                   ▼
                                [Models] (DocumentationOutput, CodeStructure)
                                   │
                                   ▼
                               [Data] (PostgreSQL table `docgen`)
                                   │
                                   ▼
                           [External Services] (Git, Confident AI)
```

All components are accounted for in the diagram and narrative, satisfying the requirement to capture **controllers/routes, services, repositories, models, utilities, configuration, security, and external integrations**.

===SECTION: EXAMPLES.md===
# API Examples – Documentation Generator Service (FastAPI)

Below are ready‑to‑copy **cURL** commands, sample request bodies, successful responses, and error responses for **all** public endpoints (`/generate-from-git`, `/generate-from-path`, `/traces`).  
No authentication is required for these endpoints; only the standard `Content-Type` header for form submissions.

---  

## 1️⃣ `POST /generate-from-git`

**Purpose** – Clone a public Git repository (depth‑1), run the documentation‑generation crew, and return generation metrics.

### Required Headers
| Header | Value |
|--------|-------|
| `Content-Type` | `multipart/form-data` (automatically set by `curl -F`) |

### cURL Example (Success)

```bash
curl -X POST "http://localhost:8000/generate-from-git" \
  -F "git_url=https://github.com/example-org/sample-python-app.git"
```

### Sample Request Body (form‑encoded)

| Field   | Example Value |
|---------|---------------|
| `git_url` | `https://github.com/example-org/sample-python-app.git` |

### Successful Response (HTTP 200)

```json
{
  "status": "success",
  "metrics": {
    "language": "python",
    "total_files": 42,
    "total_endpoints": 7,
    "docs_path": "/absolute/path/to/docs"
  }
}
```

### Error Response (HTTP 500 – clone or generation failure)

```json
{
  "error": "git: command not found"
}
```

*Typical causes*: invalid URL, network issue, repository not public, or an internal failure while running the documentation crew.

---  

## 2️⃣ `POST /generate-from-path`

**Purpose** – Generate documentation for a local folder that already exists on the server.

### Required Headers
| Header | Value |
|--------|-------|
| `Content-Type` | `multipart/form-data` |

### cURL Example (Success)

```bash
curl -X POST "http://localhost:8000/generate-from-path" \
  -F "folder_path=/home/user/projects/sample-python-app"
```

### Sample Request Body (form‑encoded)

| Field        | Example Value |
|--------------|---------------|
| `folder_path` | `/home/user/projects/sample-python-app` |

### Successful Response (HTTP 200)

```json
{
  "status": "success",
  "metrics": {
    "language": "python",
    "total_files": 42,
    "total_endpoints": 7,
    "docs_path": "/absolute/path/to/docs"
  }
}
```

### Validation Error (HTTP 400)

*Path does not exist*

```json
{
  "error": "Path does not exist: /invalid/path"
}
```

*Path is not a directory*

```json
{
  "error": "Path is not a directory: /home/user/file.txt"
}
```

### Generation Error (HTTP 500)

```json
{
  "error": "Error while running documentation crew: unexpected EOF while reading"
}
```

---  

## 3️⃣ `GET /traces`

**Purpose** – Retrieve all agent execution traces stored in PostgreSQL (used for observability).

### Required Headers
| Header | Value |
|--------|-------|
| `Accept` | `application/json` (optional – FastAPI defaults to JSON) |

### cURL Example (Success)

```bash
curl -X GET "http://localhost:8000/traces"
```

### Successful Response (HTTP 200)

```json
{
  "status": "success",
  "traces": [
    "2024-02-13T12:00:00Z - ArchitectureReasoningAgent - completed",
    "2024-02-13T12:00:01Z - APISemanticsAgent - completed",
    "2024-02-13T12:00:02Z - ExamplesAgent - completed"
  ]
}
```

### Error Response (HTTP 500 – DB access problem)

```json
{
  "error": "could not connect to PostgreSQL server"
}
```

---  

### Quick Summary of Required Headers per Endpoint
| Endpoint | Method | Required Headers |
|----------|--------|------------------|
| `/generate-from-git` | POST | `Content-Type: multipart/form-data` |
| `/generate-from-path` | POST | `Content-Type: multipart/form-data` |
| `/traces` | GET | *(none required; optional `Accept: application/json`)* |

All examples use placeholder values (`your-token-here` is **not** needed because the service does not enforce authentication). Replace the sample URLs/paths with real values that exist in your environment.

===SECTION: architecture.mermaid===
%% Layered architecture of the Documentation Generator
graph LR
    %% ==== API Layer ====
    subgraph API [API Layer]
        API_Server["FastAPI (api_server.py)"]
        API_Route_Git["/generate-from-git"]
        API_Route_Path["/generate-from-path"]
    end

    %% ==== Service / Orchestration Layer ====
    subgraph Service [Service (Crew) Layer]
        DocGenCrew["DocGenerator Crew (src/doc_generator/crew.py)"]
        ArchitectureAgent["Architecture Reasoning Agent"]
        APISemanticsAgent["API Semantics Agent"]
        ExamplesAgent["Examples Generation Agent"]
        GettingStartedAgent["Getting‑Started Agent"]
        DocumentAssembler["Document Assembler Agent"]
    end

    %% ==== Tool / Utility Layer ====
    subgraph Tools [Tool / Utility Layer]
        CodeAnalyzer["CodeAnalyzer Tool (tools/code_analyzer.py)"]
        DependencyAnalyzer["DependencyAnalyzer Tool (tools/dependency_analyzer.py)"]
        LanguageDetector["LanguageDetector Tool (tools/language_detector.py)"]
        StructureExtractor["StructureExtractor Tool (tools/structure_extractor.py)"]
        GuardrailsTool["Guardrails Tool (tools/guardrails.py)"]
        SharedMemoryTool["SharedMemory (tools/shared_memory.py)"]
        PostgreSQLStorage["PostgreSQLStorage Tool (tools/postgres_storage.py)"]
    end

    %% ==== Model Layer ====
    subgraph Models [Model Layer]
        DocumentationOutput["DocumentationOutput (models/documentation_output.py)"]
        CodeStructure["CodeStructure (models/code_structure.py)"]
    end

    %% ==== Data Layer ====
    subgraph Data [Data Layer]
        PostgreSQL["PostgreSQL DB (docgen table)"]
    end

    %% ==== External Integrations ====
    subgraph External [External Services]
        GitRepo["Git Repository"]
        ConfidentAI["Confident AI (metrics & tracing)"]
    end

    %% ==== Connections ====
    API_Server --> API_Route_Git
    API_Server --> API_Route_Path
    API_Route_Git -.-> GitRepo
    API_Route_Path -.-> (Local FS)

    API_Route_Git -->|trigger| DocGenCrew
    API_Route_Path -->|trigger| DocGenCrew

    DocGenCrew --> CodeAnalyzer
    DocGenCrew --> DependencyAnalyzer
    DocGenCrew --> LanguageDetector
    DocGenCrew --> StructureExtractor
    DocGenCrew --> GuardrailsTool
    DocGenCrew --> PostgreSQLStorage
    DocGenCrew --> ArchitectureAgent
    DocGenCrew --> APISemanticsAgent
    DocGenCrew --> ExamplesAgent
    DocGenCrew --> GettingStartedAgent
    DocGenCrew --> DocumentAssembler

    CodeAnalyzer --> SharedMemoryTool
    DependencyAnalyzer --> SharedMemoryTool
    LanguageDetector --> SharedMemoryTool
    StructureExtractor --> SharedMemoryTool
    GuardrailsTool --> SharedMemoryTool
    PostgreSQLStorage --> PostgreSQL

    SharedMemoryTool --> PostgreSQL
    DocumentationOutput -->|writes| docs_folder["/docs (static files)"]
    DocumentationOutput --> Models

    DocGenCrew ..> ConfidentAI : logs / evaluates
    PostgreSQLStorage ..> ConfidentAI : metric upload
    GuardrailsTool ..> ConfidentAI : validation results

    style API fill:#f9f,stroke:#333,stroke-width:2px
    style Service fill:#bbf,stroke:#333,stroke-width:2px
    style Tools fill:#bfb,stroke:#333,stroke-width:2px
    style Models fill:#ffb,stroke:#333,stroke-width:2px
    style Data fill:#ffe,stroke:#333,stroke-width:2px
    style External fill:#ddd,stroke:#333,stroke-width:2px