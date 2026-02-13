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