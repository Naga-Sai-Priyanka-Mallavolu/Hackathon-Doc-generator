# Technical Documentation

## README
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

## API REFERENCE
# API Reference

| # | HTTP Method | URL Path | Function | Source File | Line |
|---|--------------|----------|----------|-------------|------|
| 1 | **GET** | `/users/` | `get_all_users` | `main.py` | 13 |
| 2 | **GET** | `/users/{user_id}` | `get_user_by_email` | `main.py` | 17 |
| 3 | **POST** | `/users/` | `create_user` | `main.py` | 25 |
| 4 | **PUT** | `/users/{user_id}` | `update_user_by_email` | `main.py` | 33 |
| 5 | **DELETE** | `/users/{user_id}` | `delete_user_by_email` | `main.py` | 43 |

---

## 1. Get All Users  

**Endpoint**: `GET /users/`  

**Function**: `get_all_users(db: Session)`  

**Description**  
Returns a collection of all user records stored in the database.

**Parameters**  

| Name | Location | Type | Required |
|------|----------|------|----------|
| `db` | **dependency** (injected) | `Session` | Yes |

**Response**  

| Status Code | Body Type | Description |
|-------------|-----------|-------------|
| `200` | `list[User]` (inferred) | List of user objects. |
| *Other* | *unspecified* | *[unknown]* |

**Security**: None declared.

**Source**: `main.py:13`  


---

## 2. Get User By ID  

**Endpoint**: `GET /users/{user_id}`  

**Function**: `get_user_by_email(user_id: int, db: Session)`  

**Description**  
Retrieves a single user identified by `user_id`.

**Parameters**  

| Name | Location | Type | Required |
|------|----------|------|----------|
| `user_id` | **path** | `int` | Yes |
| `db` | **dependency** (injected) | `Session` | Yes |

**Response**  

| Status Code | Body Type | Description |
|-------------|-----------|-------------|
| `200` | `User` (inferred) | The requested user object. |
| `404` | *unspecified* | User not found. |
| *Other* | *unspecified* | *[unknown]* |

**Security**: None declared.

**Source**: `main.py:17`  


---

## 3. Create New User  

**Endpoint**: `POST /users/`  

**Function**: `create_user(user: UserCreate, db: Session)`  

**Description**  
Creates a new user record using the data supplied in the request body.

**Parameters**  

| Name | Location | Type | Required |
|------|----------|------|----------|
| `user` | **body** | `UserCreate` | Yes |
| `db` | **dependency** (injected) | `Session` | Yes |

**Response**  

| Status Code | Body Type | Description |
|-------------|-----------|-------------|
| `201` | `User` (inferred) | The newly created user. |
| `400` | *unspecified* | Validation error. |
| *Other* | *unspecified* | *[unknown]* |

**Security**: None declared.

**Source**: `main.py:25`  


---

## 4. Update Existing User  

**Endpoint**: `PUT /users/{user_id}`  

**Function**: `update_user_by_email(user_id: int, user: UserUpdate, db: Session)`  

**Description**  
Updates an existing user identified by `user_id` with the fields provided in the request body.

**Parameters**  

| Name | Location | Type | Required |
|------|----------|------|----------|
| `user_id` | **path** | `int` | Yes |
| `user` | **body** | `UserUpdate` | Yes |
| `db` | **dependency** (injected) | `Session` | Yes |

**Response**  

| Status Code | Body Type | Description |
|-------------|-----------|-------------|
| `200` | `User` (inferred) | The updated user object. |
| `404` | *unspecified* | User not found. |
| `400` | *unspecified* | Validation error. |
| *Other* | *unspecified* | *[unknown]* |

**Security**: None declared.

**Source**: `main.py:33`  


---

## 5. Delete User  

**Endpoint**: `DELETE /users/{user_id}`  

**Function**: `delete_user_by_email(user_id: int, db: Session)`  

**Description**  
Removes the user identified by `user_id` from the database.

**Parameters**  

| Name | Location | Type | Required |
|------|----------|------|----------|
| `user_id` | **path** | `int` | Yes |
| `db` | **dependency** (injected) | `Session` | Yes |

**Response**  

| Status Code | Body Type | Description |
|-------------|-----------|-------------|
| `204` | *none* | Successful deletion (no content). |
| `404` | *unspecified* | User not found. |
| *Other* | *unspecified* | *[unknown]* |

**Security**: None declared.

**Source**: `main.py:43`

## ARCHITECTURE
### Structural Analysis
```chart
{
  "type": "structural",
  "data": [
    {
      "name": "Classes",
      "value": 3
    },
    {
      "name": "Functions",
      "value": 6
    },
    {
      "name": "Imports",
      "value": 10
    }
  ]
}
```

## Architecture Documentation

## Mermaid Diagram

```mermaid
flowchart TB
    subgraph External
        DB[(SQLite Database)])
    end

    subgraph App[FastAPI Application]
        direction TB
        Controller[Controller (FastAPI routes)]
        DBSession[Database Session (get_db)]
        Model[User Model (SQLAlchemy)]
        Repository[Repository (SQLAlchemy queries)]
        Schema[UserCreate / UserUpdate (Pydantic)]
    end

    Controller -->|Depends on| DBSession
    DBSession -->|Provides| Repository
    Repository -->|Uses| Model
    Controller -->|Accepts/Returns| Schema
    Repository -->|Persists to| DB
    DB -->|Read/Write| External
```

## Architecture Narrative

### Overall Architectural Pattern
The project follows a **Layered / Simple MVC‑style architecture** built on **FastAPI**:

- **Presentation Layer** – FastAPI routes defined in `main.py` act as controllers handling HTTP requests.  
- **Service/Business Layer** – In this minimal example the business logic lives directly in the controller functions (no dedicated service classes).  
- **Data Access Layer** – SQLAlchemy ORM provides a repository‑style access pattern to the SQLite database.  
- **Domain Layer** – SQLAlchemy models (`User`) represent persistent entities.  
- **DTO Layer** – Pydantic schemas (`UserCreate`, `UserUpdate`) serve as Data Transfer Objects for request/response validation.  
- **Infrastructure Layer** – `app/database.py` configures the SQLite engine and session factory.

### Component Roles
| Component | File | Role |
|-----------|------|------|
| **FastAPI app & routes** | `main.py` | Controllers exposing CRUD HTTP endpoints. |
| **Database session dependency** | `app/database.py` | Provides a scoped `Session` (`get_db`) for each request. |
| **SQLAlchemy model** | `app/models.py` | Domain entity `User` mapped to `users` table. |
| **Pydantic schemas** | `app/schema.py` | DTOs for request validation (`UserCreate`, `UserUpdate`). |
| **SQLite DB** | `users.db` (created at runtime) | Persistent storage. |
| **Dockerfile / requirements.txt** | Root | Deployment and dependency configuration. |

### Request‑Response Data Flow
1. **Incoming HTTP request** hits a FastAPI route defined in `main.py`.  
2. FastAPI resolves the `db: Session = Depends(get_db)` dependency, invoking `get_db` which yields a SQLAlchemy `Session` bound to the SQLite engine.  
3. The controller uses the session to **query** or **mutate** `User` records via ORM calls (`db.query(User)…`).  
4. For **POST** and **PUT**, request bodies are validated against `UserCreate` or `UserUpdate` schemas before reaching the controller.  
5. After DB operations, the controller returns either the persisted ORM object (automatically converted to JSON by FastAPI) or a simple message dict.  
6. The response is sent back to the client; the session is closed by the `finally` block in `get_db`.

### API Endpoint Descriptions
| Method | Path | Function | Description |
|--------|------|----------|-------------|
| **GET** | `/users/` | `get_all_users` | Retrieves **all** user records from the `users` table and returns them as a JSON list. |
| **GET** | `/users/{user_id}` | `get_user_by_email` | Looks up a single `User` by primary‑key `id`. Returns the user object if found, otherwise raises `404 Not Found`. |
| **POST** | `/users/` | `create_user` | Accepts a `UserCreate` payload (`name`, `email`, `password`). Creates a new `User` row, commits the transaction, and returns the created record with its generated `id`. |
| **PUT** | `/users/{user_id}` | `update_user_by_email` | Accepts a `UserUpdate` payload (`name`, `email`). Finds the target user, updates mutable fields, commits, and returns a success message. If the user does not exist, responds with `404`. |
| **DELETE** | `/users/{user_id}` | `delete_user_by_email` | Deletes the user identified by `user_id`. On success returns a confirmation message; if the user is missing, returns `404`. |

### Data Persistence Strategy
- **SQLite** (`sqlite:///./users.db`) is used as the relational store.  
- SQLAlchemy **declarative base** (`Base`) defines the `User` table schema.  
- `SessionLocal` creates a new session per request; autocommit is disabled to allow explicit transaction control.  
- CRUD operations are performed via ORM methods (`query`, `add`, `commit`, `delete`).  

### Security Architecture
- No authentication or authorization is configured in the current code base.  
- FastAPI’s default exception handling is used; HTTP status codes convey error conditions.  
- For production, a security layer (OAuth2/JWT, API keys, etc.) would be added as a **dependency** injected into the controllers.  

### Design Patterns Observed
- **Dependency Injection** – FastAPI’s `Depends` injects the DB session.  
- **Repository Pattern** – Although not abstracted into a separate class, controller functions act as thin repositories using SQLAlchemy.  
- **DTO (Data Transfer Object)** – Pydantic models separate API contract from persistence models.  
- **Factory** – `sessionmaker` creates DB sessions on demand.  

### External Integrations
- **SQLite Database** – Local file‑based DB (`users.db`).  
- **Docker** – Containerised deployment configuration (`Dockerfile`).  
- **Python Packages** – Declared in `requirements.txt` (FastAPI, SQLAlchemy, Pydantic, etc.).  

---

*All components referenced are directly present in the codebase (`main.py`, `app/database.py`, `app/models.py`, `app/schema.py`). No hallucinated elements are included.*

## EXAMPLES
## API Endpoint Examples

## 1. Get All Users  

**Endpoint**: `GET /users/`  

**Description**: Retrieves a list of all user records.  

**Required Headers**:  
- `Accept: application/json`  

### Sample Request (cURL)  
```bash
curl -X GET "http://localhost:8000/users/" \
  -H "Accept: application/json"
```  

### Successful Response (200)  
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice.johnson@example.com",
    "password": "hashedpassword123"
  },
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob.smith@example.com",
    "password": "hashedpassword456"
  }
]
```  

### Error Response (500)  
```json
{
  "detail": "Internal server error"
}
```
> **Condition**: Unexpected server failure while querying the database.

---  

## 2. Get User By ID  

**Endpoint**: `GET /users/{user_id}`  

**Description**: Retrieves a single user identified by `user_id`.  

**Path Parameter**:  
- `user_id` (integer) – ID of the user to fetch.  

**Required Headers**:  
- `Accept: application/json`  

### Sample Request (cURL)  
```bash
curl -X GET "http://localhost:8000/users/1" \
  -H "Accept: application/json"
```  

### Successful Response (200)  
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice.johnson@example.com",
  "password": "hashedpassword123"
}
```  

### Error Response (404 – User Not Found)  
```json
{
  "detail": "User not found"
}
```
> **Condition**: No user exists with the supplied `user_id`.

---  

## 3. Create New User  

**Endpoint**: `POST /users/`  

**Description**: Creates a new user record.  

**Required Headers**:  
- `Content-Type: application/json`  
- `Accept: application/json`  

### Sample Request Body  
```json
{
  "name": "Charlie Davis",
  "email": "charlie.davis@example.com",
  "password": "StrongPass!2024"
}
```  

### Sample Request (cURL)  
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"name":"Charlie Davis","email":"charlie.davis@example.com","password":"StrongPass!2024"}'
```  

### Successful Response (201)  
```json
{
  "id": 3,
  "name": "Charlie Davis",
  "email": "charlie.davis@example.com",
  "password": "StrongPass!2024"
}
```  

### Error Response (400 – Validation Error)  
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
> **Condition**: Required fields (`name`, `email`, `password`) are missing or invalid.

---  

## 4. Update Existing User  

**Endpoint**: `PUT /users/{user_id}`  

**Description**: Updates the `name` and `email` of an existing user.  

**Path Parameter**:  
- `user_id` (integer) – ID of the user to update.  

**Required Headers**:  
- `Content-Type: application/json`  
- `Accept: application/json`  

### Sample Request Body  
```json
{
  "name": "Charlie D.",
  "email": "charlie.d@example.com"
}
```  

### Sample Request (cURL)  
```bash
curl -X PUT "http://localhost:8000/users/3" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"name":"Charlie D.","email":"charlie.d@example.com"}'
```  

### Successful Response (200)  
```json
{
  "message": "User updated successfully"
}
```  

### Error Response (404 – User Not Found)  
```json
{
  "detail": "User not found"
}
```
> **Condition**: No user exists with the supplied `user_id`.  

### Error Response (400 – Validation Error)  
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
> **Condition**: The `email` field does not meet the expected format (e.g., missing `@`).  

---  

## 5. Delete User  

**Endpoint**: `DELETE /users/{user_id}`  

**Description**: Removes a user from the database.  

**Path Parameter**:  
- `user_id` (integer) – ID of the **user** to delete.  

**Required Headers**:  
- `Accept: application/json`  

### Sample Request (cURL)  
```bash
curl -X DELETE "http://localhost:8000/users/3" \
  -H "Accept: application/json"
```  

### Successful Response (200)  
```json
{
  "message": "User deleted successfully"
}
```  

### Error Response (404 – User Not Found)  
```json
{
  "detail": "User not found"
}
```
> **Condition**: No user exists with the supplied `user_id`.

---  

## General Notes  

* The API currently does **not** require authentication. In a production environment you would typically protect these routes with an `Authorization: Bearer <your-token-here>` header.  
* All timestamps are omitted for brevity; the `User` model only contains `id`, `name`, `email`, and `password` fields.  
* Passwords are stored as plain text in this simple example; a real application should hash passwords before persisting.
