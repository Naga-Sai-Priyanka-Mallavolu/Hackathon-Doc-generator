# REST API Examples

All endpoints use the following authentication pattern:
- **Bearer token**: `Authorization: Bearer your-token-here`
- **Content-Type**: `application/json`

---

## 1. UserRestController (`/api/users`)

### `GET /api/users`  
*List all users (ADMIN only)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/users' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json'
```

**Request body**: N/A

**Success Response** (`200 OK`)
```json
[
  {
    "id": 1,
    "username": "jdoe",
    "email": "john.doe@example.com",
    "createdAt": "2024-03-15T10:30:00Z"
  },
  {
    "id": 2,
    "username": "asmith",
    "email": "alice.smith@example.com",
    "createdAt": "2024-03-16T14:20:00Z"
  }
]
```

**Error Response** (`403 Forbidden`)
```json
{
  "errorCode": "FORBIDDEN",
  "message": "You are not authorized to access this resource",
  "status": 403
}
```

---

### `GET /api/users/{id}`  
*Retrieve a specific user (ADMIN or USER)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/users/123' \
  -H 'Authorization: Bearer your-token-here'
```

**Request body**: N/A

**Success Response** (`200 OK`)
```json
{
  "id": 123,
  "username": "bwilliams",
  "email": "brian.w@example.com",
  "createdAt": "2024-03-18T09:15:00Z"
}
```

**Error Response** (`404 Not Found`)
```json
{
  "errorCode": "USER_NOT_FOUND",
  "message": "User with ID 123 does not exist",
  "status": 404
}
```

---

### `POST /api/users`  
*Create a new user (ADMIN only)*

**Curl**
```bash
curl -X POST 'https://api.example.com/api/users' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "mjohnson",
    "email": "mike.johnson@example.com",
    "password": "SecurePass123!"
  }'
```

**Request body**
```json
{
  "username": "mjohnson",
  "email": "mike.johnson@example.com",
  "password": "SecurePass123!"
}
```

**Success Response** (`201 Created`)
```json
{
  "id": 124,
  "username": "mjohnson",
  "email": "mike.johnson@example.com",
  "createdAt": "2024-03-20T11:45:00Z"
}
```

---

### `PUT /api/users/{id}`  
*Update user by ID (ADMIN only)*

**Curl**
```bash
curl -X PUT 'https://api.example.com/api/users/124' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "mjohnson-updated",
    "email": "mike.j@example.com"
  }'
```

**Request body**
```json
{
  "username": "mjohnson-updated",
  "email": "mike.j@example.com"
}
```

**Success Response** (`200 OK`)
```json
{
  "id": 124,
  "username": "mjohnson-updated",
  "email": "mike.j@example.com",
  "createdAt": "2024-03-20T11:45:00Z"
}
```

---

### `DELETE /api/users/{id}`  
*Delete user by ID (ADMIN only)*

**Curl**
```bash
curl -X DELETE 'https://api.example.com/api/users/124' \
  -H 'Authorization: Bearer your-token-here'
```

**Request body**: N/A

**Success Response** (`204 No Content`)

**Error Response** (`404 Not Found`)
```json
{
  "errorCode": "USER_NOT_FOUND",
  "message": "User with ID 124 does not exist",
  "status": 404
}
```

---

## 2. ProductRestController (`/api/products`)

### `GET /api/products`  
*List all products (authenticated users)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/products' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
[
  {
    "id": 1,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse with 2.4GHz connection",
    "price": 29.99,
    "stock": 150,
    "createdAt": "2024-02-10T08:00:00Z"
  },
  {
    "id": 2,
    "name": "USB-C Hub",
    "description": "7-in-1 USB-C hub with HDMI and Ethernet",
    "price": 49.99,
    "stock": 75,
    "createdAt": "2024-02-15T10:30:00Z"
  }
]
```

---

### `GET /api/products/{id}`  
*Get single product (authenticated users)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/products/1' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
{
  "id": 1,
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse with 2.4GHz connection",
  "price": 29.99,
  "stock": 150,
  "createdAt": "2024-02-10T08:00:00Z"
}
```

---

### `POST /api/products`  
*Create product (ADMIN only)*

**Curl**
```bash
curl -X POST 'https://api.example.com/api/products' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Mechanical Keyboard",
    "description": "RGB backlit mechanical keyboard with cherry mx switches",
    "price": 129.99,
    "stock": 30
  }'
```

**Success Response** (`201 Created`)
```json
{
  "id": 3,
  "name": "Mechanical Keyboard",
  "description": "RGB backlit mechanical keyboard with cherry mx switches",
  "price": 129.99,
  "stock": 30,
  "createdAt": "2024-03-21T15:00:00Z"
}
```

---

### `PUT /api/products/{id}`  
*Update product (ADMIN only)*

**Curl**
```bash
curl -X PUT 'https://api.example.com/api/products/3' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Mechanical Keyboard Pro",
    "description": "Premium RGB mechanical keyboard",
    "price": 149.99,
    "stock": 40
  }'
```

**Success Response** (`200 OK`)
```json
{
  "id": 3,
  "name": "Mechanical Keyboard Pro",
  "description": "Premium RGB mechanical keyboard",
  "price": 149.99,
  "stock": 40,
  "createdAt": "2024-03-21T15:00:00Z"
}
```

---

### `DELETE /api/products/{id}`  
*Delete product (ADMIN only)*

**Curl**
```bash
curl -X DELETE 'https://api.example.com/api/products/3' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`204 No Content`)

---

### `GET /api/products/search`  
*Search products by criteria (authenticated)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/products/search?name=keyboard&minPrice=50&maxPrice=200' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
[
  {
    "id": 3,
    "name": "Mechanical Keyboard Pro",
    "description": "Premium RGB mechanical keyboard",
    "price": 149.99,
    "stock": 40,
    "createdAt": "2024-03-21T15:00:00Z"
  }
]
```

---

## 3. OrderRestController (`/api/orders`)

### `GET /api/orders`  
*List all orders (ADMIN/MERCHANT)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/orders' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
[
  {
    "id": 101,
    "userId": 1,
    "productId": 1,
    "quantity": 2,
    "totalAmount": 59.98,
    "status": "PENDING",
    "createdAt": "2024-03-20T16:45:00Z"
  }
]
```

---

### `GET /api/orders/{id}/{userId}`  
*Get specific order (ADMIN/MERCHANT/OWNER)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/orders/101/1' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
{
  "id": 101,
  "userId": 1,
  "productId": 1,
  "quantity": 2,
  "totalAmount": 59.98,
  "status": "PENDING",
  "createdAt": "2024-03-20T16:45:00Z"
}
```

---

### `POST /api/orders`  
*Create new order (USER role)*

**Curl**
```bash
curl -X POST 'https://api.example.com/api/orders' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "productId": 2,
    "quantity": 1
  }'
```

**Success Response** (`201 Created`)
```json
{
  "id": 102,
  "userId": 2,
  "productId": 2,
  "quantity": 1,
  "totalAmount": 49.99,
  "status": "PENDING",
  "createdAt": "2024-03-22T10:00:00Z"
}
```

---

### `PATCH /api/orders/{id}/status`  
*Update order status (ADMIN/MERCHANT)*

**Curl**
```bash
curl -X PATCH 'https://api.example.com/api/orders/102/status' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '"SHIPPED"'
```

**Success Response** (`200 OK`)
```json
{
  "id": 102,
  "userId": 2,
  "productId": 2,
  "quantity": 1,
  "totalAmount": 49.99,
  "status": "SHIPPED",
  "createdAt": "2024-03-22T10:00:00Z",
  "updatedAt": "2024-03-23T14:30:00Z"
}
```

---

### `DELETE /api/orders/{id}`  
*Delete order (ADMIN/MERCHANT)*

**Curl**
```bash
curl -X DELETE 'https://api.example.com/api/orders/102' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`204 No Content`)

---

## 4. AuthRestController (`/auth`)

### `POST /auth/login`  
*Authenticate and get tokens*

**Curl**
```bash
curl -X POST 'https://api.example.com/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
  }'
```

**Success Response** (`200 OK`)
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600000,
  "tokenType": "Bearer"
}
```

---

### `POST /auth/register`  
*Register new user*

**Curl**
```bash
curl -X POST 'https://api.example.com/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "newuser",
    "email": "new.user@example.com",
    "password": "SecurePass123!"
  }'
```

**Success Response** (`201 Created`)
```json
{
  "id": 5,
  "username": "newuser",
  "email": "new.user@example.com",
  "createdAt": "2024-03-22T15:20:00Z"
}
```

---

### `POST /auth/refresh`  
*Refresh access token*

**Curl**
```bash
curl -X POST 'https://api.example.com/auth/refresh' \
  -H 'Content-Type: application/json' \
  -d '{
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Success Response** (`200 OK`)
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600000,
  "tokenType": "Bearer"
}
```

---

## 5. HealthCheckController (`/actuator/health`)

### `GET /actuator/health`  
*Health status*

**Curl**
```bash
curl -X GET 'https://api.example.com/actuator/health'
```

**Success Response** (`200 OK`)
```json
{
  "status": "UP",
  "components": {
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 107374182400,
        "free": 53687091200,
        "threshold": 10485760
      }
    },
    "db": {
      "status": "UP",
      "details": {
        "database": "MySQL",
        "hello": 1
      }
    }
  }
}
```

---

## 6. CategoryRestController (`/api/categories`)

### `GET /api/categories`  
*List all categories (authenticated)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/categories' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  },
  {
    "id": 2,
    "name": "Clothing",
    "description": "Apparel and fashion items"
  }
]
```

---

### `GET /api/categories/{id}`  
*Get category by ID (authenticated)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/categories/1' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic devices and accessories"
}
```

---

### `POST /api/categories`  
*Create category (ADMIN only)*

**Curl**
```bash
curl -X POST 'https://api.example.com/api/categories' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Home & Garden",
    "description": "Household and garden items"
  }'
```

**Success Response** (`201 Created`)
```json
{
  "id": 3,
  "name": "Home & Garden",
  "description": "Household and garden items"
}
```

---

### `PUT /api/categories/{id}`  
*Update category (ADMIN only)*

**Curl**
```bash
curl -X PUT 'https://api.example.com/api/categories/3' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Home & Garden Essentials",
    "description": "Essential household and garden items"
  }'
```

**Success Response** (`200 OK`)
```json
{
  "id": 3,
  "name": "Home & Garden Essentials",
  "description": "Essential household and garden items"
}
```

---

### `DELETE /api/categories/{id}`  
*Delete category (ADMIN only)*

**Curl**
```bash
curl -X DELETE 'https://api.example.com/api/categories/3' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`204 No Content`)

---

## 7. ReviewRestController (`/api/reviews`)

### `GET /api/reviews`  
*List all reviews (authenticated)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/reviews' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
[
  {
    "id": 1,
    "productId": 1,
    "userId": 2,
    "rating": 5,
    "comment": "Excellent mouse, very comfortable!",
    "createdAt": "2024-03-18T14:20:00Z"
  }
]
```

---

### `GET /api/reviews/{id}`  
*Get review by ID (authenticated)*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/reviews/1' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
{
  "id": 1,
  "productId": 1,
  "userId": 2,
  "rating": 5,
  "comment": "Excellent mouse, very comfortable!",
  "createdAt": "2024-03-18T14:20:00Z"
}
```

---

### `POST /api/reviews`  
*Create review (USER role)*

**Curl**
```bash
curl -X POST 'https://api.example.com/api/reviews' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "productId": 2,
    "rating": 4,
    "comment": "Good hub but shipping took longer than expected"
  }'
```

**Success Response** (`201 Created`)
```json
{
  "id": 2,
  "productId": 2,
  "userId": 3,
  "rating": 4,
  "comment": "Good hub but shipping took longer than expected",
  "createdAt": "2024-03-22T16:30:00Z"
}
```

---

### `PUT /api/reviews/{id}`  
*Update review (USER role)*

**Curl**
```bash
curl -X PUT 'https://api.example.com/api/reviews/2' \
  -H 'Authorization: Bearer your-token-here' \
  -H 'Content-Type: application/json' \
  -d '{
    "productId": 2,
    "rating": 5,
    "comment": "Excellent hub! Works perfectly"
  }'
```

**Success Response** (`200 OK`)
```json
{
  "id": 2,
  "productId": 2,
  "userId": 3,
  "rating": 5,
  "comment": "Excellent hub! Works perfectly",
  "createdAt": "2024-03-22T16:30:00Z"
}
```

---

### `DELETE /api/reviews/{id}`  
*Delete review (ADMIN or owner)*

**Curl**
```bash
curl -X DELETE 'https://api.example.com/api/reviews/2' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`204 No Content`)

---

### `GET /api/reviews/by-product/{productId}`  
*Get reviews for a product*

**Curl**
```bash
curl -X GET 'https://api.example.com/api/reviews/by-product/2' \
  -H 'Authorization: Bearer your-token-here'
```

**Success Response** (`200 OK`)
```json
[
  {
    "id": 2,
    "productId": 2,
    "userId": 3,
    "rating": 5,
    "comment": "Excellent hub! Works perfectly",
    "createdAt": "2024-03-22T16:30:00Z"
  }
]
```

---