# Migration to Multi-Agent Search System

## Overview
The search API has been successfully updated to use the new multi-agent system, replacing the old vector search and embeddings-based approach.

## Changes Made

### 1. Updated `/routers/search.py`

#### New Imports
- Added: `from services.brain_service import brain_service`
- Added: `from services.reasoning_service import reasoning_service`
- Commented out: `from services.search import search_service` (kept for reference)

#### Updated Response Model
Added new fields to `SearchResponse`:
- `agent_activity`: List of `AgentActivity` objects showing which agents ran
- `response_type`: String indicating the type of response (e.g., "transaction_summary", "customer_profile")
- `data_sources`: List of agent names that provided data

New `AgentActivity` model includes:
- `agent_name`: Name of the agent
- `handled`: Whether the agent handled the query
- `execution_time_ms`: Execution time in milliseconds
- `result_type`: Type of result returned
- `result_count`: Number of results
- `error`: Error message if agent failed

#### Updated `/api/v1/search/magic` Endpoint
The endpoint now follows this flow:
1. **Brain Service**: Parses query and routes to appropriate agents
2. **Reasoning Service**: Synthesizes results from multiple agents
3. **LLM Service**: Generates final response with synthesized context
4. **Response**: Returns answer with agent activity information

Key changes:
- Replaced `search_service.hybrid_search()` with `brain_service.execute_query()`
- Added `reasoning_service.synthesize_results()` for multi-agent result synthesis
- Extracts and returns agent activity information
- Properly handles transaction data from agent results

#### Updated `/api/v1/search/aggregate/{query_type}` Endpoint
- Now uses the multi-agent system instead of direct search service
- Maps query types to natural language queries for the brain service
- Returns agent activity information

### 2. Updated `/services/llm.py`

#### Enhanced Context Handling
- `generate_response()` now accepts both:
  - `List[Dict[str, Any]]` for legacy vector search (backward compatible)
  - `str` for new agent system (pre-formatted by reasoning service)
- Automatically detects context type and handles accordingly

#### Type Updates
- Added `Union` type import
- Updated context parameter type to `Union[List[Dict[str, Any]], str]`

## API Response Format

### New Response Structure
```json
{
  "query": "user query",
  "cif": "customer_id",
  "answer": "LLM-generated answer",
  "citations": [],
  "transactions": [...],  // If applicable
  "latency_ms": 250,
  "model_used": "claude-3-haiku-20240307",
  "guardrail_status": {...},
  "agent_activity": [
    {
      "agent_name": "transactions",
      "handled": true,
      "execution_time_ms": 45,
      "result_type": "aggregation",
      "result_count": 15,
      "error": null
    },
    {
      "agent_name": "customers",
      "handled": false,
      "execution_time_ms": null,
      "result_type": null,
      "result_count": null,
      "error": "No customer data found"
    }
  ],
  "response_type": "spending_analysis",
  "data_sources": ["transactions"]
}
```

## Benefits of the New System

1. **Multi-Source Intelligence**: Can combine data from transactions, customers, and contacts
2. **Smart Routing**: Brain service intelligently routes queries to relevant agents
3. **Parallel Processing**: Agents run in parallel for faster responses
4. **Better Context**: Reasoning service synthesizes results for more coherent responses
5. **Transparency**: Shows which agents contributed to the answer
6. **Extensibility**: Easy to add new agents without changing the API

## Testing

A test script has been created at `test_new_search_api.py` that tests:
- Various query types (transactions, profile, contacts, multi-agent)
- Agent activity tracking
- Aggregate endpoints
- Response formatting

## Backward Compatibility

- The LLM service maintains backward compatibility with list-based contexts
- Test endpoint remains unchanged
- Search history tracking continues to work

## Next Steps

1. Test the new endpoints with real data
2. Monitor agent performance and latency
3. Fine-tune agent routing logic in brain service
4. Add more specialized agents as needed
5. Optimize reasoning service synthesis logic

## Files Modified

- `/routers/search.py` - Main search router
- `/services/llm.py` - LLM service for context handling
- Created: `test_new_search_api.py` - Test script
- Created: `MIGRATION_TO_AGENTS.md` - This documentation