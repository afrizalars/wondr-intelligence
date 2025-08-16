from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.database import get_async_db
# Commented out old search service
# from services.search import search_service
from services.brain_service import brain_service
from services.reasoning_service import reasoning_service
from services.llm import llm_service
from services.guardrails import guardrail_service
from routers.auth import get_current_user
from models.user import User
from sqlalchemy import select, insert
from sqlalchemy.sql import text
from utils.simple_logger import get_flow_logger

# Initialize flow logger
flow_logger = get_flow_logger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    cif: str
    include_global: bool = True
    top_k: int = 10
    similarity_threshold: float = 0.5
    use_guardrails: bool = True
    prompt_template: Optional[str] = None

class AgentActivity(BaseModel):
    agent_name: str
    handled: bool
    execution_time_ms: Optional[int] = None
    result_type: Optional[str] = None
    result_count: Optional[int] = None
    error: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    cif: str
    answer: str
    citations: List[Dict[str, Any]]
    transactions: Optional[List[Dict[str, Any]]] = None
    latency_ms: int
    model_used: str
    guardrail_status: Optional[Dict[str, Any]] = None
    agent_activity: Optional[List[AgentActivity]] = None
    response_type: Optional[str] = None
    data_sources: Optional[List[str]] = None

# Test endpoint without authentication
@router.post("/test", response_model=SearchResponse)
async def test_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Test endpoint that doesn't require authentication"""
    # For testing, return a mock response
    return SearchResponse(
        query=request.query,
        cif=request.cif,
        answer=f"This is a test response for query: '{request.query}' for CIF: {request.cif}. The actual search service would process this with vector search and LLM.",
        citations=[
            {
                "source": "test_doc",
                "title": "Test Document",
                "text_snippet": "This is a test citation.",
                "similarity_score": 0.95
            }
        ],
        latency_ms=50,
        model_used="test_model",
        guardrail_status=None
    )

@router.post("/magic", response_model=SearchResponse)
async def magic_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Start logging the request flow
    flow_logger.start_request(request_id, request.query, request.cif)
    
    try:
        # Check guardrails on input
        guardrail_result = None
        processed_query = request.query
        
        if request.use_guardrails:
            flow_logger.log_step("Checking input guardrails...")
            guardrail_result = await guardrail_service.check_input(request.query, db)
            
            if guardrail_result["action"] == "block":
                flow_logger.log_step(f"✗ Query blocked: {guardrail_result.get('message')}")
                flow_logger.end_request("BLOCKED")
                raise HTTPException(
                    status_code=400,
                    detail=guardrail_result.get("message", "Query blocked by guardrails")
                )
            elif guardrail_result["action"] == "transform":
                processed_query = guardrail_result.get("transformed_text", request.query)
                flow_logger.log_step(f"Query transformed: '{processed_query}'")
        
        # Step 1: Use brain service to parse and route query to agents
        flow_logger.log_step("Brain service parsing query...")
        agent_results = await brain_service.execute_query(
            db=db,
            query=processed_query,
            cif=request.cif
        )
        
        # Log active agents
        for agent in agent_results.get("active_agents", []):
            flow_logger.log_agent_activation(agent, agent_results.get("context", {}))
        
        # Log agent results
        for result in agent_results.get("results", []):
            if result.get("handled"):
                count = result.get("results", {}).get("count", 0) if "results" in result else 0
                flow_logger.log_agent_result(
                    result.get("agent", "unknown"),
                    result.get("execution_time_ms", 0),
                    count
                )
        
        # Log failed agents
        for failed in agent_results.get("failed_agents", []):
            flow_logger.log_agent_error(
                failed.get("agent", "unknown"),
                failed.get("error", "Unknown error")
            )
        
        # Step 2: Use reasoning service to synthesize results
        flow_logger.log_step("Reasoning service synthesizing results...")
        synthesized_results = reasoning_service.synthesize_results(agent_results)
        
        # Log reasoning insights
        flow_logger.log_reasoning(
            synthesized_results.get("response_type", "unknown"),
            len(synthesized_results.get("sources", []))
        )
        
        # Step 3: Prepare LLM context from synthesized results
        flow_logger.log_step("Formatting context for LLM...")
        llm_context = reasoning_service.format_for_llm(synthesized_results)
        
        # Step 4: Generate LLM response with the synthesized context
        flow_logger.log_llm_call("claude-3-haiku")
        llm_response = await llm_service.generate_response(
            query=processed_query,
            context=llm_context,
            prompt_template=request.prompt_template
        )
        
        flow_logger.log_step(f"LLM response generated ({llm_response.get('tokens_used', 0)} tokens)")
        
        # Check guardrails on output
        if request.use_guardrails:
            flow_logger.log_step("Checking output guardrails...")
            output_check = await guardrail_service.check_output(llm_response["answer"], db)
            if output_check["action"] == "block":
                llm_response["answer"] = "Response blocked by content policy."
                flow_logger.log_step("✗ Response blocked by guardrails")
            elif output_check["action"] == "transform":
                llm_response["answer"] = output_check.get("transformed_text", llm_response["answer"])
                flow_logger.log_step("Response transformed by guardrails")
        
        # Extract agent activity information
        agent_activity = []
        for result in agent_results.get("results", []):
            agent_activity.append(AgentActivity(
                agent_name=result.get("agent", "unknown"),
                handled=result.get("handled", False),
                execution_time_ms=result.get("execution_time_ms"),
                result_type=result.get("results", {}).get("type") if "results" in result else None,
                result_count=result.get("results", {}).get("count") if "results" in result else None,
                error=None
            ))
        
        # Add failed agents to activity
        for failed in agent_results.get("failed_agents", []):
            agent_activity.append(AgentActivity(
                agent_name=failed.get("agent", "unknown"),
                handled=False,
                execution_time_ms=None,
                result_type=None,
                result_count=None,
                error=failed.get("error")
            ))
        
        # Extract data sources
        data_sources = list(set(
            result.get("agent") 
            for result in agent_results.get("results", [])
            if result.get("handled")
        ))
        
        # Extract transactions from agent results if available
        transactions = None
        if synthesized_results.get("data"):
            data = synthesized_results["data"]
            
            # Check if transactions data is available from agents
            if isinstance(data, dict):
                # Direct transaction data
                if "transactions" in data and isinstance(data["transactions"], dict):
                    trans_data = data["transactions"]
                    if "transactions" in trans_data:
                        transactions = trans_data["transactions"]
                # Multi-source data with transactions
                elif "transactions" in data and "transactions" in data["transactions"]:
                    transactions = data["transactions"]["transactions"]
                
                # Format transactions for response if found
                if transactions and isinstance(transactions, list):
                    # Ensure proper formatting
                    formatted_transactions = []
                    for trans in transactions[:10]:  # Limit to 10 for response
                        formatted_transactions.append({
                            "merchant": trans.get("merchant_name", trans.get("merchant", "Unknown")),
                            "amount": trans.get("amount", 0),
                            "date": trans.get("transaction_date", trans.get("date", "")),
                            "category": trans.get("category", ""),
                            "title": trans.get("description", ""),
                            "text": trans.get("description", "")
                        })
                    transactions = formatted_transactions
    
        # Calculate total latency
        total_latency = (
            agent_results.get("total_execution_time_ms", 0) + 
            synthesized_results.get("metadata", {}).get("synthesis_time_ms", 0) +
            llm_response.get("latency_ms", 0)
        )
        
        # Log performance metrics
        flow_logger.log_step(f"⚡ Total processing time: {total_latency}ms")
        flow_logger.log_step(f"  - Agents: {agent_results.get('total_execution_time_ms', 0)}ms")
        flow_logger.log_step(f"  - Reasoning: {synthesized_results.get('metadata', {}).get('synthesis_time_ms', 0)}ms")
        flow_logger.log_step(f"  - LLM: {llm_response.get('latency_ms', 0)}ms")
        
        # Save to search history
        flow_logger.log_step("Saving to search history...")
        await _save_search_history(
            db=db,
            user_id=current_user.id,
            cif=request.cif,
            query=request.query,
            response=llm_response["answer"],
            model_used=llm_response.get("model"),
            latency_ms=total_latency,
            top_similarity_score=0.0,  # Not applicable with agent system
            retrieved_count=sum(
                result.get("results", {}).get("count", 0) 
                for result in agent_results.get("results", [])
                if "results" in result and "count" in result.get("results", {})
            ),
            tokens_used=llm_response.get("tokens_used", 0)
        )
        
        # Prepare response
        response = SearchResponse(
            query=request.query,
            cif=request.cif,
            answer=llm_response["answer"],
            citations=llm_response.get("citations", []),
            transactions=transactions,
            latency_ms=total_latency,
            model_used=llm_response.get("model", "unknown"),
            guardrail_status=guardrail_result,
            agent_activity=agent_activity,
            response_type=synthesized_results.get("response_type"),
            data_sources=data_sources
        )
        
        # Log successful completion
        flow_logger.end_request("SUCCESS", total_latency)
        
        return response
        
    except Exception as e:
        # Log error and end request
        flow_logger.log_step(f"✗ Error: {str(e)}")
        flow_logger.end_request("ERROR")
        raise

@router.get("/history")
async def get_search_history(
    cif: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    query = text("""
        SELECT 
            id,
            cif,
            query,
            response,
            model_used,
            latency_ms,
            top_similarity_score,
            retrieved_count,
            tokens_used,
            created_at
        FROM search_history
        WHERE user_id = :user_id
        """ + (" AND cif = :cif" if cif else "") + """
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    
    params = {"user_id": current_user.id, "limit": limit, "offset": offset}
    if cif:
        params["cif"] = cif
    
    result = await db.execute(query, params)
    rows = result.fetchall()
    
    return {
        "history": [
            {
                "id": str(row.id),
                "cif": row.cif,
                "query": row.query,
                "response": row.response[:200] + "..." if len(row.response or "") > 200 else row.response,
                "model_used": row.model_used,
                "latency_ms": row.latency_ms,
                "top_similarity_score": row.top_similarity_score,
                "retrieved_count": row.retrieved_count,
                "tokens_used": row.tokens_used,
                "created_at": row.created_at.isoformat()
            }
            for row in rows
        ],
        "limit": limit,
        "offset": offset
    }

@router.post("/aggregate/{query_type}")
async def aggregate_query(
    query_type: str,
    cif: str = Query(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Use the multi-agent system for aggregate queries."""
    valid_types = ["total_spending", "category_breakdown", "merchant_frequency"]
    if query_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query type. Must be one of: {valid_types}"
        )
    
    # Map query type to natural language for the brain service
    query_map = {
        "total_spending": "What is the total spending?",
        "category_breakdown": "Show spending breakdown by category",
        "merchant_frequency": "Show most frequent merchants"
    }
    
    # Use brain service with mapped query
    agent_results = await brain_service.execute_query(
        db=db,
        query=query_map[query_type],
        cif=cif
    )
    
    # Synthesize and return results
    synthesized_results = reasoning_service.synthesize_results(agent_results)
    
    return {
        "query_type": query_type,
        "cif": cif,
        "data": synthesized_results.get("data"),
        "agent_activity": [
            {
                "agent": result.get("agent"),
                "handled": result.get("handled")
            }
            for result in agent_results.get("results", [])
        ],
        "execution_time_ms": agent_results.get("total_execution_time_ms", 0)
    }

async def _save_search_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    cif: str,
    query: str,
    response: str,
    model_used: str,
    latency_ms: int,
    top_similarity_score: float,
    retrieved_count: int,
    tokens_used: int
):
    query_sql = text("""
        INSERT INTO search_history (
            id, user_id, cif, query, response, model_used,
            latency_ms, top_similarity_score, retrieved_count,
            tokens_used, created_at
        ) VALUES (
            :id, :user_id, :cif, :query, :response, :model_used,
            :latency_ms, :top_similarity_score, :retrieved_count,
            :tokens_used, :created_at
        )
    """)
    
    await db.execute(
        query_sql,
        {
            "id": uuid.uuid4(),
            "user_id": user_id,
            "cif": cif,
            "query": query,
            "response": response,
            "model_used": model_used,
            "latency_ms": latency_ms,
            "top_similarity_score": top_similarity_score,
            "retrieved_count": retrieved_count,
            "tokens_used": tokens_used,
            "created_at": datetime.now()
        }
    )
    await db.commit()