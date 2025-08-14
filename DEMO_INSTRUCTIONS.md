# Wondr Intelligence Demo Instructions

## Quick Start

The system is now running and ready to use! Here's how to test it:

**IMPORTANT**: The backend is running on port 8001 (not 8000) to avoid port conflicts.

### 1. Access the Application
Open your browser and go to: http://localhost:5173

### 2. Register a New Account
Since authentication is required, you need to register first:

**Option A: Via Frontend**
1. Navigate to http://localhost:5173/auth/register
2. Fill in the registration form:
   - Email: your.email@example.com
   - Username: yourusername
   - Password: YourPassword123
   - Full Name: Your Name

**Option B: Via API (curl)**
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"demo@example.com\", \"username\": \"demouser\", \"password\": \"Demo123\", \"full_name\": \"Demo User\"}"
```

### 3. Login
After registration, login to get an access token:

**Via Frontend:**
1. Navigate to http://localhost:5173/auth/login
2. Enter your email and password

**Via API:**
```bash
# Note: Use the /login endpoint with JSON payload
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"demo@example.com\", \"password\": \"Demo123\"}"
```

### 4. Test the Search API

**Without Authentication (Test Endpoint):**
```bash
curl -X POST http://localhost:8001/api/v1/search/test \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Show me transactions above 1000000\", \"cif\": \"CIF001\"}"
```

**With Authentication (Real Search):**
```bash
# First get your token from login, then:
TOKEN="your_access_token_here"

curl -X POST http://localhost:8001/api/v1/search/magic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"query\": \"Show me my spending pattern\", \"cif\": \"CIF001\"}"
```

### 5. Use the Playground
Once logged in via the frontend:
1. Navigate to the Playground at http://localhost:5173/playground
2. Enter a CIF (Customer ID): e.g., "CIF001"
3. Type your query in natural language
4. Click Send to see the AI-powered response

## Test Data
The system has been populated with synthetic data including:
- 20 test customers (CIF001 - CIF020)
- Transaction data for each customer
- Sample merchants and categories
- Vector embeddings for search

## Available Features
- **Natural Language Search**: Query financial data using plain English
- **Mobile Banking Preview**: See how responses appear in a mobile app
- **Merchant Management**: Configure merchant data and categories
- **Guardrails**: Content filtering and safety controls
- **API Key Management**: Generate and manage API keys
- **Search History**: Track all queries and responses
- **Global Knowledge Base**: Upload and manage documents

## API Documentation
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc

## System Status
- Backend API: http://localhost:8001/health
- Frontend: http://localhost:5173

## Starting the Backend

To start the backend server:
```bash
cd backend
source venv/bin/activate
python run_server.py
```

The server will run on http://localhost:8001

## Troubleshooting

### Port 8000 Already in Use
The backend has been configured to run on port 8001 to avoid conflicts with other services.

### CORS Issues
CORS is already configured to allow requests from http://localhost:5173

### Authentication Issues
- The login endpoint expects email in the "username" field
- Tokens expire after 30 minutes
- Tokens are automatically included in API requests from the frontend

### Database Connection
- Default uses your system username (not 'postgres')
- Database: wondr_intelligence
- Check connection: `psql -U $(whoami) -d wondr_intelligence -c "SELECT 1"`

## Next Steps
1. Explore the different pages in the dashboard
2. Try various natural language queries
3. Upload documents to the knowledge base
4. Configure guardrails for content filtering
5. Create custom prompt templates