# Documentation Generator – Output Structure

## Overview

The documentation generator now produces a **structured, organized output** using a Pydantic-based `DocumentationOutput` model. This ensures consistent output across multiple runs and analyses.

---

## Output Folder Structure

```
docs/
├── README.md                    # Getting Started Guide
├── API_REFERENCE.md             # Complete API Endpoint Documentation
├── ARCHITECTURE.md              # System Architecture & Design
├── EXAMPLES.md                  # Practical Code Examples
└── diagrams/
    └── architecture.mermaid     # Architecture Diagram (Mermaid format)
```

### File Descriptions

| File | Purpose | Content |
|------|---------|---------|
| **README.md** | Getting Started Guide | Prerequisites, installation, configuration, running the app, quick start, project structure, troubleshooting |
| **API_REFERENCE.md** | API Documentation | Summary table of all endpoints, detailed endpoint specs (method, path, auth, params, responses) |
| **ARCHITECTURE.md** | System Design | Architecture diagram, layer analysis, component roles, data flow, design patterns, security architecture |
| **EXAMPLES.md** | Code Examples | Practical curl, Python, JavaScript examples for all API endpoints with request/response samples |
| **diagrams/architecture.mermaid** | Visual Diagram | Mermaid graph showing all components, layers, and relationships |

---

## Pydantic DocumentationOutput Model

### Location
`src/doc_generator/models/documentation_output.py`

### Fields

```python
class DocumentationOutput(BaseModel):
    # Metadata
    generated_at: datetime              # Timestamp of generation
    codebase_path: str                  # Path to analyzed codebase
    language: str                       # Primary language detected (java, python, etc.)
    
    # Core documentation sections
    readme: str                         # README.md content
    api_reference: str                  # API_REFERENCE.md content
    architecture: str                   # ARCHITECTURE.md content
    examples: str                       # EXAMPLES.md content
    architecture_diagram: str           # Mermaid diagram content
    
    # Optional metadata
    summary: Optional[str]              # Brief codebase summary
    total_files: Optional[int]          # Total files analyzed
    total_endpoints: Optional[int]      # Total API endpoints documented
```

### Key Method: `save_to_folder(output_dir: str)`

Automatically creates the folder structure and saves all documentation:

```python
doc_output = DocumentationOutput(...)
doc_output.save_to_folder("docs")  # Creates docs/ with all files
```

---

## Generation Pipeline

### 1. Code Analysis Phase
- **Code Analyzer Agent** parses codebase and stores data in shared memory
- Detects language, counts files, identifies classes/functions/endpoints

### 2. Documentation Generation Phase
- **API Semantics Agent** → generates `API_REFERENCE.md`
- **Architecture Agent** → generates `ARCHITECTURE.md` + Mermaid diagram
- **Examples Agent** → generates `EXAMPLES.md`
- **Getting Started Agent** → generates `README.md`

### 3. Assembly & Output Phase
- **Document Assembler** combines all outputs with section markers
- `main.py` parses sections and creates `DocumentationOutput` instance
- `save_to_folder()` writes organized folder structure

---

## Usage Example

```bash
# Run the documentation generator
uvx crewai run

# Output:
# ✅ Documentation saved to /path/to/docs
#    - README.md
#    - API_REFERENCE.md
#    - ARCHITECTURE.md
#    - EXAMPLES.md
#    - diagrams/architecture.mermaid
```

---

## Consistency Across Runs

The Pydantic model ensures:

1. **Same structure every time** — All runs produce identical folder layout
2. **Type validation** — All fields are validated before saving
3. **Metadata tracking** — Generation timestamp, language, file counts are captured
4. **Extensibility** — Easy to add new fields or sections without breaking existing code

---

## Integration with CrewAI

The pipeline integrates with CrewAI as follows:

1. **Crew runs** and generates raw output with `===SECTION: filename===` markers
2. **main.py** extracts final output and splits by section markers
3. **DocumentationOutput** is instantiated with parsed sections
4. **save_to_folder()** writes all files to organized structure

---

## Benefits

✅ **Organized** — Clear folder structure with separate files for each topic  
✅ **Consistent** — Pydantic model ensures same output format across runs  
✅ **Extensible** — Easy to add new sections or metadata fields  
✅ **Reusable** — Model can be serialized to JSON for storage/analysis  
✅ **Maintainable** — Single source of truth for output structure  

---

## Example Output (Partial)

```json
{
  "generated_at": "2024-06-15T10:30:00",
  "codebase_path": "/path/to/codebase",
  "language": "java",
  "readme": "# Getting Started\n\n## Prerequisites\n...",
  "api_reference": "# API Reference\n\n## Summary Table\n...",
  "architecture": "# Architecture\n\n## Overview\n...",
  "examples": "# Examples\n\n## Authentication\n...",
  "architecture_diagram": "graph TD\n  A[Controller]\n  B[Service]\n...",
  "summary": "Generated documentation for java codebase",
  "total_files": 25,
  "total_endpoints": 18
}
```

---

## Next Steps

1. Run the pipeline: `uvx crewai run`
2. Check `docs/` folder for organized output
3. Review each markdown file for completeness
4. Use diagrams/architecture.mermaid in documentation or presentations
5. Iterate and regenerate as needed — structure remains consistent

