# REST API Reference

This document describes all 32 REST endpoints exposed by the API, organized by controller. The API uses Spring Boot (Java) with Spring Security for authorization.

---

## Summary Table

| Controller | Base Path | Endpoints | Auth |
|------------|-----------|-----------|------|
| `UserRestController` | `/api/users` | 5 | ADMIN, USER |
| `ProductRestController` | `/api/products` | 6 | AUTHENTICATED, ADMIN |
| `OrderRestController` | `/api/orders` | 5 | ADMIN, MERCHANT, USER, OWNER |
| `AuthRestController` | `/auth` | 3 | PUBLIC |
| `HealthCheckController` | `/actuator/health` | 1 | PUBLIC |
| `CategoryRestController` | `/api/categories` | 5 | AUTHENTICATED, ADMIN |
| `ReviewRestController` | `/api/reviews` | 6 | AUTHENTICATED, USER, ADMIN |

---

## 1. UserRestController (`/api/users`)

### `GET /api/users`  
- **Purpose**: Retrieve all users  
- **Parameters**: None  
- **Response**: `List<User>`  
- **Security**: ADMIN only  
- **Exceptions**: —  
- **Source**: `UserRestController.java:16`

### `GET /api/users/{id}`  
- **Purpose**: Retrieve a user by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `User`  
- **Security**: ADMIN or USER  
- **Exceptions**: `UserNotFoundException`  
- **Source**: `UserRestController.java:23`

### `POST /api/users`  
- **Purpose**: Create a new user  
- **Parameters**: `user` (`UserCreateRequest` in body)  
- **Response**: `User`  
- **Security**: ADMIN only  
- **Exceptions**: —  
- **Source**: `UserRestController.java:31`

### `PUT /api/users/{id}`  
- **Purpose**: Update user by ID  
- **Parameters**: `id` (path, `Long`), `user` (`UserUpdateRequest` in body)  
- **Response**: `User`  
- **Security**: ADMIN only  
- **Exceptions**: `UserNotFoundException`  
- **Source**: `UserRestController.java:39`

### `DELETE /api/users/{id}`  
- **Purpose**: Delete user by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `void`  
- **Security**: ADMIN only  
- **Exceptions**: `UserNotFoundException`  
- **Source**: `UserRestController.java:47`

---

## 2. ProductRestController (`/api/products`)

### `GET /api/products`  
- **Purpose**: Retrieve all products  
- **Parameters**: None  
- **Response**: `List<Product>`  
- **Security**: Authenticated users  
- **Exceptions**: —  
- **Source**: `ProductRestController.java:19`

### `GET /api/products/{id}`  
- **Purpose**: Retrieve a product by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `Product`  
- **Security**: Authenticated users  
- **Exceptions**: `ProductNotFoundException`  
- **Source**: `ProductRestController.java:26`

### `POST /api/products`  
- **Purpose**: Create a new product  
- **Parameters**: `product` (`ProductCreateRequest` in body)  
- **Response**: `Product`  
- **Security**: ADMIN only  
- **Exceptions**: —  
- **Source**: `ProductRestController.java:34`

### `PUT /api/products/{id}`  
- **Purpose**: Update product by ID  
- **Parameters**: `id` (path, `Long`), `product` (`ProductUpdateRequest` in body)  
- **Response**: `Product`  
- **Security**: ADMIN only  
- **Exceptions**: `ProductNotFoundException`  
- **Source**: `ProductRestController.java:42`

### `DELETE /api/products/{id}`  
- **Purpose**: Delete product by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `void`  
- **Security**: ADMIN only  
- **Exceptions**: `ProductNotFoundException`  
- **Source**: `ProductRestController.java:50`

### `GET /api/products/search`  
- **Purpose**: Search products by criteria  
- **Parameters**:  
  - `name` (query, `String`, optional)  
  - `minPrice` (query, `BigDecimal`, optional)  
  - `maxPrice` (query, `BigDecimal`, optional)  
- **Response**: `List<Product>`  
- **Security**: Authenticated users  
- **Exceptions**: —  
- **Source**: `ProductRestController.java:58`

---

## 3. OrderRestController (`/api/orders`)

### `GET /api/orders`  
- **Purpose**: Retrieve all orders  
- **Parameters**: None  
- **Response**: `List<Order>`  
- **Security**: ADMIN or MERCHANT  
- **Exceptions**: —  
- **Source**: `OrderRestController.java:16`

### `GET /api/orders/{id}/{userId}`  
- **Purpose**: Retrieve an order by ID, with owner verification  
- **Parameters**: `id` (path, `Long`), `userId` (path, `Long`)  
- **Response**: `Order`  
- **Security**: ADMIN, MERCHANT, or `principal.userId == #userId` (owner)  
- **Exceptions**: `OrderNotFoundException`  
- **Source**: `OrderRestController.java:23`

### `POST /api/orders`  
- **Purpose**: Create a new order  
- **Parameters**: `order` (`OrderCreateRequest` in body)  
- **Response**: `Order`  
- **Security**: USER role  
- **Exceptions**: —  
- **Source**: `OrderRestController.java:31`

### `PATCH /api/orders/{id}/status`  
- **Purpose**: Update order status  
- **Parameters**: `id` (path, `Long`), `status` (`String` in body; must match pattern `^(PENDING\|SHIPPED\|DELIVERED\|CANCELLED)$`)  
- **Response**: `Order`  
- **Security**: ADMIN or MERCHANT  
- **Exceptions**: `OrderNotFoundException`, `InvalidOrderStatusException`  
- **Source**: `OrderRestController.java:39`

### `DELETE /api/orders/{id}`  
- **Purpose**: Delete order by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `void`  
- **Security**: ADMIN or MERCHANT  
- **Exceptions**: `OrderNotFoundException`  
- **Source**: `OrderRestController.java:48`

---

## 4. AuthRestController (`/auth`)

### `POST /auth/login`  
- **Purpose**: Authenticate a user and return tokens  
- **Parameters**: `loginRequest` (`LoginRequest` in body)  
- **Response**: `AuthResponse`  
- **Security**: Public (`@Anonymous`)  
- **Exceptions**: `AuthenticationException`  
- **Source**: `AuthRestController.java:14`

### `POST /auth/register`  
- **Purpose**: Register a new user  
- **Parameters**: `registerRequest` (`RegisterRequest` in body)  
- **Response**: `User`  
- **Security**: Public  
- **Exceptions**: `UserAlreadyExistsException`  
- **Source**: `AuthRestController.java:22`

### `POST /auth/refresh`  
- **Purpose**: Refresh access token  
- **Parameters**: `refreshToken` (`String` in body)  
- **Response**: `AuthResponse`  
- **Security**: Public  
- **Exceptions**: `InvalidTokenException`  
- **Source**: `AuthRestController.java:30`

---

## 5. HealthCheckController (`/actuator/health`)

### `GET /actuator/health`  
- **Purpose**: Application health status (Spring Boot actuator-style)  
- **Parameters**: None  
- **Response**: `HealthStatus`  
- **Security**: Public  
- **Exceptions**: —  
- **Source**: `HealthCheckController.java:12`

---

## 6. CategoryRestController (`/api/categories`)

### `GET /api/categories`  
- **Purpose**: Retrieve all categories  
- **Parameters**: None  
- **Response**: `List<Category>`  
- **Security**: Authenticated users  
- **Exceptions**: —  
- **Source**: `CategoryRestController.java:16`

### `GET /api/categories/{id}`  
- **Purpose**: Retrieve a category by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `Category`  
- **Security**: Authenticated users  
- **Exceptions**: `CategoryNotFoundException`  
- **Source**: `CategoryRestController.java:23`

### `POST /api/categories`  
- **Purpose**: Create a new category  
- **Parameters**: `category` (`CategoryCreateRequest` in body)  
- **Response**: `Category`  
- **Security**: ADMIN only  
- **Exceptions**: —  
- **Source**: `CategoryRestController.java:31`

### `PUT /api/categories/{id}`  
- **Purpose**: Update category by ID  
- **Parameters**: `id` (path, `Long`), `category` (`CategoryUpdateRequest` in body)  
- **Response**: `Category`  
- **Security**: ADMIN only  
- **Exceptions**: `CategoryNotFoundException`  
- **Source**: `CategoryRestController.java:39`

### `DELETE /api/categories/{id}`  
- **Purpose**: Delete category by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `void`  
- **Security**: ADMIN only  
- **Exceptions**: `CategoryNotFoundException`  
- **Source**: `CategoryRestController.java:47`

---

## 7. ReviewRestController (`/api/reviews`)

### `GET /api/reviews`  
- **Purpose**: Retrieve all reviews  
- **Parameters**: None  
- **Response**: `List<Review>`  
- **Security**: Authenticated users  
- **Exceptions**: —  
- **Source**: `ReviewRestController.java:18`

### `GET /api/reviews/{id}`  
- **Purpose**: Retrieve a review by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `Review`  
- **Security**: Authenticated users  
- **Exceptions**: `ReviewNotFoundException`  
- **Source**: `ReviewRestController.java:25`

### `POST /api/reviews`  
- **Purpose**: Create a new review  
- **Parameters**: `review` (`ReviewCreateRequest` in body)  
- **Response**: `Review`  
- **Security**: USER role  
- **Exceptions**: —  
- **Source**: `ReviewRestController.java:33`

### `PUT /api/reviews/{id}`  
- **Purpose**: Update a review by ID  
- **Parameters**: `id` (path, `Long`), `review` (`ReviewUpdateRequest` in body)  
- **Response**: `Review`  
- **Security**: USER role  
- **Exceptions**: `ReviewNotFoundException`  
- **Source**: `ReviewRestController.java:41`

### `DELETE /api/reviews/{id}`  
- **Purpose**: Delete a review by ID  
- **Parameters**: `id` (path, `Long`)  
- **Response**: `void`  
- **Security**: ADMIN or owner (`principal.userId == #reviewId`)  
- **Exceptions**: `ReviewNotFoundException`  
- **Source**: `ReviewRestController.java:49`

### `GET /api/reviews/by-product/{productId}`  
- **Purpose**: Retrieve all reviews for a product  
- **Parameters**: `productId` (path, `Long`)  
- **Response**: `List<Review>`  
- **Security**: Authenticated users  
- **Exceptions**: —  
- **Source**: `ReviewRestController.java:58`

---

*Total endpoints: 32 | Controllers: 7 | Languages: Java (Spring Boot)*  
*Authentication: Spring Security with `@PreAuthorize` expressions and custom `@Anonymous`*  
*Note: All path variables are `Long` unless otherwise specified. Query params for `/api/products/search` are optional.*

---