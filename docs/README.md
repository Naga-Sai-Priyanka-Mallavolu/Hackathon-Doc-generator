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