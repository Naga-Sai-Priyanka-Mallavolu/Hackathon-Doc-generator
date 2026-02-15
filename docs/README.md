### File Extension Distribution
```chart
{
  "type": "file_dist",
  "data": [
    {
      "name": ".py",
      "value": 5
    }
  ]
}
```

# FastAPI CRUD User Service

**FastAPI CRUD User Service**

This repository implements a simple CRUD (Create Read Update Delete) API for managing user records using **FastAPI** and **SQLAlchemy** with a local **SQLite** database. The service exposes RESTful endpoints to list users, retrieve a single user, create new users, update existing users, and delete users. It demonstrates a layered architecture with clear separation of concerns:

- **Presentation Layer:** FastAPI routes defined in `main.py`.
- **Data Access Layer:** SQLAlchemy ORM models (`User`) and session management (`app/database.py`).
- **DTO Layer:** Pydantic schemas (`UserCreate`, `UserUpdate`).
- **Infrastructure:** Dockerfile for containerised deployment and `requirements.txt` for dependencies.

## Table of Contents
- [Project Overview](#fastapi-crud-user-service)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Quick Start](#quick-start)
- [API Endpoint Descriptions](#api-endpoint-descriptions)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

See the full API reference in **[API_REFERENCE.md](API_REFERENCE.md)**.  
For details on system design, consult **[ARCHITECTURE.md](ARCHITECTURE.md)**.  
Example usage of each endpoint is provided in **[EXAMPLES.md](EXAMPLES.md)**.

## Prerequisites

| Tool | Minimum Version |
|------|-----------------|
| Python | 3.10 (the Docker image uses `python:3.10-slim`) |
| pip | Latest (used to install `requirements.txt`) |
| Docker | 20.10+ (optional, for containerised run) |
| Git | 2.20+ |

*No external database server is required; the app uses an SQLite file (`users.db`).*  

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-org/fastapi-crud-user-service.git
   cd fastapi-crud-user-service
   ```

2. **Create a virtual environment (optional but recommended)**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **(Optional) Build and run with Docker**  
   ```bash
   docker build -t fastapi-crud-user-service .
   docker run -p 8000:8000 fastapi-crud-user-service
   ```
   The container automatically creates an empty `users.db` file and starts the API on port **8000**.  

## Configuration

A template for environment variables is provided in `.env.example`:

```
DB_NAME=fastapi
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_PORT=5432
```

*These variables are currently unused because the app connects to a local SQLite file (`sqlite:///./users.db`).* They are kept for future extension to external databases.

### Database
- The SQLite file `users.db` is created automatically on first start. No manual migration step is required.  
- To start with a fresh database, simply delete `users.db` before launching the app.  

## Running the Application

### Local (development) mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- `--reload` enables live code reloading.  
- The API will be reachable at **http://localhost:8000**.

### Expected startup output
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Running Tests

The repository includes a test suite under the `tests/` directory. To execute them:

```bash
pytest
```

- Run a specific file: `pytest tests/test_users.py`  
- Expected result: a summary showing **X passed** and **0 failed**.  

## Quick Start

1. Start the API (see *Running the Application*).  
2. Verify the service is alive:
   ```bash
   curl -X GET "http://localhost:8000/users/" -H "Accept: application/json"
   ```
   You should receive an empty JSON array (`[]`) on a fresh database.  
3. Create a user to see the full flow (see API endpoint examples below).  

## API Endpoint Descriptions

| Method | Path | Request Body | Success Response | Description |
|--------|------|--------------|------------------|-------------|
| **GET** | `/users/` | – | `200 OK` – JSON array of all users | Returns every user stored in the SQLite `users` table. |
| **GET** | `/users/{user_id}` | – | `200 OK` – JSON object of the requested user | Retrieves a single user identified by its integer `user_id`. Returns **404** if not found. |
| **POST** | `/users/` | `UserCreate` (`name`, `email`, `password`) | `201 Created` – JSON object of the newly created user (including generated `id`) | Creates a new record. All three fields are required. |
| **PUT** | `/users/{user_id}` | `UserUpdate` (`name`, `email`) | `200 OK` – `{ "message": "User updated successfully" }` | Updates mutable fields of an existing user. Returns **404** if the user does not exist. |
| **DELETE** | `/users/{user_id}` | – | `200 OK` – `{ "message": "User deleted successfully" }` | Removes the user from the database. Returns **404** if the user is missing. |

## Project Structure
```
.
├── Dockerfile               # Container definition (Python 3.10‑slim)
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables (future DB config)
├── main.py                  # FastAPI app + route definitions (controllers)
├── app/
│   ├── __init__.py
│   ├── database.py          # SQLite engine and SessionLocal factory
│   ├── models.py            # SQLAlchemy User model
│   └── schema.py            # Pydantic request/response schemas
├── tests/ (optional)        # Pytest test suite
└── users.db (created at runtime)
```
- **Controllers** live in `main.py`.  
- **Database session** is provided via the `Depends(get_db)` dependency.  
- **Models** and **schemas** are separated for clarity and re‑usability.  

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `Address already in use: bind` on startup | Port **8000** is occupied | Stop the conflicting process or run `uvicorn main:app --port <other>` |
| `sqlite3.OperationalError: unable to open database file` | No write permission for the working directory | Ensure the current user has write access, or specify an absolute path for `users.db` in `app/database.py` |
| ImportError / missing package | Dependencies not installed | Re‑run `pip install -r requirements.txt` or rebuild the Docker image |
| `404 Not Found` when calling `/users/{id}` | User with that `id` does not exist | Create the user first (`POST /users/`) or verify the `id` value |
| Tests fail with `ImportError` | Virtual environment not activated | Activate the venv (`source venv/bin/activate`) before running `pytest` |

If you encounter other issues, consult the FastAPI documentation or open an issue on the repository.

---  

*End of Getting Started guide.*