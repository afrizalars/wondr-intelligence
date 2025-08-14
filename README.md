# Wondr Intelligence

A financial data intelligence platform that enables natural language queries over customer transaction data using hybrid search (PostgreSQL + pgvector) and LLM-powered responses.

## Features

### Core Capabilities
- **Natural Language Search**: Query financial transactions using plain English
- **Hybrid Search**: Combines vector similarity search with traditional SQL queries
- **Real-time Insights**: Sub-200ms query latency for millions of records
- **Mobile Banking UI**: Interactive playground with mobile banking mockup
- **Content Guardrails**: Configurable content filtering and transformation rules
- **Multi-tenant Ready**: Designed for horizontal scaling with CIF partitioning

### Components
- **Authentication**: JWT-based auth with user registration/login
- **Magic Search Playground**: Interactive interface for testing queries
- **Merchants Catalog**: Manage merchant information and categorization
- **Guardrails**: Configure regex/keyword-based content filtering
- **Prompt Templates**: Customize LLM response tone and style
- **API Keys**: Generate and manage API access keys
- **Search History**: Track and analyze query patterns
- **Global Knowledge**: Upload and index reference documents

## Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.8+)
- **Frontend**: React 18 with TypeScript
- **Database**: PostgreSQL with pgvector extension
- **Vector Search**: E5 multilingual embeddings (768-dim)
- **LLM**: Anthropic Claude API
- **UI Framework**: Material-UI

### Database Schema
- Unified knowledge base with per-CIF vector embeddings
- Partitioned for horizontal scaling
- ANN indexes for fast similarity search
- Separate tables for transactions, profiles, contacts, promos

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 14+ with pgvector extension
- Anthropic API key

**For macOS users**: See [SETUP_MACOS.md](SETUP_MACOS.md) for detailed setup instructions.

### Quick Setup

1. Clone the repository:
```bash
git clone <repository>
cd wondr-intelligence
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Follow the prompts to:
   - Configure database connection
   - Add your Anthropic API key
   - Generate synthetic data (optional)

4. Start the application:
```bash
./start.sh
```

### Manual Setup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
psql -U postgres -d wondr_intelligence -f ../database/schema.sql

# Generate synthetic data
python ../scripts/generate_synthetic_data.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Usage

### Default URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Default Test Account
After running synthetic data generation:
- Use any CIF from CIF00000001 to CIF00000100
- Register a new account via the UI

### Example Queries
- "Show me all my Starbucks transactions"
- "How much did I spend on food last month?"
- "What are my top 5 merchants?"
- "Show me transactions over 100,000"
- "Analyze my spending patterns"

## API Documentation

### Authentication
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me
```

### Magic Search
```http
POST /api/v1/search/magic
{
  "query": "string",
  "cif": "string",
  "include_global": true,
  "top_k": 10,
  "similarity_threshold": 0.5,
  "use_guardrails": true
}
```

### Aggregate Queries
```http
POST /api/v1/search/aggregate/{query_type}?cif=CIF00000001
```
Query types: `total_spending`, `category_breakdown`, `merchant_frequency`

## Configuration

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
ANTHROPIC_API_KEY=your-key
EMBEDDING_MODEL=intfloat/multilingual-e5-base
```

### Guardrails Configuration
Default guardrails include:
- Credit card number masking
- Personal ID filtering
- Profanity detection
- SQL injection prevention

## Performance

### Benchmarks
- Vector search: <100ms for 1M vectors
- LLM response: <2s end-to-end
- Embedding generation: ~50ms per text
- Database queries: <50ms for aggregations

### Optimization Tips
- Use partitioning for large CIF counts
- Adjust IVFFlat lists parameter for index
- Enable connection pooling
- Implement database-based session caching if needed

## Development

### Project Structure
```
wondr-intelligence/
├── backend/
│   ├── app/           # Core application
│   ├── models/        # SQLAlchemy models
│   ├── routers/       # API endpoints
│   ├── services/      # Business logic
│   └── main.py        # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── api/       # API clients
│   │   ├── pages/     # React pages
│   │   ├── layouts/   # Layout components
│   │   └── contexts/  # React contexts
│   └── package.json
├── database/
│   └── schema.sql     # Database DDL
├── scripts/
│   └── generate_synthetic_data.py
└── install.sh         # Installation script
```

### Adding New Features
1. Define database schema in `database/schema.sql`
2. Create SQLAlchemy model in `backend/models/`
3. Implement service logic in `backend/services/`
4. Add API endpoint in `backend/routers/`
5. Create React page in `frontend/src/pages/`

## Security

### Built-in Security Features
- JWT token authentication
- Password hashing with bcrypt
- API key management with SHA256
- Content guardrails and filtering
- SQL injection prevention
- CORS configuration

### Best Practices
- Never commit `.env` files
- Rotate API keys regularly
- Use HTTPS in production
- Enable rate limiting
- Monitor search history for abuse

## Troubleshooting

### Common Issues

1. **pgvector not found**
   ```bash
   # Install pgvector
   cd /tmp
   git clone https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   make install
   ```

2. **Embedding model download fails**
   ```python
   # Pre-download the model
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('intfloat/multilingual-e5-base')
   ```

3. **Database connection errors**
   - Check PostgreSQL is running
   - Verify credentials in `.env`
   - Ensure database exists

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.