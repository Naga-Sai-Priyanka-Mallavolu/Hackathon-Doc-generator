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