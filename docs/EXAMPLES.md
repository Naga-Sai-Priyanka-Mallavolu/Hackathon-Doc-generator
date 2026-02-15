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