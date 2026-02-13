<<<<<<< Updated upstream
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
=======
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
>>>>>>> Stashed changes
