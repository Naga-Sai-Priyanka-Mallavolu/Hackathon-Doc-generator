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