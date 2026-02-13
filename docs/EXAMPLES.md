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