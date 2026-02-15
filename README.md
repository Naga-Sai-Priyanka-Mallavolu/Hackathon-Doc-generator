# Multi-Agent Documentation Generation System

> **Treat documentation as a living system, not a static artifact.**
> Agents continuously *observe code*, *reason about intent*, *validate accuracy*, and *publish trusted documentation*.

This is not "generate README once" — this is **documentation intelligence**.

## 🧠 Architecture Overview

This system implements a **multi-agent architecture** with specialized agents working in layers:

```
Code → Structure → Meaning → Knowledge → Documentation → Evaluation
```

### Layer 1: Ingestion & Structural Understanding
- **Structural Scanner Agent**: Extracts deterministic structural information (files, modules, classes, functions)
- **Dependency Analyzer Agent**: Maps relationships and dependencies between components

### Layer 2: Semantic Understanding
- **API Semantics Agent**: Infers purpose and meaning from code structure
- **Architecture Agent**: Identifies patterns and architectural roles

### Layer 3: Documentation Assembly
- **API Doc Agent**: Generates comprehensive API reference
- **Architecture Doc Agent**: Creates architecture overview
- **Example Generator Agent**: Produces usage examples
- **Getting Started Agent**: Creates onboarding guides

### Layer 4: Evaluation & Quality
- **Evaluation Agent**: Measures coverage, accuracy, and consistency

## 🚀 Quick Start

### Installation

Ensure you have Python >=3.10 <3.14 installed. This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install uv if you haven't already
pip install uv

# Install dependencies
crewai install
```

### Configuration

Add your `OPENAI_API_KEY` to a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

### Usage

Run the documentation generator on a codebase:

```bash
# Process current directory
crewai run

# Process a specific folder
python -m doc_generator.main /path/to/your/codebase

# Or use the script directly
doc_generator /path/to/your/codebase
```

The system will:
1. Analyze the codebase structure
2. Detect programming languages
3. Extract dependencies and relationships
4. Generate comprehensive documentation
5. Evaluate quality and coverage

Output will be saved to `technical_documentation.json` in the project root in a structured JSON format.

## 🧩 Features

### Deterministic Extraction First
- AST-based parsing for accurate structure extraction
- No hallucination - only documents what exists
- Evidence-backed generation

### Multi-Language Support
Currently supports:
- Python (full AST parsing)
- JavaScript/TypeScript (detection)
- Java, Go, Rust (detection)
- And more via extension

### Quality Guarantees
- **Coverage metrics**: % of code documented
- **Accuracy checks**: Verify against actual code
- **Consistency validation**: Same API described once
- **Confidence scoring**: Flag uncertain inferences

### Enterprise-Safe
- Redaction of secrets and tokens
- Schema enforcement
- Honest uncertainty handling
- "Prefers incomplete over wrong"

## 📁 Project Structure

```
doc_generator/
├── src/
│   └── doc_generator/
│       ├── models/              # Data models for code structure
│       │   └── code_structure.py
│       ├── tools/               # Specialized tools
│       │   ├── language_detector.py
│       │   ├── structure_extractor.py
│       │   └── dependency_analyzer.py
│       ├── config/              # Agent and task configurations
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── crew.py              # Multi-agent crew orchestration
│       └── main.py             # Entry point
├── knowledge/                   # Knowledge base for agents
└── pyproject.toml
```

## 🛠️ Customization

### Modify Agents
Edit `src/doc_generator/config/agents.yaml` to customize agent roles, goals, and backstories.

### Modify Tasks
Edit `src/doc_generator/config/tasks.yaml` to adjust task descriptions and expected outputs.

### Add Tools
Create new tools in `src/doc_generator/tools/` following the BaseTool pattern, then add them to agents in `crew.py`.

## 🧪 Advanced Usage

### Training
```bash
python -m doc_generator.main train <n_iterations> <filename> [folder_path]
```

### Testing
```bash
python -m doc_generator.main test <n_iterations> <eval_llm> [folder_path]
```

### Replay
```bash
python -m doc_generator.main replay <task_id>
```

## 🎯 Design Philosophy

### Evidence-First Reasoning
Every claim in documentation is backed by actual code structure. The system:
- Extracts facts deterministically
- Infers meaning with confidence scores
- Flags uncertainty rather than guessing
- Prefers being incomplete over being wrong

### Multi-Agent Collaboration
Specialized agents work together:
- Each agent has a focused responsibility
- Context flows between agents
- Tasks build on previous results
- Evaluation ensures quality

### Continuous Evolution
Documentation is treated as a living system:
- Can be regenerated as code changes
- Maintains consistency across versions
- Tracks quality metrics over time

## 📊 Output Structure

The generated `technical_documentation.json` includes a structured JSON document with:

1. **documentation** section:
   - `table_of_contents`: Markdown table of contents
   - `architecture_overview`: System summary, components, design patterns, data flow
   - `api_reference`: Complete API documentation organized by module
   - `examples`: Practical, runnable code examples with difficulty levels
   - `getting_started`: Prerequisites, installation, quick start, next steps

2. **metadata** section:
   - File and function/class counts
   - Quality assurance issues found
   - Generation timestamp

The output follows a standardized JSON schema for easy parsing and integration.

## 🔒 Safety & Trust

- **Guardrails**: Don't invent APIs, only document what exists
- **Redaction**: Removes secrets, tokens, internal URLs
- **Hallucination Controls**: Evidence-required generation
- **Schema Enforcement**: Output matches expected structure

## 🤝 Contributing

This is a hackathon project demonstrating real agentic thinking. The architecture is designed to be:
- Framework-agnostic (can use CrewAI, LangGraph, LangChain, etc.)
- Extensible (easy to add new languages, tools, agents)
- Production-ready (includes evaluation, safety, quality checks)

## create .env with following props

- API_BASE= https://ollama.com/v1
- MODEL_NAME= gpt-oss:120b-cloud
- OPENAI_API_KEY=""
- CREWAI_TRACING_ENABLED=false
 
- CONFIDENT_API_KEY=
- CONFIDENT_TRACE_VERBOSE=0
- CONFIDENT_METRIC_LOGGING_FLUSH=1
- DEEPEVAL_TEST_MODE=false
 
# Ollama config for DeepEval GEval metrics currently using local model to eval we can switch it to cloud
- OLLAMA_EVAL_MODEL=deepseek-r1:1.5b
- OLLAMA_BASE_URL=http://localhost:11434
- DEEPEVAL_METRIC_COLLECTION=my-evals
 
# Increase timeout for Ollama eval calls (seconds per attempt)
- DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE=300
 
# Eval quality gate: min score to accept docs, max retries if below
MIN_EVAL_SCORE=6.0
MAX_RETRY_ATTEMPTS=2
