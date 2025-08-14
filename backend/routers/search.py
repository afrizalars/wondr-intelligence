from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.database import get_async_db
from services.search import search_service
from services.llm import llm_service
from services.guardrails import guardrail_service
from routers.auth import get_current_user
from models.user import User
from sqlalchemy import select, insert
from sqlalchemy.sql import text

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    cif: str
    include_global: bool = True
    top_k: int = 10
    similarity_threshold: float = 0.5
    use_guardrails: bool = True
    prompt_template: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    cif: str
    answer: str
    citations: List[Dict[str, Any]]
    transactions: Optional[List[Dict[str, Any]]] = None
    latency_ms: int
    model_used: str
    guardrail_status: Optional[Dict[str, Any]] = None

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
    # Check guardrails on input
    guardrail_result = None
    processed_query = request.query
    
    if request.use_guardrails:
        guardrail_result = await guardrail_service.check_input(request.query, db)
        
        if guardrail_result["action"] == "block":
            raise HTTPException(
                status_code=400,
                detail=guardrail_result.get("message", "Query blocked by guardrails")
            )
        elif guardrail_result["action"] == "transform":
            processed_query = guardrail_result.get("transformed_text", request.query)
    
    # Perform vector search
    search_results = await search_service.hybrid_search(
        db=db,
        query=processed_query,
        cif=request.cif,
        top_k=request.top_k,
        similarity_threshold=request.similarity_threshold,
        include_global=request.include_global
    )
    
    # Generate LLM response
    llm_response = await llm_service.generate_response(
        query=processed_query,
        context=search_results["results"],
        prompt_template=request.prompt_template
    )
    
    # Check guardrails on output
    if request.use_guardrails:
        output_check = await guardrail_service.check_output(llm_response["answer"], db)
        if output_check["action"] == "block":
            llm_response["answer"] = "Response blocked by content policy."
        elif output_check["action"] == "transform":
            llm_response["answer"] = output_check.get("transformed_text", llm_response["answer"])
    
    # Extract transactions from search results if it's a spending query
    transactions = None
    query_lower = processed_query.lower()
    if any(keyword in query_lower for keyword in ['spending', 'spend', 'transaction', 'purchase', 'payment', 'trend']):
        # For spending queries, directly fetch recent transactions
        # since semantic search doesn't work well for generic spending queries
        query_sql = text("""
            SELECT 
                kb.title,
                kb.text,
                kb.metadata,
                kb.source_table
            FROM kb_documents kb
            WHERE kb.cif = :cif
                AND kb.source_table = 'transactions_raw'
            ORDER BY kb.created_at DESC
            LIMIT 8
        """)
        
        result = await db.execute(query_sql, {"cif": request.cif})
        transaction_rows = result.fetchall()
        
        if transaction_rows:
            transactions = []
            import json
            import ast
            
            for row in transaction_rows:
                # Parse metadata - it might be a JSON string, Python dict string, or dict
                metadata = row.metadata
                
                # Try to parse if it's a string
                if isinstance(metadata, str):
                    try:
                        # First try JSON
                        metadata = json.loads(metadata)
                    except:
                        try:
                            # Then try Python literal eval for dict-like strings
                            metadata = ast.literal_eval(metadata)
                        except:
                            metadata = {}
                
                # Extract merchant from title if available (format: "Merchant · Amount · Date")
                title_parts = row.title.split("·") if row.title else []
                merchant_name = title_parts[0].strip() if title_parts else ""
                
                # Ensure we have valid data
                if metadata or merchant_name:
                    transactions.append({
                        "merchant": metadata.get("merchant", merchant_name) or merchant_name or "Unknown",
                        "amount": metadata.get("amount", 0),
                        "date": metadata.get("date", ""),
                        "category": metadata.get("category", ""),
                        "title": row.title or "",
                        "text": row.text or ""
                    })
    
    # Save to search history
    await _save_search_history(
        db=db,
        user_id=current_user.id,
        cif=request.cif,
        query=request.query,
        response=llm_response["answer"],
        model_used=llm_response.get("model"),
        latency_ms=search_results["latency_ms"] + llm_response.get("latency_ms", 0),
        top_similarity_score=search_results.get("top_similarity_score", 0),
        retrieved_count=len(search_results["results"]),
        tokens_used=llm_response.get("tokens_used", 0)
    )
    
    return SearchResponse(
        query=request.query,
        cif=request.cif,
        answer=llm_response["answer"],
        citations=llm_response.get("citations", []),
        transactions=transactions,
        latency_ms=search_results["latency_ms"] + llm_response.get("latency_ms", 0),
        model_used=llm_response.get("model", "unknown"),
        guardrail_status=guardrail_result
    )

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
    valid_types = ["total_spending", "category_breakdown", "merchant_frequency"]
    if query_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query type. Must be one of: {valid_types}"
        )
    
    result = await search_service.aggregate_queries(db, cif, query_type)
    return result

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