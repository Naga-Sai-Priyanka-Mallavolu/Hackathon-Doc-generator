```

# 📚 API Gateway Documentation Suite

---

## 🚀 Getting Started Guide: API Gateway System

## 1. Project Overview

This is an **enterprise-grade, multi-module Spring Boot microservice** implementing a layered architecture with clear separation of concerns across three modules: `api-gateway`, `api-scheduling`, and `api-springbatch`.

### Core Purpose
- **REST API Gateway** (`api-gateway`): Provides HTTP endpoints for managing users, orders, products, categories, and reviews with full authentication (JWT), rate limiting, and cross-cutting concerns (logging, caching, CORS).
- **Scheduling Module** (`api-scheduling`): Manages and executes scheduled tasks using cron expressions, with task persistence and enable/disable controls.
- **Batch Processing Module** (`api-springbatch`): Implements Spring Batch for ETL tasks with custom `Reader`, `Processor`, and `Writer` components.

### Technology Stack Summary
- **Backend Framework**: Spring Boot 2.7.18
- **Language**: Java 17
- **Database**: MySQL 8.0 (JPA/Hibernate)
- **Caching**: Redis (with Spring Cache)
- **Messaging**: Apache Kafka
- **Security**: JWT authentication + Spring Security
- **Build Tool**: Maven 3.8+

---

## 2. Prerequisites

| Component | Required Version | Notes |
|-----------|------------------|-------|
| **Java** | 17 or higher | Verify with `java -version` |
| **Maven** | 3.8.8+ | Included via Maven Wrapper (`./mvnw`) |
| **MySQL** | 8.0+ | For data persistence |
| **Redis** | 6.0+ | Required for caching |
| **Kafka** | 3.0+ | Optional for messaging features |
| **Git** | Any modern version | For cloning the repository |

---

## 3. Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/example/api-gateway.git
cd api-gateway
```

### Step 2: Install Dependencies
```bash
# Use Maven Wrapper (included) or system Maven
./mvnw clean install
```
*This builds all modules and runs tests.*

### Step 3: Verify Build
```bash
./mvnw clean package
```
*Output should show `BUILD SUCCESS` with all tests passing.*

---

## 4. Configuration

### Environment Variables
Create a `.env` file from `.env.example` and update credentials:

```bash
cp .env.example .env
```

```bash
# Required variables (edit with your values):
JWT_SECRET=your-super-secret-key-min-32-chars
DB_HOST=localhost
DB_PORT=3306
DB_NAME=api_gateway
DB_USER=api_user
DB_PASSWORD=your-password-here
REDIS_HOST=localhost
REDIS_PORT=6379
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### Configuration Files

- **`src/main/resources/application.yml`**: Main configuration (database, Redis, Kafka, JWT)
- **Module-specific profiles** are supported via `SPRING_PROFILES_ACTIVE=dev` (default)

#### Key Properties (from `application.yml`):
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/api_gateway
    username: api_user
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: update
    database-platform: org.hibernate.dialect.MySQL8Dialect
  data:
    redis:
      host: localhost
      port: 6379
    kafka:
      bootstrap-servers: localhost:9092
  cache:
    type: redis

security:
  jwt:
    secret: ${JWT_SECRET}
    expiration: 3600000  # 1 hour

server:
  port: 8080
```

### Database Setup

1. **Create Database & User**
   ```sql
   CREATE DATABASE api_gateway;
   CREATE USER 'api_user'@'localhost' IDENTIFIED BY 'your-password-here';
   GRANT ALL PRIVILEGES ON api_gateway.* TO 'api_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
2. **Database Schema**
   - `ddl-auto: update` auto-creates tables (`users`, `orders`, `products`, `scheduled_tasks`, etc.)
   - Entities: `User`, `Order`, `Product`, `ScheduledTask`, `Category`, `Review`

---

## 5. Running the Application

### Starting the Main API Gateway (`api-gateway`)
```bash
# Run using Maven Wrapper
./mvnw spring-boot:run -pl api-gateway
```

**Expected Output:**
```
Started RestApiApplication in X.XXX seconds
Tomcat started on port 8080 (http://localhost:8080)
```

### ports Used by Each Module:
| Module | Port | Command |
|--------|------|---------|
| `api-gateway` | 8080 | `./mvnw spring-boot:run -pl api-gateway` |
| `api-scheduling` | 8081 | `./mvnw spring-boot:run -pl api-scheduling` |
| `api-springbatch` | 8082 | `./mvnw spring-boot:run -pl api-springbatch` |

### Health Check Endpoint
```bash
curl http://localhost:8080/actuator/health
```

---

## 6. Running Tests

### Run All Tests
```bash
./mvnw test
```

### Run Specific Test Suite
```bash
./mvnw test -Dtest=UserServiceTest
```

### Run Integration Tests
```bash
./mvnw verify -Dtest=**/*IT.java
```

> ✅ **All tests must pass before proceeding.**

---

## 7. Quick Start: First API Call

### Step 1: Register a New User
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```
✅ **Success Response:** `201 Created` with user ID and email.

### Step 2: Login to Get JWT
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```
✅ **Success Response:** `200 OK` with `accessToken`.

### Step 3: Get All Products (Authenticated)
```bash
curl -X GET http://localhost:8080/api/products \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

> 📚 Full API examples: See [`EXAMPLES.md`](EXAMPLES.md)

---

## 8. Project Structure

```
api-gateway/
├── api-gateway/                # Main REST API module (port 8080)
│   ├── src/main/java/com/example/api/
│   │   ├── RestApiApplication.java          # Entry point
│   │   ├── controller/
│   │   │   ├── UserController.java
│   │   │   ├── OrderController.java
│   │   │   ├── ProductController.java
│   │   │   └── AuthController.java
│   │   ├── service/
│   │   │   ├── UserService.java
│   │   │   ├── OrderService.java
│   │   │   └── ProductService.java
│   │   ├── repository/
│   │   │   ├── UserRepository.java
│   │   │   ├── OrderRepository.java
│   │   │   └── ProductRepository.java
│   │   └── model/
│   │       ├── User.java, Order.java, Product.java, etc.
│   └── pom.xml
│
├── api-scheduling/             # Scheduled tasks module (port 8081)
│   ├── src/main/java/com/example/scheduling/
│   │   ├── SchedulingApplication.java
│   │   ├── controller/ScheduledTaskController.java
│   │   ├── service/ScheduledTaskService.java
│   │   └── repository/ScheduledTaskRepository.java
│   └── pom.xml
│
└── api-springbatch/            # Batch processing module (port 8082)
    ├── src/main/java/com/example/batch/
    │   ├── SpringBatchApplication.java
    │   ├── reader/CustomerReader.java
    │   ├── processor/CustomerProcessor.java
    │   └── writer/CustomerWriter.java
    └── pom.xml

├── .env.example
├── pom.xml                     # Parent POM
└── README.md
```

### Key Directories
| Directory | Purpose |
|-----------|---------|
| `controller/` | REST endpoint classes (`@RestController`) |
| `service/` | Business logic (`@Service`) |
| `repository/` | JPA repositories (`@Repository`) |
| `model/` | JPA entities (`@Entity`) |
| `config/` | Spring configs (`@Configuration`) |
| `aspect/` | AOP logging/rate limiting (`@Aspect`) |
| `util/` | Transformers, response wrappers |

---

## 9. Troubleshooting

### 🔴 Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080
# Or kill all Java processes
pkill -f java
```

### 🔴 Database Connection Issues
- ✅ Ensure MySQL is running: `mysql -u api_user -p`
- ✅ Verify `.env` has correct credentials
- ✅ Check `spring.datasource.url` matches DB name

### 🔴 Redis Cache Errors
- ✅ Start Redis: `redis-server`
- ✅ Verify connection: `redis-cli ping` → `PONG`

### 🔴 Kafka Errors (Optional)
- ✅ Skip Kafka features by commenting out `@KafkaListener` classes
- ✅ Or install Kafka: `docker run -p 9092:9092 apache/kafka`

### 🔴 Build Failures
- ✅ Ensure Java 17: `java -version`
- ✅ Clear Maven cache: `rm -rf ~/.m2/repository && ./mvnw dependency:purge-local-repository`

### 🔴 JWT Validation Errors
- ✅ Ensure `JWT_SECRET` in `.env` is ≥ 32 chars
- ✅ Use same secret for token generation and validation

---

✅ **Next Steps**:  
- Explore controllers in `api-gateway/src/main/java/com/example/api/controller/`  
- Try the quick-start API calls  
- Configure production DB credentials before deployment

---

===SECTION: API_REFERENCE.md===

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

===SECTION: ARCHITECTURE.md===

# API Gateway System Architecture

## Overview

This is a **multi-module Spring Boot microservice system** implementing a layered architecture with clear separation of concerns. The system consists of three primary modules: `api-gateway` (main application), `api-scheduling`, and `api-springbatch`. It follows a **strict layered architecture** with a **MVC pattern** in the API layer, enhanced with cross-cutting concerns for security, logging, caching, and message processing.

---

## Architecture Diagram

```mermaid
classDiagram
    %% Direction and layout
    direction TB

    %% Application Entry Points
    class RestApiApplication {
        +main()
        @SpringBootApplication
        @EnableCaching
        @EnableScheduling
    }
    
    class SchedulingApplication {
        +main()
        @SpringBootApplication
    }
    
    class SpringBatchApplication {
        +main()
        @SpringBootApplication
    }

    %% Gateway Layer - Controllers
    class UserController {
        +getUser() GET /users/{id}
        +getUsers() GET /users
        +createUser() POST /users
        +updateUser() PUT /users/{id}
        +deleteUser() DELETE /users/{id}
        +getUserOrders()
        +getUserProducts()
    }
    
    class OrderController {
        +getOrder() GET /orders/{id}
        +getOrders() GET /orders
        +createOrder() POST /orders
        +updateOrder() PUT /orders/{id}
        +deleteOrder() DELETE /orders/{id}
        +cancelOrder() PATCH /orders/{id}/cancel
    }

    class ProductController {
        +getProduct() GET /products/{id}
        +getProducts() GET /products
        +createProduct() POST /products
        +updateProduct() PUT /products/{id}
        +deleteProduct() DELETE /products/{id}
        +getProductsByCategory()
    }

    %% Gateway Layer - Services
    class UserService {
        +getUserById()
        +getAllUsers()
        +createUser()
        +updateUser()
        +deleteUser()
        +validateUser()
    }
    
    class OrderService {
        +getOrderById()
        +getAllOrders()
        +createOrder()
        +updateOrder()
        +deleteOrder()
        +processOrder()
    }

    class ProductService {
        +getProductById()
        +getAllProducts()
        +createProduct()
        +updateProduct()
        +deleteProduct()
        +validateProduct()
    }

    %% Gateway Layer - Repositories
    class UserRepository {
        +findById()
        +findByEmail()
        +existsByEmail()
        +deleteByEmail()
    }

    class OrderRepository {
        +findById()
        +findByUserId()
        +findByProductId()
        +findAllByStatus()
    }

    class ProductRepository {
        +findById()
        +findByName()
        +existsByName()
        +deleteByName()
    }

    %% Models & DTOs
    class User {
        +id, username, email, password, createdAt
        @Entity
        @Table(name='users')
    }

    class Order {
        +id, userId, productId, quantity, totalAmount, status, createdAt
        @Entity
        @Table(name='orders')
    }

    class Product {
        +id, name, description, price, stock, createdAt
        @Entity
        @Table(name='products')
    }

    %% Integration Layer
    class ExternalApiGateway {
        +callExternalApi()
    }

    class InternalApiGateway {
        +callInternalApi()
    }

    class MessageQueuePublisher {
        +publish()
        @Retryable
    }

    class MessageQueueConsumer {
        +consumeMessage()
        @KafkaListener
    }

    %% Configuration
    class SecurityConfig {
        +configure(HttpSecurity)
        +passwordEncoder()
        +authenticationManager()
        @Configuration
        @EnableWebSecurity
    }

    class DatabaseConfig {
        +entityManagerFactory()
        @Configuration
        @EnableJpaRepositories
    }

    class JpaConfig {
        +hibernateProperties()
        @Configuration
    }

    class CorsConfig {
        +corsFilter()
        @Configuration
    }

    class CacheConfig {
        +cacheManager()
        @Configuration
        @EnableCaching
    }

    class RestTemplateConfig {
        +restTemplateBuilder()
        @Configuration
    }

    class WebMvcConfig {
        +addInterceptors()
        @Configuration
        @EnableWebMvc
    }

    %% Security Components
    class JwtTokenProvider {
        +generateToken()
        +validateToken()
        +getUserIdFromToken()
        +getExpiration()
        @Component
    }

    class JwtAuthenticationFilter {
        +doFilterInternal()
        @Component
        @Order(FIRST)
    }

    %% AOP & Utilities
    class LoggingAspect {
        +logMethodEntry()
        +logMethodExit()
        +logException()
        @Component
        @Aspect
    }

    class RateLimiter {
        +allowRequest()
        @Component
        @Aspect
    }

    class ResponseWrapper {
        +wrap()
        +wrapList()
        @Component
    }

    class UserTransformer {
        +toEntity()
        +toDto()
        @Component
    }

    class OrderTransformer {
        +toEntity()
        +toDto()
        @Component
    }

    class ProductTransformer {
        +toEntity()
        +toDto()
        @Component
    }

    %% Exception Handling
    class RestApiException {
        +errorCode, message, status
    }

    class RestApiExceptionHandler {
        +handleRestApiException()
        +handleException()
        +handleValidationException()
        @ControllerAdvice
    }

    %% Scheduling Module
    class ScheduledTask {
        +id, name, cron, enabled, createdAt
        @Entity
    }

    class ScheduledTaskRepository {
        +findById()
        +findByEnabled()
    }

    class ScheduledTaskService {
        +executeScheduledTask()
        @Service
        @Scheduled
    }

    class ScheduledTaskController {
        +getScheduledTasks() GET /scheduled-tasks
        +enableScheduledTask()
        +disableScheduledTask()
    }

    %% Spring Batch Components
    class CustomerReader {
        +read()
    }

    class CustomerProcessor {
        +process()
    }

    class CustomerWriter {
        +write()
    }

    %% Dependencies
    UserController --> UserService : inject
    OrderController --> OrderService : inject
    ProductController --> ProductService : inject

    UserService --> UserRepository : inject
    OrderService --> OrderRepository : inject
    ProductService --> ProductRepository : inject

    UserController --> ResponseWrapper : wrap
    OrderController --> ResponseWrapper : wrap
    ProductController --> ResponseWrapper : wrap

    JwtAuthenticationFilter ..> SecurityConfig : config
    JwtTokenProvider --> SecurityConfig : inject
    UserService --> JwtTokenProvider : inject
    UserService --> JwtAuthenticationFilter : depend

    ExternalApiGateway --> InternalApiGateway : may call
    MessageQueuePublisher ..> ExternalApiGateway : publish async

    LoggingAspect .->.* : aspect weaving
    RateLimiter .->.* : aspect weaving

    ScheduledTaskController --> ScheduledTaskService : inject
    ScheduledTaskService --> ScheduledTaskRepository : inject

    CustomerReader .->.* : batch item read
    CustomerProcessor .->.* : batch item process
    CustomerWriter .->.* : batch item write

    %% External Systems
    class "MySQL Database" as DB
    class "Kafka" as Kafka
    class "Redis Cache" as Redis
    class "External APIs" as ExternalAPI

    UserRepository --o DB : JPA/Hibernate
    OrderRepository --o DB : JPA/Hibernate
    ProductRepository --o DB : JPA/Hibernate
    ScheduledTaskRepository --o DB : JPA/Hibernate

    MessageQueuePublisher --> Kafka : publish
    MessageQueueConsumer --> Kafka : subscribe

    CacheConfig --> Redis : cache storage
```

---

## Architecture Narrative

### 1. Architectural Pattern

This system implements a **Layered (n-tier) Architecture** with clear separation of concerns:

- **Presentation Layer** (`*Controller` classes)
- **Business Logic Layer** (`*Service` classes)
- **Data Access Layer** (`*Repository` interfaces)
- **Integration Layer** (external/internal API clients, message queues)
- **Configuration & Cross-Cutting Concerns** (security, logging, caching, AOP)

The presentation layer follows the **MVC pattern**, where controllers delegate to services, and services coordinate repositories. A **hexagonal architecture influence** is evident in the integration layer abstraction (e.g., `ExternalApiGateway`, `InternalApiGateway`).

### 2. Component Roles

#### Presentation Layer (`*Controller`)
- HTTP request entry points (`@RestController`)
- Request routing, validation, and response wrapping
- Examples: `UserController`, `OrderController`, `ProductController`

#### Business Logic Layer (`*Service`)
- Core domain logic and orchestration
- Transaction boundaries (implied via `@Transactional`)
- Utilizes repositories and transformers
- Examples: `UserService`, `OrderService`, `ProductService`

#### Data Access Layer (`*Repository`)
- JPA repository interfaces extending `JpaRepository`
- Repository methods for common queries (`findById`, `findByXxx`)
- Examples: `UserRepository`, `OrderRepository`, `ProductRepository`

#### Domain Models (`*`)
- JPA entities (`@Entity`)
- Mapped to database tables (`@Table`)
- Include lifecycle callbacks via `@EntityListeners`
- Examples: `User`, `Order`, `Product`, `ScheduledTask`

#### Integration Layer
- `ExternalApiGateway`: REST client for external system calls (`RestTemplate`)
- `InternalApiGateway`: REST client for internal service-to-service calls
- `MessageQueuePublisher`/`MessageQueueConsumer`: Kafka integration for async messaging
- Kafka consumer uses `@KafkaListener`, publisher uses `@Retryable`

#### Configuration Layer
- Module-specific configurations (`@Configuration`)
- Database setup (`DatabaseConfig`, `JpaConfig`)
- Security (`SecurityConfig`)
- Web (`WebMvcConfig`, `CorsConfig`)
- Caching (`CacheConfig` using Redis)
- REST client (`RestTemplateConfig`)

#### Security & AOP Layer
- `SecurityConfig`: Spring Security setup with JWT-based authentication
- `JwtTokenProvider`: JWT generation and validation
- `JwtAuthenticationFilter`: HTTP request filter for JWT extraction and validation
- `LoggingAspect`: Method entry/exit/exception logging via AOP
- `RateLimiter`: Rate limiting via AOP

#### Transformer Layer
- `*Transformer` classes convert between DTOs and entities
- Examples: `UserTransformer`, `OrderTransformer`, `ProductTransformer`

#### Exception Handling Layer
- `RestApiException`: Custom exception for application errors
- `RestApiExceptionHandler` (`@ControllerAdvice`): Global exception handler

#### Utility Layer
- `ResponseWrapper`: Standardizes API response format
- `RateLimiter`: Utility for rate limiting logic
- Custom interceptors (e.g., `CustomRetryInterceptor`)

#### Scheduling Module (`api-scheduling`)
- Dedicated to scheduled batch operations
- `@Scheduled` tasks with cron configuration
- `ScheduledTask` entity for task persistence
- Module includes its own repository, service, and controller

#### Batch Processing Module (`api-springbatch`)
- Spring Batch implementation for ETL tasks
- Custom `CustomerReader`, `CustomerProcessor`, `CustomerWriter`
- Designed for large data processing jobs

### 3. Data Flow (Request to Response)

1. **HTTP Request** → `*Controller` (e.g., `GET /users/1` → `UserController.getUser()`)
2. **Controller** validates input and calls `UserService.getUserById(id)`
3. **Service** calls `UserRepository.findById(id)`
4. **Repository** executes JPA query → **MySQL Database**
5. **Result** → entity → `UserTransformer.toDto()`
6. **Service** performs business logic, optionally calls `JwtTokenProvider`
7. **Controller** wraps response with `ResponseWrapper.wrap()`
8. **Response** sent with standardized format

Cross-cutting concerns applied via AOP and filters:
- `JwtAuthenticationFilter` intercepts before request reaches controller
- `LoggingAspect` logs method entry/exit
- `RateLimiter` enforces request rate limits
- `RestApiExceptionHandler` handles exceptions globally

### 4. External Integrations

| Integration | Component | Technology | Purpose |
|-------------|-----------|------------|---------|
| **MySQL** | `DatabaseConfig`, `JpaConfig` | Spring Data JPA / Hibernate | Primary data persistence |
| **Redis** | `CacheConfig` | Spring Cache / Lettuce | Caching layer |
| **Kafka** | `MessageQueuePublisher`, `MessageQueueConsumer` | Spring Kafka | Async messaging and event-driven architecture |
| **External APIs** | `ExternalApiGateway` | `RestTemplate` | Integrate with 3rd-party services |
| **Internal Services** | `InternalApiGateway` | `RestTemplate` | Service-to-service communication |

### 5. Security Architecture

- **Authentication**: JWT-based
  - `JwtTokenProvider` generates and validates tokens
  - `JwtAuthenticationFilter` extracts and validates JWT from `Authorization: Bearer` header
  - Credentials and tokens stored/configured in `application.yml`

- **Authorization**:
  - Secured via Spring Security (`SecurityConfig`)
  - Password encoding via BCrypt (via `passwordEncoder()` bean)
  - `@PreAuthorize`, `@Secured` annotations implied (not visible but standard)

- **CORS**:
  - Configured in `CorsConfig`
  - Allows cross-origin requests per environment

- **Rate Limiting**:
  - `RateLimiter` component with AOP advice
  - Configurable limits per endpoint or user

- **Security Properties** (from `application.yml`):
  ```yaml
  security:
    jwt:
      secret: env:JWT_SECRET
      expiration: 3600000  # 1 hour
  ```

### 6. Design Patterns Observed

- **Layered Architecture**: Clear layer separation (Controller → Service → Repository)
- **DTO/Entity Pattern**: Separation between domain models (`User`) and DTOs via `Transformer`
- **Gateway Pattern**: `ExternalApiGateway`, `InternalApiGateway` abstract HTTP calls
- **Aspect-Oriented Programming (AOP)**: Logging, rate limiting via `@Aspect` components
- **Template Method**: Spring Batch `ItemReader`, `ItemProcessor`, `ItemWriter`
- **Observer Pattern**: Kafka `@KafkaListener` subscribers
- **Factory Pattern**: `JwtTokenProvider`, `ResponseWrapper`
- **Strategy Pattern**: Multiple transformer implementations
- **Retry Pattern**: `@Retryable` on message queue publisher

### 7. Data Persistence Strategy

- **ORM**: Hibernate via Spring Data JPA
- **DDL Auto**: `update` (for dev environments)
- **SQL Dialect**: MySQL 8
- **Database URL**: `jdbc:mysql://db:3306/api_gateway`
- **Entities**:
  - `User`: table = `users`
  - `Order`: table = `orders`
  - `Product`: table = `products`
  - `ScheduledTask`: table = `scheduled_tasks`
- **Entity Lifecycle**: `@EntityListeners` → `EntityListener` for `prePersist`, `preUpdate`

### 8. Build & Dependencies

- **Build Tool**: Maven
- **Modules**:
  - `api-gateway` (main app, 17 source files)
  - `api-scheduling` (scheduled tasks, 5 files)
  - `api-springbatch` (batch processing, 4 files)
- **Key Dependencies** (from `pom.xml`):
  - Spring Boot: 2.7.18
  - Spring Security: 2.7.18
  - Spring Data JPA: 2.7.18
  - Spring Kafka: 2.9.11
  - Spring Batch: 2.7.18
  - JWT (jjwt): 0.11.5
  - Redis (caching), MySQL Connector: 8.0.33

### 9. Application Entry Points

| Entry Point | Module | Purpose |
|-------------|--------|---------|
| `RestApiApplication.java` | api-gateway | Main HTTP API gateway (port 8080) |
| `SchedulingApplication.java` | api-scheduling | Task scheduling runner |
| `SpringBatchApplication.java` | api-springbatch | Batch job runner |

---

## Summary

The system is a **well-structured, enterprise-grade Spring Boot microservice** with layered architecture and clean separation between concerns. It supports REST APIs, scheduled tasks, and batch processing, integrated with MySQL, Redis, and Kafka. Security is implemented via JWT, with additional protections like rate limiting, CORS, and global exception handling. All layers are comprehensively implemented with clear responsibility and dependency flow.

---

===SECTION: EXAMPLES.md===

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

===SECTION: architecture.mermaid===

classDiagram
    %% Direction and layout
    direction TB

    %% Application Entry Points
    class RestApiApplication {
        +main()
        @SpringBootApplication
        @EnableCaching
        @EnableScheduling
    }
    
    class SchedulingApplication {
        +main()
        @SpringBootApplication
    }
    
    class SpringBatchApplication {
        +main()
        @SpringBootApplication
    }

    %% Gateway Layer - Controllers
    class UserController {
        +getUser() GET /users/{id}
        +getUsers() GET /users
        +createUser() POST /users
        +updateUser() PUT /users/{id}
        +deleteUser() DELETE /users/{id}
        +getUserOrders()
        +getUserProducts()
    }
    
    class OrderController {
        +getOrder() GET /orders/{id}
        +getOrders() GET /orders
        +createOrder() POST /orders
        +updateOrder() PUT /orders/{id}
        +deleteOrder() DELETE /orders/{id}
        +cancelOrder() PATCH /orders/{id}/cancel
    }

    class ProductController {
        +getProduct() GET /products/{id}
        +getProducts() GET /products
        +createProduct() POST /products
        +updateProduct() PUT /products/{id}
        +deleteProduct() DELETE /products/{id}
        +getProductsByCategory()
    }

    %% Gateway Layer - Services
    class UserService {
        +getUserById()
        +getAllUsers()
        +createUser()
        +updateUser()
        +deleteUser()
        +validateUser()
    }
    
    class OrderService {
        +getOrderById()
        +getAllOrders()
        +createOrder()
        +updateOrder()
        +deleteOrder()
        +processOrder()
    }

    class ProductService {
        +getProductById()
        +getAllProducts()
        +createProduct()
        +updateProduct()
        +deleteProduct()
        +validateProduct()
    }

    %% Gateway Layer - Repositories
    class UserRepository {
        +findById()
        +findByEmail()
        +existsByEmail()
        +deleteByEmail()
    }

    class OrderRepository {
        +findById()
        +findByUserId()
        +findByProductId()
        +findAllByStatus()
    }

    class ProductRepository {
        +findById()
        +findByName()
        +existsByName()
        +deleteByName()
    }

    %% Models & DTOs
    class User {
        +id, username, email, password, createdAt
        @Entity
        @Table(name='users')
    }

    class Order {
        +id, userId, productId, quantity, totalAmount, status, createdAt
        @Entity
        @Table(name='orders')
    }

    class Product {
        +id, name, description, price, stock, createdAt
        @Entity
        @Table(name='products')
    }

    %% Integration Layer
    class ExternalApiGateway {
        +callExternalApi()
    }

    class InternalApiGateway {
        +callInternalApi()
    }

    class MessageQueuePublisher {
        +publish()
        @Retryable
    }

    class MessageQueueConsumer {
        +consumeMessage()
        @KafkaListener
    }

    %% Configuration
    class SecurityConfig {
        +configure(HttpSecurity)
        +passwordEncoder()
        +authenticationManager()
        @Configuration
        @EnableWebSecurity
    }

    class DatabaseConfig {
        +entityManagerFactory()
        @Configuration
        @EnableJpaRepositories
    }

    class JpaConfig {
        +hibernateProperties()
        @Configuration
    }

    class CorsConfig {
        +corsFilter()
        @Configuration
    }

    class CacheConfig {
        +cacheManager()
        @Configuration
        @EnableCaching
    }

    class RestTemplateConfig {
        +restTemplateBuilder()
        @Configuration
    }

    class WebMvcConfig {
        +addInterceptors()
        @Configuration
        @EnableWebMvc
    }

    %% Security Components
    class JwtTokenProvider {
        +generateToken()
        +validateToken()
        +getUserIdFromToken()
        +getExpiration()
        @Component
    }

    class JwtAuthenticationFilter {
        +doFilterInternal()
        @Component
        @Order(FIRST)
    }

    %% AOP & Utilities
    class LoggingAspect {
        +logMethodEntry()
        +logMethodExit()
        +logException()
        @Component
        @Aspect
    }

    class RateLimiter {
        +allowRequest()
        @Component
        @Aspect
    }

    class ResponseWrapper {
        +wrap()
        +wrapList()
        @Component
    }

    class UserTransformer {
        +toEntity()
        +toDto()
        @Component
    }

    class OrderTransformer {
        +toEntity()
        +toDto()
        @Component
    }

    class ProductTransformer {
        +toEntity()
        +toDto()
        @Component
    }

    %% Exception Handling
    class RestApiException {
        +errorCode, message, status
    }

    class RestApiExceptionHandler {
        +handleRestApiException()
        +handleException()
        +handleValidationException()
        @ControllerAdvice
    }

    %% Scheduling Module
    class ScheduledTask {
        +id, name, cron, enabled, createdAt
        @Entity
    }

    class ScheduledTaskRepository {
        +findById()
        +findByEnabled()
    }

    class ScheduledTaskService {
        +executeScheduledTask()
        @Service
        @Scheduled
    }

    class ScheduledTaskController {
        +getScheduledTasks() GET /scheduled-tasks
        +enableScheduledTask()
        +disableScheduledTask()
    }

    %% Spring Batch Components
    class CustomerReader {
        +read()
    }

    class CustomerProcessor {
        +process()
    }

    class CustomerWriter {
        +write()
    }

    %% Dependencies
    UserController --> UserService : inject
    OrderController --> OrderService : inject
    ProductController --> ProductService : inject

    UserService --> UserRepository : inject
    OrderService --> OrderRepository : inject
    ProductService --> ProductRepository : inject

    UserController --> ResponseWrapper : wrap
    OrderController --> ResponseWrapper : wrap
    ProductController --> ResponseWrapper : wrap

    JwtAuthenticationFilter ..> SecurityConfig : config
    JwtTokenProvider --> SecurityConfig : inject
    UserService --> JwtTokenProvider : inject
    UserService --> JwtAuthenticationFilter : depend

    ExternalApiGateway --> InternalApiGateway : may call
    MessageQueuePublisher ..> ExternalApiGateway : publish async

    LoggingAspect .->.* : aspect weaving
    RateLimiter .->.* : aspect weaving

    ScheduledTaskController --> ScheduledTaskService : inject
    ScheduledTaskService --> ScheduledTaskRepository : inject

    CustomerReader .->.* : batch item read
    CustomerProcessor .->.* : batch item process
    CustomerWriter .->.* : batch item write

    %% External Systems
    class "MySQL Database" as DB
    class "Kafka" as Kafka
    class "Redis Cache" as Redis
    class "External APIs" as ExternalAPI

    UserRepository --o DB : JPA/Hibernate
    OrderRepository --o DB : JPA/Hibernate
    ProductRepository --o DB : JPA/Hibernate
    ScheduledTaskRepository --o DB : JPA/Hibernate

    MessageQueuePublisher --> Kafka : publish
    MessageQueueConsumer --> Kafka : subscribe

    CacheConfig --> Redis : cache storage