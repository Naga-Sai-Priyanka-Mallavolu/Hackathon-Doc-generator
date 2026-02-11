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