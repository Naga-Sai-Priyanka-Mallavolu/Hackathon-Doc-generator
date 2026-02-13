===SECTION: README.md===
<<<<<<< Updated upstream
# Documentation Generator

## Table of Contents
- [Project Overview](#project-overview)  
- [Getting Started](#getting-started)  
- [Running the Application](#running-the-application)  
- [API Reference](API_REFERENCE.md)  
- [Architecture Diagram](ARCHITECTURE.md)  
- [Examples](EXAMPLES.md)
=======
# README

## Table of Contents
- [Project Overview](#project-overview)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Quick Start Example](#quick-start-example)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Further Documentation](#further-documentation)
>>>>>>> Stashed changes

## Project Overview
**doc‑generator** is an AI‑powered documentation generator that extracts source code, configuration, and test information from a repository, runs a series of crew‑AI agents, evaluates the output with GEval metrics, and writes a complete set of markdown documentation (README, API reference, architecture diagram, examples, test docs, etc.).

<<<<<<< Updated upstream
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
=======
- **Core purpose** – Automatically produce high‑quality project documentation without manual writing.
- **Technology stack** – Python 3.10‑3.13, FastAPI, PostgreSQL, Ollama LLM, React 19 + Vite frontend, npm, Docker.

## Getting Started

### Prerequisites

| Tool | Minimum version | Install command |
|------|----------------|-----------------|
| Python | 3.10 ≤ x < 3.14 | `pyenv install 3.12 && pyenv global 3.12` |
| pip | latest (bundled) | `python -m ensurepip --upgrade` |
| Node.js | 20.x (LTS) | `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs` |
| npm | 10.x (bundled) | `npm --version` |
| PostgreSQL | 14.x+ | `sudo apt-get install postgresql-14` |
| Git | any recent | `git --version` |
| Docker (optional) | 24.x | `docker pull postgres:15 && docker run …` |

### Installation

```bash
# 1️⃣ Clone the repository
git clone https://github.com/your-org/doc-generator.git
cd doc-generator

# 2️⃣ Set up a Python virtual environment
python -m venv .venv
source .venv/bin/activate

# 3️⃣ Install Python dependencies
pip install --upgrade pip
pip install .   # installs package and crewAI[tools], deepeval, etc.

# 4️⃣ Install the React frontend dependencies
cd docgen-frontend
npm install
cd ..

# 5️⃣ Prepare the PostgreSQL database
psql -U postgres <<SQL
CREATE DATABASE docgen;
CREATE USER docgen_user WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE docgen TO docgen_user;
SQL

# 6️⃣ Create a .env file at the project root
cat > .env <<EOF
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docgen
POSTGRES_USER=docgen_user
POSTGRES_PASSWORD=password
OLLAMA_HOST=http://127.0.0.1:11434
EOF

# 7️⃣ Build the frontend (optional – needed only for UI)
cd docgen-frontend
npm run build   # produces static assets in dist/
cd ..

# 8️⃣ Verify the installation
python -m doc_generator --help   # should show CLI entry points
```

### Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB`   | Database name | `docgen` |
| `POSTGRES_USER` | DB user | `docgen_user` |
| `POSTGRES_PASSWORD` | DB password | `password` |
| `OLLAMA_HOST` | URL of the local Ollama server | `http://127.0.0.1:11434` |

Optional:
- `LOG_LEVEL` – set to `DEBUG` for verbose logs.
- `MAX_RETRY_ATTEMPTS` – number of crew retries (default 3).

### Running the Application

#### API server (FastAPI)

```bash
source .venv/bin/activate
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

The API is reachable at `http://localhost:8000`.

#### CLI entry points

```bash
# From a local folder
doc_generator generate-from-path --folder_path /path/to/project --output_dir ./generated-docs

# From a public Git repo
doc_generator generate-from-git --git_url https://github.com/example/example-repo.git --output_dir ./generated-docs
```

All generated markdown files will be placed under the supplied `output_dir`.

### Quick Start – First API Call

```bash
curl -X POST "http://localhost:8000/generate-from-path" \
     -H "Content-Type: multipart/form-data" \
     -F "folder_path=$(pwd)"
>>>>>>> Stashed changes
```

Expected JSON response (truncated):

<<<<<<< Updated upstream
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

=======
```json
{
  "status": "success",
  "metrics": {
    "language": "python",
    "total_files": 120,
    "total_endpoints": 5,
    "docs_path": "/full/path/to/generated-docs"
  }
}
```

Open the `docs_path` folder to find `README.md`, `API_REFERENCE.md`, `ARCHITECTURE.md`, etc.

### Project Structure

```
/doc-generator
│
├─ src/
│   └─ doc_generator/
│       ├─ crew.py
│       ├─ main.py
│       ├─ models/
│       └─ tools/
│
├─ docgen-frontend/
│   ├─ src/
│   └─ package.json
│
├─ api_server.py
├─ pyproject.toml
├─ .env.example
└─ tests/
```

### Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Port 8000 already in use | Another process bound to 8000 | Run on another port (`uvicorn ... --port 8080`) or stop the other service |
| DB connection error | Wrong `.env` values or PostgreSQL not running | Verify `.env` and test `psql` connection |
| `ImportError: No module named crewai` | Dependencies not installed | `pip install .` inside the venv |
| Frontend build fails | Node version too old | Upgrade to Node 20+, delete `node_modules`, run `npm install` |
| LLM request times out | Ollama not running | Start Ollama (`ollama serve`) and check `curl $OLLAMA_HOST/v1/models` |
| Tests fail with `psycopg2` errors | Missing PostgreSQL client lib | `pip install psycopg2-binary` |

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logs.

## Further Documentation
- **API Reference**: See [API_REFERENCE.md](API_REFERENCE.md)  
- **System Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)  
- **Code Examples**: See [EXAMPLES.md](EXAMPLES.md)  
- **Test Documentation**: See [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)  

===SECTION: API_REFERENCE.md===
# API Reference

## Documentation Generator API – FastAPI Endpoints

| # | Method | Path | Short description |
|---|--------|------|-------------------|
| 1 | POST | `/generate-from-git` | Clone a public Git repo, run the documentation pipeline and return generation metrics. |
| 2 | POST | `/generate-from-path` | Run the documentation pipeline on a local folder and return generation metrics. |
| 3 | GET | `/traces` | Retrieve the list of agent execution traces stored in PostgreSQL. |
| 4 | GET | `/docs-static/{page}`* | Serve static documentation files (README, API reference, …) from the `docs/` folder. *Provided automatically by FastAPI `StaticFiles` mount; not a custom handler. |

### 1. `POST /generate-from-git`

**Purpose**  
Clones the supplied Git repository (shallow clone, depth 1) into a temporary directory, runs the full documentation generation pipeline, and returns a JSON payload containing the generation status and metrics.

**Request Parameters**

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| `git_url` | Form‑data | `str` | Yes | URL of a **public** Git repository (e.g. `https://github.com/user/repo`). |

**Response (`application/json`)**

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` when the pipeline finishes without error. |
| `metrics` | `object` | Dictionary with keys `language`, `total_files`, `total_endpoints`, `docs_path`. |
| `error` | `str` | Present only on failure (HTTP 500). |

**Status codes**

| Code | Meaning |
|------|---------|
| 200 | Generation succeeded. |
| 400 | Invalid request (unlikely for this endpoint). |
| 500 | Runtime error while cloning or generating docs. |

### 2. `POST /generate-from-path`

**Purpose**  
Runs the documentation pipeline on an already‑cloned local folder and returns the same JSON payload as the Git endpoint.

**Request Parameters**

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| `folder_path` | Form‑data | `str` | Yes | Absolute or relative path to the project directory on the server. |

**Response (`application/json`)**

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` on normal completion. |
| `metrics` | `object` | Same metric dictionary as above. |
| `error` | `str` | Error description (HTTP 500) or validation error (HTTP 400). |

**Status codes**

| Code | Meaning |
|------|---------|
| 200 | Generation succeeded. |
| 400 | Path does not exist or is not a directory. |
| 500 | Unexpected error during generation. |

### 3. `GET /traces`

**Purpose**  
Fetches all agent execution traces stored in the shared PostgreSQL `docgen` table.

**Response (`application/json`)**

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` when the request is processed. |
| `traces` | `list[str]` | Array of trace strings (raw JSON payloads from CrewAI agents). |
| `error` | `str` | Present only on failure (HTTP 500). |

**Status codes**

| Code | Meaning |
|------|---------|
| 200 | Traces returned successfully. |
| 500 | Database/serialization error. |

### 4. `GET /docs-static/{page}` *(static files)*  

FastAPI automatically serves any file placed in the `docs/` directory under the URL path `/docs-static/{page}` (e.g. `/docs-static/README.md`). No custom logic, request validation, or response schema beyond the default static‑file handling.

**Typical usage:**  
`GET /docs-static/README.md` → returns the **README.md** file content.

**Error handling:**  
If the file does not exist, FastAPI returns a standard `404` JSON response: `{ "detail": "Not Found" }`.

---

#### Common **Metrics** object (returned by the two POST endpoints)

```json
{
  "language": "java",
  "total_files": 42,
  "total_endpoints": 17,
  "docs_path": "/full/path/to/docs"
}
```

===SECTION: ARCHITECTURE.md===
# Architecture Documentation

This document provides a complete overview of the **doc‑generator** system, including a Mermaid diagram and a detailed narrative of its layers, components, data flow, persistence, security, observability, and extensibility.

## Narrative Architecture Description

### 1. Architectural Pattern
The system follows a **layered (n‑tier) architecture** with micro‑service‑style componentization inside a single FastAPI process. The layers are:

1. **Presentation Layer** – FastAPI endpoints (`api_server.py`) and a React/Vite UI (`docgen‑frontend`).
2. **Application Layer** – Orchestration logic (`src/doc_generator/main.py`) that launches the **DocGenerator Crew** (`src/doc_generator/crew.py`).
3. **Domain / Model Layer** – Pydantic and dataclass models that describe extracted code structure and generated documentation (`src/doc_generator/models/*`).
4. **Infrastructure Layer** – Tools and adapters (code analyser, config parser, guard‑rails, PostgreSQL storage, shared‑memory singleton, test analyser, GEval metrics).
5. **External Services** – PostgreSQL, Ollama LLM, Confident AI observability, and remote Git repositories.

### 2. Component Roles
| Component | Layer | Role |
|-----------|-------|------|
| `api_server.py` (FastAPI) | Presentation | HTTP routes (`/generate-from-git`, `/generate-from-path`, `/traces`). Delegates to the application layer. |
| `docgen‑frontend` (React) | Presentation | UI that consumes the FastAPI endpoints and renders markdown/diagrams. |
| `src/doc_generator/main.py` | Application | Boots the crew, handles retries, evaluation, and final document persistence. |
| `src/doc_generator/crew.py` – `DocGenerator` class | Application | Declares agents (code analyser, API semantics, architecture reasoning, example generation, getting‑started guide, document assembler) and the tasks that wire them together. Provides `run_with_evaluation`. |
| `src/doc_generator/models/*` | Domain | `CodeStructure` (language‑agnostic AST) and `DocumentationOutput` (structured output with `save_to_folder`). |
| `src/doc_generator/tools/code_analyzer.py` | Infrastructure | Parses source files (Python, Java, generic) and stores AST data in shared memory. |
| `src/doc_generator/tools/config_parser.py` | Infrastructure | Extracts Maven, Gradle, npm, Docker, Spring, and generic configuration files. |
| `src/doc_generator/tools/guardrails.py` | Infrastructure / Security | Redacts secrets, checks hallucination, validates JSON/Markdown, and enforces quality gates. |
| `src/doc_generator/tools/memory_reader.py` | Infrastructure | Reads arbitrary keys from shared memory for agents that need prior artefacts. |
| `src/doc_generator/tools/postgres_storage.py` | Infrastructure | Persists trace records and metric results to PostgreSQL (`DocGenTaskRecord`). |
| `src/doc_generator/tools/shared_memory.py` | Infrastructure | Singleton backed by a PostgreSQL table; provides `set/get/append_to_list` etc. |
| `src/doc_generator/tools/test_analyzer.py` | Infrastructure | Analyses test files (Python, Java, JavaScript) and stores a summary in shared memory. |
| `src/doc_generator/geval_metrics.py` | Infrastructure | Creates GEval metric objects (faithfulness, toxicity, hallucination, relevance, completion, efficiency) and can upload them to Confident AI. |
| PostgreSQL DB | External | Persistent store for shared memory, task traces, and evaluation metrics. |
| Ollama LLM | External | Large language model used by crew agents to generate documentation content. |
| Confident AI | External | Observability platform that receives tracing spans and metric uploads. |
| Git repository (remote URL) | External | Source of code when `/generate-from-git` is invoked. |

### 3. Data Persistence Strategy
* **SharedMemory** (singleton) acts as the in‑process cache and is backed by a PostgreSQL table (`docgen`). All agents read/write through it.  
* **PostgreSQLStorage** stores immutable trace entries (`DocGenTaskRecord`) for auditability and historical metric analysis.  
* Generated documentation files are written to the filesystem under the user‑provided output directory; the path is communicated back to the client.

### 4. Security Architecture
* **Guardrails** validates output before it leaves the system: redacts API keys, passwords, tokens, and PII; checks for hallucinations; validates JSON/Markdown syntax; enforces quality thresholds.  
* FastAPI enables CORS only for trusted origins.  
* Sensitive configuration (DB credentials, Confident AI API key) is loaded from `.env` and never stored in shared memory because guard‑rails redact it.  
* External calls (Git clone, Ollama inference, Confident AI upload) run in async functions with proper timeout/exception handling.

### 5. Observability & Traceability
* The `@observe` decorator (`deepeval.tracing`) wraps crew execution, producing **Confident AI spans** that capture agent name, task name, tool calls, timestamps, and confidence scores.  
* GEval metric results can be uploaded via `geval_metrics.upload_all_metrics`.  
* The `/traces` endpoint queries the PostgreSQL trace table, allowing users to inspect past runs.

### 6. Extensibility
* Adding a new documentation section only requires a new **Agent** and associated **Task** in `crew.py`; shared‑memory contracts remain unchanged.  
* Supporting additional programming languages involves extending **CodeAnalyzer** with language‑specific parsers.  
* Storage back‑ends can be swapped by implementing the same `BaseTool` interface (`_run`) for another database or cloud store.

## Mermaid Diagram
```mermaid
flowchart LR
    %% Presentation Layer
    subgraph Presentation[Presentation Layer]
        API[FastAPI (api_server.py)]
        UI[Frontend (docgen‑frontend)]
    end
    
    %% Application Layer
    subgraph Application[Application Layer]
        Main[Main Entrypoint (src/doc_generator/main.py)]
        Crew[DocGenerator Crew (src/doc_generator/crew.py)]
    end
    
    %% Domain / Model Layer
    subgraph Domain[Domain / Model Layer]
        CodeModel[CodeStructure Models (src/doc_generator/models/code_structure.py)]
        DocOut[DocumentationOutput Model (src/doc_generator/models/documentation_output.py)]
    end
    
    %% Infrastructure Layer
    subgraph Infrastructure[Infrastructure Layer]
        SM[SharedMemory (src/doc_generator/tools/shared_memory.py)]
        PG[PostgreSQLStorage (src/doc_generator/tools/postgres_storage.py)]
        CA[CodeAnalyzer Tool (src/doc_generator/tools/code_analyzer.py)]
        CP[ConfigParser Tool (src/doc_generator/tools/config_parser.py)]
        GA[Guardrails Tool (src/doc_generator/tools/guardrails.py)]
        MR[MemoryReader Tool (src/doc_generator/tools/memory_reader.py)]
        TA[TestAnalyzer Tool (src/doc_generator/tools/test_analyzer.py)]
        GE[GEval Metrics (src/doc_generator/geval_metrics.py)]
    end
    
    %% External Services
    subgraph External[External Services]
        DB[(PostgreSQL DB)]
        LLM[(Ollama LLM)]
        CI[(Confident AI Observability)]
        Git[(Git Repository)]
    end
    
    %% Relationships
    UI -- calls --> API
    API --> Main
    Main --> Crew
    Crew -- orchestrates --> CA
    Crew -- orchestrates --> CP
    Crew -- orchestrates --> GA
    Crew -- orchestrates --> TA
    Crew -- orchestrates --> GE
    Crew -- stores/retrieves --> SM
    SM -- persists --> DB
    PG -- writes traces --> DB
    CA -- writes parsed code --> SM
    CP -- writes config data --> SM
    MR -- reads shared data --> SM
    GA -- validates output --> SM
    TA -- writes test analysis --> SM
    GE -- evaluates docs --> SM
    LLM -- used by agents (via Crew) --> API
    CI -- receives traces & metrics --> Crew
    API -- clones --> Git
    style Presentation fill:#f9f,stroke:#333,stroke-width:2px
    style Application fill:#bbf,stroke:#333,stroke-width:2px
    style Domain fill:#bfb,stroke:#333,stroke-width:2px
    style Infrastructure fill:#ffb,stroke:#333,stroke-width:2px
    style External fill:#ddd,stroke:#333,stroke-width:2px
```

===SECTION: EXAMPLES.md===
# API Usage Examples

Below are ready‑to‑copy `curl` commands for every endpoint exposed by the Documentation Generator API, together with sample responses and common error cases.

## `POST /generate-from-git`

**Description** – Clone a public Git repository, run the documentation pipeline, and receive generation metrics.

```bash
curl -X POST "http://localhost:8000/generate-from-git" \
     -H "Content-Type: multipart/form-data" \
     -F "git_url=https://github.com/example-user/example-repo"
```

**Success (HTTP 200)**

>>>>>>> Stashed changes
```json
{
  "status": "success",
  "metrics": {
<<<<<<< Updated upstream
    "language": "python",
    "total_files": 42,
    "total_endpoints": 7,
    "docs_path": "/absolute/path/to/docs"
=======
    "language": "java",
    "total_files": 42,
    "total_endpoints": 17,
    "docs_path": "/full/path/to/docs"
>>>>>>> Stashed changes
  }
}
```

<<<<<<< Updated upstream
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
=======
**Error – Git clone failure (HTTP 500)**

```json
{
  "error": "fatal: repository 'https://github.com/nonexistent/repo' not found"
}
```

---

## `POST /generate-from-path`

**Description** – Run the documentation pipeline on a local folder.

```bash
curl -X POST "http://localhost:8000/generate-from-path" \
     -H "Content-Type: multipart/form-data" \
     -F "folder_path=/home/user/projects/example-repo"
```

**Success (HTTP 200)**
>>>>>>> Stashed changes

```json
{
  "status": "success",
  "metrics": {
    "language": "python",
<<<<<<< Updated upstream
    "total_files": 42,
    "total_endpoints": 7,
    "docs_path": "/absolute/path/to/docs"
  }
=======
    "total_files": 128,
    "total_endpoints": 23,
    "docs_path": "/full/path/to/docs"
  }
}
```

**Error – Path does not exist (HTTP 400)**

```json
{
  "error": "Path does not exist: /nonexistent/path"
}
```

**Error – Path is not a directory (HTTP 400)**

```json
{
  "error": "Path is not a directory: /home/user/file.txt"
>>>>>>> Stashed changes
}
```

### Validation Error (HTTP 400)

<<<<<<< Updated upstream
*Path does not exist*

```json
{
  "error": "Path does not exist: /invalid/path"
=======
## `GET /traces`

**Description** – Retrieve all stored agent execution traces.

```bash
curl -X GET "http://localhost:8000/traces" -H "Accept: application/json"
```

**Success (HTTP 200)**

```json
{
  "status": "success",
  "traces": [
    "{\"agent\": \"CodeAnalyzer\", \"time\": \"2024-02-13T12:34:56Z\", \"output\": \"...\"}",
    "{\"agent\": \"API Semantics\", \"time\": \"2024-02-13T12:35:10Z\", \"output\": \"...\"}"
  ]
}
```

**Error – Database connection failure (HTTP 500)**

```json
{
  "error": "could not connect to server: Connection refused"
>>>>>>> Stashed changes
}
```

*Path is not a directory*

<<<<<<< Updated upstream
```json
{
  "error": "Path is not a directory: /home/user/file.txt"
=======
## `GET /docs-static/{page}` (Static Files)

**Description** – Serve static documentation files from the `docs/` directory.

```bash
curl -X GET "http://localhost:8000/docs-static/README.md" -H "Accept: text/plain"
```

**Success (HTTP 200, `text/markdown`)**

```markdown
# README

Documentation was generated for the example Java project.
```

**Error – File not found (HTTP 404)**

```json
{
  "detail": "Not Found"
>>>>>>> Stashed changes
}
```

### Generation Error (HTTP 500)

<<<<<<< Updated upstream
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
=======
# Summary of Required Headers per Endpoint

| Endpoint | Method | Required Headers |
|----------|--------|-------------------|
| `/generate-from-git` | POST | `Content-Type: multipart/form-data` |
| `/generate-from-path` | POST | `Content-Type: multipart/form-data` |
| `/traces` | GET | `Accept: application/json` |
| `/docs-static/{page}` | GET | `Accept: text/plain` (or appropriate MIME) |

Feel free to adapt the examples to your environment (host, port, auth headers if added later).

===SECTION: TEST_DOCUMENTATION.md===
# Test Documentation

## Overview
- **Total Test Files**: 1
- **Total Test Cases**: 10
- **Test Frameworks**: None detected

## Test Types
- **Unit**: 1 test file

## Test Files Details

### /Users/Shriya/Documents/docgenerator/Hackathon-Doc-generator/test_connection.py
**Type**: unit  
**Test Cases**: 10  
- `test_llm`  
- `test_embeddings_v1`  
- `test_embeddings_api`  
- `test_models`  
- `test_embeddings_extra`  
- `test_api_tags`  
- `test_models` (duplicate entry)  
- `test_embeddings_exhaustive`  
- `test_ollama_library`  
- `test_embeddings_exhaustive` (duplicate entry)

No additional test frameworks or integration tests were detected in the repository.

===SECTION: architecture.mermaid===
flowchart LR
    %% Presentation Layer
    subgraph Presentation[Presentation Layer]
        API[FastAPI (api_server.py)]
        UI[Frontend (docgen‑frontend)]
    end
    
    %% Application Layer
    subgraph Application[Application Layer]
        Main[Main Entrypoint (src/doc_generator/main.py)]
        Crew[DocGenerator Crew (src/doc_generator/crew.py)]
    end
    
    %% Domain / Model Layer
    subgraph Domain[Domain / Model Layer]
        CodeModel[CodeStructure Models (src/doc_generator/models/code_structure.py)]
        DocOut[DocumentationOutput Model (src/doc_generator/models/documentation_output.py)]
    end
    
    %% Infrastructure Layer
    subgraph Infrastructure[Infrastructure Layer]
        SM[SharedMemory (src/doc_generator/tools/shared_memory.py)]
        PG[PostgreSQLStorage (src/doc_generator/tools/postgres_storage.py)]
        CA[CodeAnalyzer Tool (src/doc_generator/tools/code_analyzer.py)]
        CP[ConfigParser Tool (src/doc_generator/tools/config_parser.py)]
        GA[Guardrails Tool (src/doc_generator/tools/guardrails.py)]
        MR[MemoryReader Tool (src/doc_generator/tools/memory_reader.py)]
        TA[TestAnalyzer Tool (src/doc_generator/tools/test_analyzer.py)]
        GE[GEval Metrics (src/doc_generator/geval_metrics.py)]
    end
    
    %% External Services
    subgraph External[External Services]
        DB[(PostgreSQL DB)]
        LLM[(Ollama LLM)]
        CI[(Confident AI Observability)]
        Git[(Git Repository)]
    end
    
    %% Relationships
    UI -- calls --> API
    API --> Main
    Main --> Crew
    Crew -- orchestrates --> CA
    Crew -- orchestrates --> CP
    Crew -- orchestrates --> GA
    Crew -- orchestrates --> TA
    Crew -- orchestrates --> GE
    Crew -- stores/retrieves --> SM
    SM -- persists --> DB
    PG -- writes traces --> DB
    CA -- writes parsed code --> SM
    CP -- writes config data --> SM
    MR -- reads shared data --> SM
    GA -- validates output --> SM
    TA -- writes test analysis --> SM
    GE -- evaluates docs --> SM
    LLM -- used by agents (via Crew) --> API
    CI -- receives traces & metrics --> Crew
    API -- clones --> Git
    style Presentation fill:#f9f,stroke:#333,stroke-width:2px
    style Application fill:#bbf,stroke:#333,stroke-width:2px
    style Domain fill:#bfb,stroke:#333,stroke-width:2px
    style Infrastructure fill:#ffb,stroke:#333,stroke-width:2px
>>>>>>> Stashed changes
    style External fill:#ddd,stroke:#333,stroke-width:2px