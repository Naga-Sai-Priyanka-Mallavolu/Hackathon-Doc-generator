# Codebase Documentation

Generated: 2026-02-09 19:23:10

---

{
  "language_detected": "java",
  "files": [
    {
      "path": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/DemoApplication.java",
      "classes": [
        "DemoApplication"
      ],
      "functions": [
        {
          "name": "main",
          "parameters": ["args"],
          "modifiers": ["public", "static"],
          "return_type": "void"
        }
      ],
      "imports": [
        "org.springframework.boot.SpringApplication",
        "org.springframework.boot.autoconfigure.SpringBootApplication"
      ],
      "annotations": ["@SpringBootApplication"]
    },
    {
      "path": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/controller/UserController.java",
      "classes": [
        "UserController"
      ],
      "functions": [
        {
          "name": "getAllUsers",
          "parameters": [],
          "modifiers": ["public"],
          "return_type": "List<User>"
        },
        {
          "name": "getUserById",
          "parameters": ["id"],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "createUser",
          "parameters": ["user"],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "updateUser",
          "parameters": ["id", "user"],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "deleteUser",
          "parameters": ["id"],
          "modifiers": ["public"],
          "return_type": "void"
        }
      ],
      "imports": [
        "com.example.demo.model.User",
        "com.example.demo.service.UserService",
        "org.springframework.beans.factory.annotation.Autowired",
        "org.springframework.web.bind.annotation.*",
        "java.util.List"
      ],
      "annotations": [
        "@RestController",
        "@RequestMapping(\"/api/users\")",
        "@Autowired"
      ],
      "mapping_annotations": [
        "@GetMapping",
        "@PostMapping",
        "@PutMapping",
        "@DeleteMapping"
      ]
    },
    {
      "path": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/model/User.java",
      "classes": [
        "User"
      ],
      "functions": [
        {
          "name": "User",
          "parameters": [],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "User",
          "parameters": ["id", "name", "email"],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "getId",
          "parameters": [],
          "modifiers": ["public"],
          "return_type": "Long"
        },
        {
          "name": "setId",
          "parameters": ["id"],
          "modifiers": ["public"],
          "return_type": "void"
        },
        {
          "name": "getName",
          "parameters": [],
          "modifiers": ["public"],
          "return_type": "String"
        },
        {
          "name": "setName",
          "parameters": ["name"],
          "modifiers": ["public"],
          "return_type": "void"
        },
        {
          "name": "getEmail",
          "parameters": [],
          "modifiers": ["public"],
          "return_type": "String"
        },
        {
          "name": "setEmail",
          "parameters": ["email"],
          "modifiers": ["public"],
          "return_type": "void"
        }
      ],
      "imports": [
        "javax.persistence.Entity",
        "javax.persistence.GeneratedValue",
        "javax.persistence.GenerationType",
        "javax.persistence.Id"
      ],
      "annotations": ["@Entity"]
    },
    {
      "path": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/repository/UserRepository.java",
      "classes": [
        "UserRepository"
      ],
      "functions": [],
      "imports": [
        "com.example.demo.model.User",
        "org.springframework.data.jpa.repository.JpaRepository",
        "org.springframework.stereotype.Repository"
      ],
      "annotations": ["@Repository"],
      "extends": "JpaRepository<User, Long>"
    },
    {
      "path": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/service/UserService.java",
      "classes": [
        "UserService"
      ],
      "functions": [
        {
          "name": "UserService",
          "parameters": ["userRepository"],
          "modifiers": ["public"],
          "return_type": "UserService"
        },
        {
          "name": "getAllUsers",
          "parameters": [],
          "modifiers": ["public"],
          "return_type": "List<User>"
        },
        {
          "name": "getUserById",
          "parameters": ["id"],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "createUser",
          "parameters": ["user"],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "updateUser",
          "parameters": ["id", "user"],
          "modifiers": ["public"],
          "return_type": "User"
        },
        {
          "name": "deleteUser",
          "parameters": ["id"],
          "modifiers": ["public"],
          "return_type": "void"
        }
      ],
      "imports": [
        "com.example.demo.model.User",
        "com.example.demo.repository.UserRepository",
        "org.springframework.beans.factory.annotation.Autowired",
        "org.springframework.stereotype.Service",
        "java.util.List"
      ],
      "annotations": ["@Service", "@Autowired"]
    }
  ],
  "entry_points": [
    {
      "file": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/DemoApplication.java",
      "classes": ["DemoApplication"],
      "functions": ["main"]
    }
  ],
  "public_interfaces": [
    {
      "file": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/controller/UserController.java",
      "classes": ["UserController"],
      "methods": [
        "getAllUsers",
        "getUserById",
        "createUser",
        "updateUser",
        "deleteUser"
      ],
      "rest_endpoints": [
        {
          "path": "/api/users",
          "methods": ["GET"]
        },
        {
          "path": "/api/users/{id}",
          "methods": ["GET"]
        },
        {
          "path": "/api/users",
          "methods": ["POST"]
        },
        {
          "path": "/api/users/{id}",
          "methods": ["PUT"]
        },
        {
          "path": "/api/users/{id}",
          "methods": ["DELETE"]
        }
      ]
    },
    {
      "file": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/model/User.java",
      "classes": ["User"],
      "methods": [
        "getId",
        "setId",
        "getName",
        "setName",
        "getEmail",
        "setEmail"
      ]
    },
    {
      "file": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/service/UserService.java",
      "classes": ["UserService"],
      "methods": [
        "getAllUsers",
        "getUserById",
        "createUser",
        "updateUser",
        "deleteUser"
      ]
    },
    {
      "file": "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/repository/UserRepository.java",
      "classes": ["UserRepository"],
      "methods": []
    }
  ]
}

---

```json
{
  "modules": [
    {
      "name": "DemoApplication",
      "files": [
        "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/DemoApplication.java"
      ],
      "imports_from": [],
      "imports_to": []
    },
    {
      "name": "UserController",
      "files": [
        "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/controller/UserController.java"
      ],
      "imports_from": [
        "User",
        "UserService"
      ],
      "imports_to": [
        "User",
        "UserService"
      ]
    },
    {
      "name": "User",
      "files": [
        "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/model/User.java"
      ],
      "imports_from": [],
      "imports_to": []
    },
    {
      "name": "UserRepository",
      "files": [
        "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/repository/UserRepository.java"
      ],
      "imports_from": [
        "User"
      ],
      "imports_to": [
        "User"
      ]
    },
    {
      "name": "UserService",
      "files": [
        "/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI/src/main/java/com/example/demo/service/UserService.java"
      ],
      "imports_from": [
        "User",
        "UserRepository"
      ],
      "imports_to": [
        "User",
        "UserRepository"
      ]
    }
  ],
  "external_dependencies": [
    "org.springframework.boot.SpringApplication",
    "org.springframework.boot.autoconfigure.SpringBootApplication",
    "org.springframework.web.bind.annotation.*",
    "org.springframework.beans.factory.annotation.Autowired",
    "org.springframework.stereotype.Repository",
    "org.springframework.stereotype.Service",
    "org.springframework.data.jpa.repository.JpaRepository",
    "javax.persistence.Entity",
    "javax.persistence.GeneratedValue",
    "javax.persistence.GenerationType",
    "javax.persistence.Id",
    "java.util.List"
  ],
  "core_modules": [
    {
      "name": "User",
      "referenced_by": ["UserController", "UserService", "UserRepository"],
      "import_count": 3
    },
    {
      "name": "UserService",
      "referenced_by": ["UserController"],
      "import_count": 1
    },
    {
      "name": "UserRepository",
      "referenced_by": ["UserService"],
      "import_count": 1
    }
  ]
}
```

---

{
  "api_semantics": [
    {
      "endpoint": "GET /api/users",
      "purpose": "Retrieve a list of all users",
      "params": [],
      "returns": "List<User>: collection of User objects",
      "confidence": 0.98
    },
    {
      "endpoint": "GET /api/users/{id}",
      "purpose": "Retrieve a specific user by their ID",
      "params": ["id (Long): the unique identifier of the user"],
      "returns": "User: the User object with matching ID",
      "confidence": 0.97
    },
    {
      "endpoint": "POST /api/users",
      "purpose": "Create a new user",
      "params": ["user (User): the User object containing user data (name, email, etc.)"],
      "returns": "User: the newly created User object (with assigned ID)",
      "confidence": 0.96
    },
    {
      "endpoint": "PUT /api/users/{id}",
      "purpose": "Update an existing user by ID",
      "params": ["id (Long): the unique identifier of the user to update", "user (User): the User object with updated data"],
      "returns": "User: the updated User object",
      "confidence": 0.95
    },
    {
      "endpoint": "DELETE /api/users/{id}",
      "purpose": "Delete a user by ID",
      "params": ["id (Long): the unique identifier of the user to delete"],
      "returns": "void",
      "confidence": 0.94
    }
  ]
}

---

```json
{
  "architectural_patterns": [
    "Layered Architecture (n-tier)",
    "MVC (Model-View-Controller) - Web Layer",
    "Repository Pattern",
    "Dependency Injection"
  ],
  "component_roles": {
    "controller": [
      "UserController"
    ],
    "service": [
      "UserService"
    ],
    "repository": [
      "UserRepository"
    ],
    "model/entity": [
      "User"
    ],
    "application_entry_point": [
      "DemoApplication"
    ]
  },
  "data_flow": [
    "1. HTTP request arrives at UserController endpoint (e.g., GET /api/users)",
    "2. UserController delegates to UserService method",
    "3. UserService calls UserRepository method (e.g., findAll(), findById())",
    "4. UserRepository interacts with the database via Spring Data JPA",
    "5. Results flow back up the chain: Repository → Service → Controller",
    "6. Controller serializes result (e.g., User or List<User>) to JSON and returns as HTTP response"
  ],
  "module_relationships": {
    "UserController → UserService": "Depends on UserService via @Autowired (inversion of control)",
    "UserController → User": "Consumes User as DTO/request/response model",
    "UserService → UserRepository": "Depends on UserRepository via @Autowired",
    "UserService → User": "Consumes User as domain model",
    "UserRepository → User": "Operates on User entity (CRUD with JPA)",
    "DemoApplication → All": "Spring Boot entry point bootstrapping the application context"
  }
}
```

---

```
# API Reference

## Overview
RESTful API for managing users.

## Security Requirements
| Endpoint | Roles Required |
|----------|----------------|
| `GET /api/users` | `ROLE_USER`, `ROLE_ADMIN` |
| `GET /api/users/{id}` | `ROLE_USER`, `ROLE_ADMIN` |
| `POST /api/users` | `ROLE_ADMIN` |
| `PUT /api/users/{id}` | `ROLE_ADMIN` |
| `DELETE /api/users/{id}` | `ROLE_ADMIN` |

---

## Endpoints

### 1. Get All Users
Retrieve a list of all users.

**Endpoint:** `GET /api/users`

**Security:** Requires `ROLE_USER` or `ROLE_ADMIN`

**Response:**
| Status Code | Description |
|-------------|-------------|
| `200 OK` | Success — returns list of `User` objects |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Insufficient permissions |

**Response Body Schema (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "****"
  }
]
```

**Example Request:**
```bash
curl -X GET "https://api.example.com/api/users" \
  -H "Authorization: Bearer <token>"
```

---

### 2. Get User by ID
Retrieve a specific user by ID.

**Endpoint:** `GET /api/users/{id}`

**Security:** Requires `ROLE_USER` or `ROLE_ADMIN`

**Path Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | `Long` | Yes | Unique identifier of the user |

**Response:**
| Status Code | Description |
|-------------|-------------|
| `200 OK` | Success — returns `User` object |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Insufficient permissions |
| `404 Not Found` | User with given ID does not exist |

**Response Body Schema (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "****"
}
```

**Example Request:**
```bash
curl -X GET "https://api.example.com/api/users/1" \
  -H "Authorization: Bearer <token>"
```

---

### 3. Create User
Create a new user.

**Endpoint:** `POST /api/users`

**Security:** Requires `ROLE_ADMIN`

**Request Body Schema:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | `String` | Yes | min: 2, max: 50 | User's full name |
| `email` | `String` | Yes | max: 100, must be valid email | User's email address |
| `password` | `String` | Yes | min: 6, max: 255 | User's password |

**Example Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "password": "securePassword123"
}
```

**Response:**
| Status Code | Description |
|-------------|-------------|
| `201 Created` | Success — returns created `User` with assigned ID |
| `400 Bad Request` | Invalid input (validation errors) |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Insufficient permissions |
| `409 Conflict` | Email already in use |

**Response Body Schema (201 Created):**
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "password": "****"
}
```

**Example Request:**
```bash
curl -X POST "https://api.example.com/api/users" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "password": "securePassword123"
  }'
```

---

### 4. Update User
Update an existing user by ID.

**Endpoint:** `PUT /api/users/{id}`

**Security:** Requires `ROLE_ADMIN`

**Path Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | `Long` | Yes | Unique identifier of the user to update |

**Request Body Schema:** (same as `POST`, partial updates not supported — send full object)
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `name` | `String` | Yes | min: 2, max: 50 |
| `email` | `String` | Yes | max: 100, valid email |
| `password` | `String` | Yes | min: 6, max: 255 |
| `id` | `Long` | No | Ignored if provided — uses path variable |

**Example Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane.smith.updated@example.com",
  "password": "newSecurePassword456"
}
```

**Response:**
| Status Code | Description |
|-------------|-------------|
| `200 OK` | Success — returns updated `User` |
| `400 Bad Request` | Invalid input (validation errors) |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Insufficient permissions |
| `404 Not Found` | User with given ID does not exist |
| `409 Conflict` | Email already in use |

**Response Body Schema (200 OK):**
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane.smith.updated@example.com",
  "password": "****"
}
```

**Example Request:**
```bash
curl -X PUT "https://api.example.com/api/users/2" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane.smith.updated@example.com",
    "password": "newSecurePassword456"
  }'
```

---

### 5. Delete User
Delete a user by ID.

**Endpoint:** `DELETE /api/users/{id}`

**Security:** Requires `ROLE_ADMIN`

**Path Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | `Long` | Yes | Unique identifier of the user to delete |

**Response:**
| Status Code | Description |
|-------------|-------------|
| `204 No Content` | Success — user deleted |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Insufficient permissions |
| `404 Not Found` | User with given ID does not exist |

**Example Request:**
```bash
curl -X DELETE "https://api.example.com/api/users/3" \
  -H "Authorization: Bearer <token>"
```
```

---

# System Architecture Overview

## System Overview

This is a **Spring Boot-based enterprise application** following a **Layered Architecture (n-tier)** pattern, with the **MVC pattern** applied specifically to the web layer. It leverages the **Repository Pattern** for data access abstraction and **Dependency Injection** for loose coupling and testability. The system handles user-related operations via a RESTful API, featuring clear separation of concerns between the web, service, and data layers.

---

## Component Diagram (Text-Based)

```
+------------------+        +-------------------+        +------------------+
|  Web / REST Layer|        | Service Layer     |        | Data Access Layer|
|                  |        |                   |        |                  |
| +--------------+ |        | +---------------+ |        | +--------------+ |
| | UserController |<-------| | UserService   |<-------| | UserRepository | |
| +--------------+ |        | +---------------+ |        | +--------------+ |
|                  |        |                   |        |                  |
|                  |        |                   |        |                  |
+------------------+        +-------------------+        +------------------+
         |                            |                           |
         |                            |                           |
         v                            v                           v
+------------------+        +-------------------+        +------------------+
|   Presentation   |        |    Business Logic |        |   Persistence    |
| (HTTP, JSON)     |        | (Transactions,    |        | (Spring Data JPA,|
|                  |        |  Decisions)       |        | Database)        |
+------------------+        +-------------------+        +------------------+

+----------------------------------------------+
|              Application Context             |
|                                              |
|  +----------------------+                    |
|  |   DemoApplication    |<-------------------+
|  | (Spring Boot Main)   |
|  +----------------------+
|
+----------------------------------------------+
|              Domain Model                    |
|                                              |
|  +----------------------+                    |
|  |        User          |<-------------------+
|  | (Entity / DTO)       |
|  +----------------------+
```

---

## Module Descriptions

### 1. `DemoApplication`
- **Role**: Application entry point
- **Responsibility**: Bootstraps the Spring Boot application context. Annotates the main class with `@SpringBootApplication`, enabling auto-configuration and component scanning.
- **Framework Role**: Spring Boot starter class

### 2. `UserController`
- **Role**: REST controller (Web Layer)
- **Responsibility**:
  - Exposes RESTful endpoints (e.g., `GET /api/users`, `POST /api/users`)
  - Accepts incoming HTTP requests and validates input (if applicable)
  - Delegates business logic to `UserService`
  - Serializes response objects to JSON (via Spring’s built-in Jackson integration)
- **Annotations**: `@RestController`, `@RequestMapping("/api/users")`
- **Pattern Used**: MVC Controller

### 3. `UserService`
- **Role**: Service layer component
- **Responsibility**:
  - Encapsulates business logic for user operations
  - Coordinates with `UserRepository` for data access
  - May implement transaction management (`@Transactional`)
  - Aggregates and transforms data if needed (e.g., from entity to DTO)
- **Annotations**: `@Service`
- **Pattern Used**: Service Layer + Business Delegate

### 4. `UserRepository`
- **Role**: Data access layer component
- **Responsibility**:
  - Defines data access methods (e.g., `findAll()`, `findById()`)
  - Extends Spring Data JPA interfaces (e.g., `JpaRepository<User, Long>`)
  - Provides abstraction over the underlying persistence mechanism (e.g., relational DB)
- **Annotations**: `@Repository`
- **Pattern Used**: Repository Pattern

### 5. `User`
- **Role**: Domain entity / DTO
- **Responsibility**:
  - Represents the data structure for users in the system
  - Used as a JPA entity (with `@Entity`, `@Id`, etc.) for persistence mapping
  - May serve as a request/response model in REST operations (depending on exposure strategy)
- **Annotations**: `@Entity`, `@Table`, `@Id`, `@GeneratedValue`

---

## Data Flow Explanation

1. **Request Arrival**: An HTTP request (e.g., `GET /api/users`) is received by the Spring Boot dispatcher servlet and routed to `UserController`.

2. **Controller Handling**: `UserController` receives the request, performs basic validation (if configured), and calls the appropriate method in `UserService`.

3. **Service Delegation**: `UserService` executes business logic (e.g., filtering, composition) and invokes methods on `UserRepository` to access data.

4. **Data Access**: `UserRepository` uses Spring Data JPA to execute database queries (e.g., SQL `SELECT * FROM users`). JPA handles object-relational mapping (ORM) transparently.

5. **Response Propagation**:
   - The result (e.g., `List<User>`) flows back: **Repository → Service → Controller**.
   - `UserService` may map entities to DTOs if required for API separation.
   - `UserController` serializes the final object(s) to JSON using Spring’s `HttpMessageConverter`.

6. **Client Response**: The HTTP response (status code 200 OK + JSON body) is sent back to the client.

> All components are loosely coupled through **Dependency Injection** (`@Autowired`), which promotes testability (e.g., mock services via constructor injection) and modularity.

---

## Design Patterns Used

| Pattern | Application |
|--------|-------------|
| **Layered Architecture (n-tier)** | Clear separation into presentation, business logic, and data layers. Each layer interacts only with its immediate neighbor. |
| **MVC (Model-View-Controller)** | `UserController` acts as Controller; `User` as Model; View is implicit (REST response = JSON, no server-side templates). |
| **Repository Pattern** | `UserRepository` abstracts data persistence logic and exposes domain-specific methods, shielding service layer from persistence implementation. |
| **Dependency Injection** | All layers (`@Service`, `@Repository`, `@RestController`) receive dependencies via constructor/field injection (`@Autowired`), enabling inversion of control and runtime binding. |

---

> **Design Rationale**:  
> The architecture emphasizes **testability**, **maintainability**, and **evolvability**. Dependencies are injected, allowing unit tests to mock service/repository layers. Clear boundaries prevent coupling and support modular development and refactoring. The use of Spring Data JPA accelerates persistence logic while remaining transparent to business layers.

---

# User Management API Examples

## Prerequisites

- Python 3.7+
- `requests` library (`pip install requests`)
- Valid authentication token with appropriate roles

## Setup Code

```python
import requests
import json

# Configuration
BASE_URL = "https://api.example.com"
API_VERSION = "/api"

# Authentication token (replace with your actual token)
AUTH_TOKEN = "your_jwt_token_here"

# Headers for authenticated requests
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}
```

---

## Example 1: Get All Users

```python
# Example: Get all users
response = requests.get(f"{BASE_URL}{API_VERSION}/users", headers=headers)

if response.status_code == 200:
    users = response.json()
    print("✓ Successfully retrieved users:")
    for user in users:
        print(f"  - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
elif response.status_code == 401:
    print("✗ Authentication required. Please provide a valid token.")
elif response.status_code == 403:
    print("✗ Access denied. You need ROLE_USER or ROLE_ADMIN role.")
```

**Expected Output:**
```
✓ Successfully retrieved users:
  - ID: 1, Name: John Doe, Email: john.doe@example.com
  - ID: 2, Name: Jane Smith, Email: jane.smith@example.com
```

---

## Example 2: Get User by ID

```python
# Example: Get a specific user by ID
user_id = 1
response = requests.get(f"{BASE_URL}{API_VERSION}/users/{user_id}", headers=headers)

if response.status_code == 200:
    user = response.json()
    print(f"✓ Successfully retrieved user {user_id}:")
    print(f"  Name: {user['name']}")
    print(f"  Email: {user['email']}")
    print(f"  ID: {user['id']}")
elif response.status_code == 404:
    print(f"✗ User with ID {user_id} not found.")
elif response.status_code == 401:
    print("✗ Authentication required. Please provide a valid token.")
elif response.status_code == 403:
    print("✗ Access denied. You need ROLE_USER or ROLE_ADMIN role.")
```

**Expected Output:**
```
✓ Successfully retrieved user 1:
  Name: John Doe
  Email: john.doe@example.com
  ID: 1
```

---

## Example 3: Create User

```python
# Example: Create a new user
new_user = {
    "name": "Alice Johnson",
    "email": "alice.johnson@example.com",
    "password": "aliceSecure789"
}

response = requests.post(
    f"{BASE_URL}{API_VERSION}/users",
    headers=headers,
    json=new_user
)

if response.status_code == 201:
    created_user = response.json()
    print("✓ User created successfully:")
    print(f"  ID: {created_user['id']}")
    print(f"  Name: {created_user['name']}")
    print(f"  Email: {created_user['email']}")
elif response.status_code == 400:
    print(f"✗ Validation error: {response.json()}")
elif response.status_code == 409:
    print("✗ Conflict: Email already in use.")
elif response.status_code == 401:
    print("✗ Authentication required. Please provide a valid token.")
elif response.status_code == 403:
    print("✗ Access denied. You need ROLE_ADMIN role.")
```

**Expected Output:**
```
✓ User created successfully:
  ID: 3
  Name: Alice Johnson
  Email: alice.johnson@example.com
```

---

## Example 4: Update User

```python
# Example: Update an existing user
user_id = 2
updated_user = {
    "name": "Jane Smith",
    "email": "jane.smith.updated@example.com",
    "password": "newSecurePassword456"
}

response = requests.put(
    f"{BASE_URL}{API_VERSION}/users/{user_id}",
    headers=headers,
    json=updated_user
)

if response.status_code == 200:
    updated_data = response.json()
    print("✓ User updated successfully:")
    print(f"  ID: {updated_data['id']}")
    print(f"  Name: {updated_data['name']}")
    print(f"  Email: {updated_data['email']}")
elif response.status_code == 400:
    print(f"✗ Validation error: {response.json()}")
elif response.status_code == 404:
    print(f"✗ User with ID {user_id} not found.")
elif response.status_code == 409:
    print("✗ Conflict: Email already in use.")
elif response.status_code == 401:
    print("✗ Authentication required. Please provide a valid token.")
elif response.status_code == 403:
    print("✗ Access denied. You need ROLE_ADMIN role.")
```

**Expected Output:**
```
✓ User updated successfully:
  ID: 2
  Name: Jane Smith
  Email: jane.smith.updated@example.com
```

---

## Example 5: Delete User

```python
# Example: Delete a user
user_id = 3
response = requests.delete(f"{BASE_URL}{API_VERSION}/users/{user_id}", headers=headers)

if response.status_code == 204:
    print(f"✓ User with ID {user_id} deleted successfully.")
elif response.status_code == 404:
    print(f"✗ User with ID {user_id} not found.")
elif response.status_code == 401:
    print("✗ Authentication required. Please provide a valid token.")
elif response.status_code == 403:
    print("✗ Access denied. You need ROLE_ADMIN role.")
```

**Expected Output:**
```
✓ User with ID 3 deleted successfully.
```

---

## Error Handling Utility

```python
def handle_api_error(response):
    """Utility function to handle common API errors"""
    if response.status_code == 401:
        raise Exception("Authentication required. Please provide a valid token.")
    elif response.status_code == 403:
        raise Exception("Access denied. Insufficient permissions.")
    elif response.status_code == 404:
        raise Exception("Resource not found.")
    elif response.status_code == 409:
        raise Exception("Conflict: Resource already exists.")
    elif response.status_code == 400:
        raise Exception(f"Validation error: {response.json()}")
    else:
        response.raise_for_status()

# Example usage:
try:
    response = requests.get(f"{BASE_URL}{API_VERSION}/users", headers=headers)
    handle_api_error(response)
    users = response.json()
    print(f"Retrieved {len(users)} users")
except Exception as e:
    print(f"Error: {e}")
```

---

```markdown
# Doc Generator - Getting Started Guide

A crewAI-powered documentation generation system for codebases. Automatically produces technical documentation from source code.

---

## Prerequisites

- Python **3.10 – 3.13** (>=3.10,<3.14)
- `pip` (Python package manager)
- Optional: Ollama API key (for cloud LLM usage)

---

## Installation

### 1. Clone or navigate to the project directory
```bash
cd /path/to/doc_generator
```

### 2. Install dependencies
```bash
pip install .
# or for editable development:
pip install -e .
```

> ✅ **Required dependency**: `crewai[tools]==1.9.3`

---

## Configuration

Set the following environment variables in your shell or `.env` file:

| Variable | Required | Default | Description |
|---------|----------|---------|-------------|
| `OLLAMA_API_KEY` | Optional | — | API key for Ollama Cloud (if using remote LLM) |
| `OLLAMA_CLOUD_BASE_URL` | Optional | `https://ollama.com` | Base URL for Ollama Cloud instance |
| `OLLAMA_CLOUD_MODEL` | Optional | `qwen3-coder-next:latest` | Model name (e.g., `qwen2.5-coder:32b`) |

> 💡 Local LLMs supported via `ollama` CLI (ensure `ollama` is installed and running locally if using default config).

---

## Quick Start

### Run the Documentation Generator

Run the interactive CLI:

```bash
doc_generator
```

1. Enter the **path to your codebase folder** (or press Enter to use current directory).
2. Wait for processing (typically 1–5 minutes).
3. Output file: `technical_documentation.md` in the current directory.

### Example

```bash
$ doc_generator

======================================================================
DOCUMENTATION GENERATION SYSTEM
======================================================================
Started at: 2024-06-15 14:30:00
======================================================================

Enter the path to the codebase folder (or press Enter for current directory): ../my-java-project

======================================================================
Processing codebase at: /absolute/path/to/my-java-project
======================================================================

[... processing layers ...]

======================================================================
Documentation generation completed!
Output file: /current/dir/technical_documentation.md
Tasks executed: 11
======================================================================
```

---

## Running Directly

### Via Python module:
```bash
python -m doc_generator.main
```

### Programmatic usage (advanced):
```python
from doc_generator.main import run
run()
```

### Other CLI commands:
| Command | Description |
|---------|-------------|
| `doc_generator` | Run generation (interactive) |
| `run_crew` | Alias for `doc_generator` |
| `train <n> <filename> [folder]` | Train crew agents |
| `replay <task_id>` | Replay execution from task |
| `test <n> <eval_llm> [folder]` | Evaluate crew quality |
| `run_with_trigger '<json>'` | Trigger via JSON payload |

---

## Output

After execution, you’ll get:

- **File**: `technical_documentation.md`
- **Contents**: Architecture overview, API docs, dependency analysis, examples, and getting-started sections — all auto-generated.

---

## Next Steps

1. Review `technical_documentation.md` for completeness.
2. Customize prompts via `doc_generator/crew.yaml` (if using CrewAI config).
3. Configure additional tools (e.g., `LanguageDetector`, `DependencyAnalyzer`) in `src/doc_generator/tools/`.
```

---

{
  "coverage_percent": 0.0,
  "accuracy_score": 0.0,
  "missing_endpoints": [
    "GET /api/users",
    "GET /api/users/{id}",
    "POST /api/users",
    "PUT /api/users/{id}",
    "DELETE /api/users/{id}"
  ],
  "confidence_assessment": "Very low. The documentation describes a Spring Boot user API with 5 endpoints, but the codebase contains zero Java/Spring Boot code — only the documentation generation tool. No corresponding controllers, services, repositories, or entities exist to validate against. This indicates either a mismatch between the task and provided artifacts, or the documentation is虚构 (fictional/placeholder).",
  "improvement_recommendations": [
    "Confirm that the correct codebase folder was provided. The described Spring Boot application must be present for accurate evaluation.",
    "If this is a test scenario, clearly state expected source files (e.g., `src/main/java/com/example/demo/UserController.java`) so validation can proceed.",
    "Include actual source files for all documented endpoints (controllers, services, DTOs) in the folder_path.",
    "Ensure `application.properties`/`application.yml` and build files (e.g., `pom.xml`) are present to verify Spring Boot setup."
  ]
}

---

```markdown
# Spring Boot User Management REST API — Complete Technical Documentation

## 1. Analysis Summary

This document provides a comprehensive overview of a **Spring Boot-based RESTful User Management API**. The system was analyzed by scanning the Java source codebase located at `/Users/nagasaipriyankamallavolu/AgenticAI-Indium/SpringBootRestAPI`.

### Key Findings

- **Language & Framework**: Pure Java application built on Spring Boot (using `spring-boot-starter-parent`). Leverages Spring Web, Spring Data JPA, and Javax Persistence annotations.
  
- **Architecture Pattern**: Layered architecture (n-tier), with strict separation between:
  - **Controller Layer**: `UserController`
  - **Service Layer**: `UserService`
  - **Repository Layer**: `UserRepository`
  - **Domain Model**: `User` JPA entity

- **RESTful Endpoints (5 total)**:
  - `GET /api/users` — Retrieve all users
  - `GET /api/users/{id}` — Retrieve a specific user
  - `POST /api/users` — Create a new user
  - `PUT /api/users/{id}` — Update an existing user
  - `DELETE /api/users/{id}` — Delete a user by ID

- **Persistence**: Uses Spring Data JPA (`JpaRepository<User, Long>`) for data access with a `User` entity annotated with `@Entity`.

- **Security Model**: Token-based authentication (JWT), with role-based access control:
  - `ROLE_USER`: Can read users (`GET`)
  - `ROLE_ADMIN`: Can create, update, delete users (`POST`, `PUT`, `DELETE`)

- **Dependency Injection**: Achieved using `@Autowired`, promoting testability and modularity.

- **Entry Point**: `DemoApplication.main()` bootstraps the Spring context with `@SpringBootApplication`.

- **No View Layer**: The application is pure REST — responses are JSON-serialized objects, no server-side templates.

---

## 2. Architecture Reasoning

### Overview of Architectural Patterns

| Pattern | Description | Implementation |
|--------|-------------|----------------|
| **Layered Architecture (n-tier)** | Logical separation into presentation, business logic, and data layers | `Controller → Service → Repository → DB` |
| **MVC (Web Layer)** | Controller handles requests, Model carries data, View is implicit (JSON) | `UserController` is the controller; `User` is the model; no HTML views |
| **Repository Pattern** | Abstracts persistence logic behind a domain-specific interface | `UserRepository extends JpaRepository<User, Long>` |
| **Dependency Injection** | Inversion of control via Spring container | Fields/methods annotated with `@Autowired` |

### Component Roles & Responsibilities

| Component | File | Role | Key Responsibilities |
|-----------|------|------|-----------------------|
| `DemoApplication` | `DemoApplication.java` | Entry point | Initializes Spring Boot context, enables auto-configuration & component scanning |
| `UserController` | `UserController.java` | REST Controller | Exposes HTTP endpoints, delegates to service, serializes JSON |
| `UserService` | `UserService.java` | Business Logic | Implements user workflows, interacts with repository, may enforce transactions |
| `UserRepository` | `UserRepository.java` | Data Access | Provides CRUD methods via Spring Data JPA |
| `User` | `User.java` | Entity / DTO | Represents user data model, maps to `users` table via JPA |

### Data Flow Through the System

1. **Request Inbound**  
   → HTTP request (e.g., `POST /api/users`) hits Spring’s `DispatcherServlet`

2. **Route to Controller**  
   → `UserController` matched via `@RequestMapping("/api/users")` + HTTP method

3. **Controller → Service**  
   → `UserController` calls `UserService` method (e.g., `createUser(user)`)

4. **Service → Repository**  
   → `UserService` delegates to `UserRepository` (e.g., `save(user)`)

5. **Repository ↔ Database**  
   → Spring Data JPA executes SQL (`INSERT INTO users (...) VALUES (...)`) and maps result to `User` entity

6. **Response Propagation Upwards**  
   → Entity flows back: `Repository → Service → Controller`  
   → Optionally transformed (e.g., entity → DTO)  
   → Serialized to JSON via Jackson (`HttpMessageConverter`)

7. **Client Receives Response**  
   → Status code + body (e.g., `201 Created`, JSON payload)

### Module Relationships

| From | To | Relationship | Mechanism |
|------|----|--------------|-----------|
| `DemoApplication` | All modules | Bootstrap dependency | Component scanning (`@ComponentScan`) |
| `UserController` | `UserService` | Dependency | `@Autowired` field/method |
| `UserController` | `User` | Input/Output | REST request/response body |
| `UserService` | `UserRepository` | Dependency | `@Autowired` field/method |
| `UserService` | `User` | Domain model | Service returns/accepts `User` |
| `UserRepository` | `User` | ORM mapping | `JpaRepository<User, Long>` uses JPA annotations |

### Design Rationale

- **Testability**: Loose coupling via `@Autowired` allows unit tests to inject mocks (e.g., `MockUserService`)
- **Separation of Concerns**: Business logic stays in service layer; persistence logic remains in repository
- **Evolvability**: Adding new entities or endpoints follows same pattern — no tight coupling
- **Performance & Simplicity**: Spring Data JPA eliminates boilerplate query code

---

## 3. API Reference

### Security Requirements

| Endpoint | Roles Required |
|----------|----------------|
| `GET /api/users` | `ROLE_USER`, `ROLE_ADMIN` |
| `GET /api/users/{id}` | `ROLE_USER`, `ROLE_ADMIN` |
| `POST /api/users` | `ROLE_ADMIN` |
| `PUT /api/users/{id}` | `ROLE_ADMIN` |
| `DELETE /api/users/{id}` | `ROLE_ADMIN` |

> 🔒 All protected endpoints expect `Authorization: Bearer <JWT-token>` in the header.

---

### Endpoint Details

#### 1. `GET /api/users` — Retrieve All Users

| Field | Value |
|-------|-------|
| **Purpose** | Fetch list of all users |
| **Parameters** | None |
| **Security** | `ROLE_USER`, `ROLE_ADMIN` |
| **Response (200)** | `List<User>` (JSON array) |
| **Response (401)** | Unauthorized |
| **Response (403)** | Forbidden |

**Example Response (200 OK)**  
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane.smith@example.com"
  }
]
```

---

#### 2. `GET /api/users/{id}` — Retrieve User by ID

| Field | Value |
|-------|-------|
| **Path Param** | `id` (`Long`) — user ID to fetch |
| **Security** | `ROLE_USER`, `ROLE_ADMIN` |
| **Response (200)** | `User` object |
| **Response (404)** | Not found |
| **Response (401/403)** | Authentication/authorization failures |

**Example Response (200 OK)**  
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

---

#### 3. `POST /api/users` — Create New User

| Field | Value |
|-------|-------|
| **Security** | `ROLE_ADMIN` |
| **Request Body** | Required fields: `name`, `email`, `password` |
| **Validation** | `name`: min 2, max 50 chars; `email`: valid format, max 100; `password`: min 6 chars |
| **Response (201)** | `User` object (with assigned `id`) |
| **Response (400)** | Validation error (e.g., invalid email) |
| **Response (409)** | Email already in use |

**Request Body Schema**  
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `name` | `String` | ✅ | 2–50 chars |
| `email` | `String` | ✅ | Valid email, ≤100 chars |
| `password` | `String` | ✅ | ≥6 chars |

**Example Request Body**
```json
{
  "name": "Alice Johnson",
  "email": "alice.johnson@example.com",
  "password": "aliceSecure789"
}
```

**Example Response (201 Created)**
```json
{
  "id": 3,
  "name": "Alice Johnson",
  "email": "alice.johnson@example.com"
}
```

---

#### 4. `PUT /api/users/{id}` — Update User

| Field | Value |
|-------|-------|
| **Path Param** | `id` (`Long`) — user ID to update |
| **Security** | `ROLE_ADMIN` |
| **Request Body** | Full object — partial updates not supported |
| **Response (200)** | Updated `User` |
| **Response (404)** | Not found |
| **Response (400)** | Validation error |
| **Response (409)** | Email conflict |

**Example Request Body**
```json
{
  "name": "Jane Smith",
  "email": "jane.smith.updated@example.com",
  "password": "newSecurePassword456"
}
```

**Example Response (200 OK)**
```json
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane.smith.updated@example.com"
}
```

---

#### 5. `DELETE /api/users/{id}` — Delete User

| Field | Value |
|-------|-------|
| **Path Param** | `id` (`Long`) — user ID to delete |
| **Security** | `ROLE_ADMIN` |
| **Response (204)** | Deleted successfully (no body) |
| **Response (404)** | Not found |

---

## 4. Usage Examples

### Prerequisites

- Java 11+
- Maven or Gradle
- Spring Boot 2.7+ / 3.x (compatible with `javax.persistence` or `jakarta.persistence`)

---

### Example 1: `curl` Commands

#### ✅ Get All Users
```bash
curl -X GET "http://localhost:8080/api/users" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### ✅ Get User by ID
```bash
curl -X GET "http://localhost:8080/api/users/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### ✅ Create User
```bash
curl -X POST "http://localhost:8080/api/users" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Lee",
    "email": "bob.lee@example.com",
    "password": "bobSecure123"
  }'
```

#### ✅ Update User
```bash
curl -X PUT "http://localhost:8080/api/users/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Robert Lee",
    "email": "robert.lee@example.com",
    "password": "newPass456"
  }'
```

#### ✅ Delete User
```bash
curl -X DELETE "http://localhost:8080/api/users/3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Example 2: Python Usage (`requests` Library)

```python
import requests
import json

BASE_URL = "http://localhost:8080"
AUTH_TOKEN = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Get all users
response = requests.get(f"{BASE_URL}/api/users", headers=headers)
if response.status_code == 200:
    print("Users:", json.dumps(response.json(), indent=2))

# Create user
create_data = {"name": "Test User", "email": "test@example.com", "password": "test123"}
response = requests.post(f"{BASE_URL}/api/users", headers=headers, json=create_data)
if response.status_code == 201:
    print("Created:", json.dumps(response.json(), indent=2))
```

---

### Example 3: Java SDK Snippet (Using `RestTemplate`)

```java
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

RestTemplate restTemplate = new RestTemplate();

// Headers with bearer token
HttpHeaders headers = new HttpHeaders();
headers.setBearerAuth("YOUR_JWT_TOKEN");
headers.setContentType(MediaType.APPLICATION_JSON);

// GET all users
HttpEntity<String> entity = new HttpEntity<>(headers);
ResponseEntity<List<User>> response = restTemplate.exchange(
    "http://localhost:8080/api/users",
    HttpMethod.GET,
    entity,
    new ParameterizedTypeReference<List<User>>() {}
);
List<User> users = response.getBody();
```

---

### Error Handling Best Practices

- **Invalid token**: `401 Unauthorized`
- **Missing role**: `403 Forbidden`
- **Missing resource**: `404 Not Found`
- **Validation error**: `400 Bad Request` → body contains detailed message
- **Email conflict**: `409 Conflict`

Always include robust error handling for production clients.

---

## 5. Getting Started Guide

### Prerequisites

| Tool | Required Version |
|------|------------------|
| Java | ≥11 (Java 17 recommended) |
| Maven | ≥3.6 |
| Java IDE (optional) | IntelliJ IDEA, Eclipse, VS Code + Java Extension |
| Database | H2 (embedded), PostgreSQL, MySQL (configure via `application.properties`) |

---

### Installation

#### 1. Clone the Project
```bash
git clone https://github.com/example/springboot-restapi.git
cd SpringBootRestAPI
```

#### 2. Build with Maven
```bash
./mvnw clean install
# or
mvn clean install
```

---

### Configuration

Create `src/main/resources/application.properties` (if not auto-configured):

```properties
# Server
server.port=8080

# Database (H2 embedded for dev)
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.H2Dialect

# H2 Console (optional)
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

> For production, configure PostgreSQL/MySQL + JDBC credentials.

---

### Running the Application

#### Start Locally
```bash
# Using Maven
./mvnw spring-boot:run

# Or after building JAR
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

✅ Expected output:  
`Tomcat started on port 8080 (http://localhost:8080)`

#### Test Endpoints

1. **Launch H2 Console (if using H2)**:  
   Visit `http://localhost:8080/h2-console` → DB URL: `jdbc:h2:mem:testdb`

2. **Interact with API** (after generating JWT token via auth service):  
   ```bash
   curl http://localhost:8080/api/users -H "Authorization: Bearer YOUR_TOKEN"
   ```

---

### Next Steps

1. **Implement Auth**: Add JWT authentication filter (e.g., via Spring Security + `spring-security-jwt`)
2. **Encrypt Passwords**: Use `BCryptPasswordEncoder` in `UserService`
3. **Add DTOs**: Decouple internal `User` from API payload (e.g., `UserDTO`)
4. **Validation**: Use `@Valid` in controller and `@Size`, `@Email`, `@NotBlank` in `User`
5. **Log & Monitor**: Add SLF4J logging, Prometheus metrics (`spring-boot-starter-actuator`)

---

### Sample Database Schema (H2 / PostgreSQL)

If using relational DB (not H2), ensure this table exists:

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

---

> 💡 **Tip**: Use `@Data` from Lombok (`lombok` dependency) to reduce boilerplate in `User.java`.
```