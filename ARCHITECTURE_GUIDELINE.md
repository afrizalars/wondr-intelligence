# Architecture Guidelines - Wondr Intelligence

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   React     │  │   TypeScript  │  │  Material-UI  │      │
│  │   Vite      │  │   React Query │  │  Apple Theme  │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI   │  │     CORS      │  │     Auth      │      │
│  │   Pydantic  │  │   Middleware  │  │     JWT       │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   LLM       │  │  Embeddings   │  │   Search      │      │
│  │  Service    │  │   Service     │  │   Service     │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL  │  │   pgvector    │  │    Redis      │      │
│  │   Supabase  │  │  Embeddings   │  │    Cache      │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Core Architectural Principles

### 1. Separation of Concerns
- **Presentation**: UI/UX logic only
- **Business**: Core domain logic
- **Data**: Persistence and retrieval
- **Infrastructure**: Cross-cutting concerns

### 2. Scalability First
- Horizontal scaling capability
- Stateless services
- Database connection pooling
- Caching strategies
- Async processing

### 3. Security by Design
- Zero-trust architecture
- Defense in depth
- Principle of least privilege
- Encryption at rest and in transit
- Regular security audits

### 4. High Availability
- No single point of failure
- Graceful degradation
- Circuit breakers
- Health checks
- Auto-recovery

## Technology Stack

### Frontend
```yaml
Framework: React 18+
Language: TypeScript 5+
Build Tool: Vite
State Management: React Query + Context API
UI Library: Material-UI v5
Styling: Emotion + CSS-in-JS
Testing: Vitest + React Testing Library
Linting: ESLint + Prettier
```

### Backend
```yaml
Framework: FastAPI
Language: Python 3.11+
ORM: SQLAlchemy
Validation: Pydantic
Authentication: JWT (PyJWT)
Testing: Pytest
Linting: Ruff + Black
Documentation: OpenAPI/Swagger
```

### Database
```yaml
Primary: PostgreSQL 15+
Vector Store: pgvector
Cache: Redis
Search: PostgreSQL Full Text Search
Backup: Automated daily backups
Migration: Alembic
```

### Infrastructure
```yaml
Container: Docker
Orchestration: Docker Compose (dev), Kubernetes (prod)
CI/CD: GitHub Actions
Monitoring: Prometheus + Grafana
Logging: ELK Stack
APM: OpenTelemetry
```

### AI/ML
```yaml
LLM: OpenAI GPT-4
Embeddings: OpenAI text-embedding-3-small
Vector Search: pgvector
ML Framework: scikit-learn (future)
Feature Store: PostgreSQL
```

## Service Architecture

### API Design Principles

#### RESTful Conventions
```
GET    /api/v1/resources      # List
GET    /api/v1/resources/{id} # Read
POST   /api/v1/resources      # Create
PUT    /api/v1/resources/{id} # Update
DELETE /api/v1/resources/{id} # Delete
```

#### API Versioning
```
/api/v1/...  # Current stable
/api/v2/...  # Next version (breaking changes)
/api/beta/...  # Experimental features
```

#### Response Format
```json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2025-01-14T10:00:00Z",
    "version": "1.0.0",
    "request_id": "uuid"
  },
  "errors": []
}
```

### Service Layer Architecture

#### LLM Service
```python
class LLMService:
    - generate_response()
    - generate_embeddings()
    - moderate_content()
    - extract_entities()
    
Responsibilities:
- OpenAI API integration
- Prompt engineering
- Response formatting
- Token management
- Rate limiting
```

#### Search Service
```python
class SearchService:
    - vector_search()
    - hybrid_search()
    - semantic_search()
    - filter_results()
    
Responsibilities:
- Query processing
- Vector similarity
- Result ranking
- Caching
- Analytics
```

#### Auth Service
```python
class AuthService:
    - authenticate()
    - authorize()
    - refresh_token()
    - validate_permissions()
    
Responsibilities:
- JWT management
- Session handling
- Permission checks
- Password hashing
- MFA support
```

## Database Design

### Schema Design Principles
1. **Normalization**: 3NF minimum
2. **Indexes**: Strategic indexing for performance
3. **Constraints**: Foreign keys, unique, check
4. **Audit**: Created/updated timestamps
5. **Soft Delete**: Logical deletion with flags

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Transactions Table
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cif_id VARCHAR(20) NOT NULL,
    merchant_name VARCHAR(255),
    amount DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'IDR',
    category VARCHAR(100),
    transaction_date TIMESTAMP,
    description TEXT,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Search History Table
```sql
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    query TEXT NOT NULL,
    response TEXT,
    cif_id VARCHAR(20),
    latency_ms INTEGER,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Vector Search Implementation
```sql
-- Create vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add vector column
ALTER TABLE transactions 
ADD COLUMN embedding vector(1536);

-- Create index for similarity search
CREATE INDEX ON transactions 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Similarity search query
SELECT *, 1 - (embedding <=> $1) as similarity
FROM transactions
WHERE 1 - (embedding <=> $1) > 0.8
ORDER BY similarity DESC
LIMIT 10;
```

## Security Architecture

### Authentication Flow
```
1. User Login
   └── POST /auth/login
       └── Validate credentials
           └── Generate JWT token
               └── Return token + refresh token

2. API Request
   └── Authorization header
       └── Validate JWT
           └── Check permissions
               └── Process request
```

### Security Layers
1. **Network Security**
   - HTTPS only
   - Rate limiting
   - DDoS protection
   - WAF rules

2. **Application Security**
   - Input validation
   - SQL injection prevention
   - XSS protection
   - CSRF tokens

3. **Data Security**
   - Encryption at rest
   - Encryption in transit
   - PII masking
   - Audit logging

### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@example.com",
    "exp": 1234567890,
    "iat": 1234567890,
    "permissions": ["read", "write"]
  }
}
```

## Performance Optimization

### Caching Strategy

#### Cache Levels
1. **Browser Cache**: Static assets
2. **CDN Cache**: Public resources
3. **Application Cache**: Redis
4. **Database Cache**: Query results

#### Redis Cache Implementation
```python
# Cache key pattern
cache_key = f"search:{user_id}:{query_hash}"

# Cache with TTL
redis.setex(cache_key, 3600, result)

# Cache invalidation
redis.delete(f"search:{user_id}:*")
```

### Database Optimization

#### Indexing Strategy
```sql
-- Search optimization
CREATE INDEX idx_transactions_cif_date 
ON transactions(cif_id, transaction_date DESC);

-- Text search
CREATE INDEX idx_transactions_search 
ON transactions USING gin(to_tsvector('english', description));

-- JSONB queries
CREATE INDEX idx_transactions_metadata 
ON transactions USING gin(metadata);
```

#### Query Optimization
- Use prepared statements
- Batch operations
- Connection pooling
- Query plan analysis
- Partitioning for large tables

### Frontend Optimization
1. **Code Splitting**: Dynamic imports
2. **Lazy Loading**: Route-based splitting
3. **Bundle Optimization**: Tree shaking
4. **Asset Optimization**: WebP, compression
5. **Caching**: Service workers

## Monitoring & Observability

### Metrics Collection
```yaml
Application Metrics:
  - Request rate
  - Response time
  - Error rate
  - Throughput

Business Metrics:
  - Active users
  - Query volume
  - Feature usage
  - Conversion rates

Infrastructure Metrics:
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network traffic
```

### Logging Strategy
```python
# Structured logging
logger.info("search_request", {
    "user_id": user_id,
    "query": query,
    "cif": cif,
    "timestamp": datetime.utcnow(),
    "request_id": request_id
})

# Log levels
- DEBUG: Development only
- INFO: General information
- WARNING: Potential issues
- ERROR: Errors requiring attention
- CRITICAL: System failures
```

### Distributed Tracing
```python
# OpenTelemetry implementation
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("search_operation"):
    # Operation logic
    pass
```

## Deployment Architecture

### Development Environment
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    volumes: ["./frontend:/app"]
    
  backend:
    build: ./backend
    ports: ["8001:8001"]
    volumes: ["./backend:/app"]
    
  postgres:
    image: postgres:15
    ports: ["5432:5432"]
    
  redis:
    image: redis:7
    ports: ["6379:6379"]
```

### Production Environment
```yaml
Compute:
  - Auto-scaling groups
  - Load balancers
  - Health checks
  - Rolling updates

Storage:
  - Managed PostgreSQL
  - Redis cluster
  - S3 for static assets
  - Backup automation

Network:
  - VPC isolation
  - Private subnets
  - Security groups
  - CDN distribution
```

## Disaster Recovery

### Backup Strategy
1. **Database**: Daily automated backups
2. **Code**: Git repository
3. **Configuration**: Encrypted vault
4. **User Data**: Incremental backups

### Recovery Procedures
- **RPO**: 1 hour maximum data loss
- **RTO**: 2 hours maximum downtime
- **Failover**: Automatic to standby
- **Rollback**: Blue-green deployment

## Development Guidelines

### Code Organization
```
wondr-intelligence/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   └── tests/
├── backend/
│   ├── app/
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── tests/
└── infrastructure/
    ├── docker/
    ├── kubernetes/
    └── terraform/
```

### Testing Strategy
```
Unit Tests: 80% coverage minimum
Integration Tests: API endpoints
E2E Tests: Critical user flows
Performance Tests: Load testing
Security Tests: Vulnerability scanning
```

### CI/CD Pipeline
```yaml
stages:
  - lint
  - test
  - build
  - security-scan
  - deploy-staging
  - integration-tests
  - deploy-production
```

---

*Last Updated: January 2025*
*Version: 1.0*
*Owner: Engineering Team*