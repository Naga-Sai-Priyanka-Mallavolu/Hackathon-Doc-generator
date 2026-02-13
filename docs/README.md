# Documentation Generator

## Table of Contents
<<<<<<< Updated upstream
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
=======
- [Project Overview](#project-overview)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Quick Start Example](#quick-start-example)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Further Documentation](#further-documentation)

## Project Overview
**doc‑generator** is an AI‑powered documentation generator that extracts source code, configuration, and test information from a repository, runs a series of crew‑AI agents, evaluates the output with GEval metrics, and writes a complete set of markdown documentation (README, API reference, architecture diagram, examples, test docs, etc.).

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
>>>>>>> Stashed changes
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docgen
POSTGRES_USER=docgen_user
<<<<<<< Updated upstream
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
=======
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
```

Expected JSON response (truncated):
>>>>>>> Stashed changes

```json
{
  "status": "success",
  "metrics": {
    "language": "python",
<<<<<<< Updated upstream
    "total_files": 42,
    "total_endpoints": 7,
    "docs_path": "/absolute/path/to/documentation-generator/docs"
=======
    "total_files": 120,
    "total_endpoints": 5,
    "docs_path": "/full/path/to/generated-docs"
>>>>>>> Stashed changes
  }
}
```

<<<<<<< Updated upstream
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
=======
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
>>>>>>> Stashed changes
