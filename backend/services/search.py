from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, and_
from models.cif import KBDocument
from services.embeddings import embedding_service
import numpy as np
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.embedding_service = embedding_service
        
    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        cif: str,
        top_k: int = 10,
        similarity_threshold: float = 0.5,
        include_global: bool = True
    ) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)[0]
        
        # Perform vector similarity search
        cif_results = await self._vector_search_cif(
            db, cif, query_embedding, top_k, similarity_threshold
        )
        
        global_results = []
        if include_global:
            global_results = await self._vector_search_global(
                db, query_embedding, top_k // 2, similarity_threshold
            )
        
        # Combine and rerank results
        all_results = self._combine_and_rerank(cif_results, global_results)
        
        # Calculate latency
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return {
            "query": query,
            "cif": cif,
            "results": all_results[:top_k],
            "total_retrieved": len(all_results),
            "latency_ms": latency_ms,
            "top_similarity_score": all_results[0]["similarity_score"] if all_results else 0
        }
    
    async def _vector_search_cif(
        self,
        db: AsyncSession,
        cif: str,
        query_embedding: np.ndarray,
        top_k: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        # Convert numpy array to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, query_embedding.tolist())) + ']'
        
        query = text("""
            SELECT 
                id,
                row_no,
                source_table,
                source_id,
                title,
                text,
                metadata,
                1 - (embedding <=> CAST(:embedding AS vector)) as similarity_score
            FROM kb_documents
            WHERE cif = :cif
                AND 1 - (embedding <=> CAST(:embedding AS vector)) > :threshold
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        
        result = await db.execute(
            query,
            {
                "embedding": embedding_str,
                "cif": cif,
                "threshold": threshold,
                "limit": top_k
            }
        )
        
        rows = result.fetchall()
        return [
            {
                "id": str(row.id),
                "source_table": row.source_table,
                "source_id": str(row.source_id),
                "title": row.title,
                "text": row.text,
                "metadata": row.metadata,
                "similarity_score": float(row.similarity_score),
                "source": "cif"
            }
            for row in rows
        ]
    
    async def _vector_search_global(
        self,
        db: AsyncSession,
        query_embedding: np.ndarray,
        top_k: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        embedding_str = '[' + ','.join(map(str, query_embedding.tolist())) + ']'
        
        query = text("""
            SELECT 
                gc.id,
                gc.chunk_index,
                gc.text,
                gd.filename,
                gd.metadata,
                1 - (gc.embedding <=> CAST(:embedding AS vector)) as similarity_score
            FROM global_chunks gc
            JOIN global_docs gd ON gc.doc_id = gd.id
            WHERE 1 - (gc.embedding <=> CAST(:embedding AS vector)) > :threshold
                AND gd.status = 'indexed'
            ORDER BY gc.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        
        result = await db.execute(
            query,
            {
                "embedding": embedding_str,
                "threshold": threshold,
                "limit": top_k
            }
        )
        
        rows = result.fetchall()
        return [
            {
                "id": str(row.id),
                "filename": row.filename,
                "chunk_index": row.chunk_index,
                "text": row.text,
                "metadata": row.metadata,
                "similarity_score": float(row.similarity_score),
                "source": "global"
            }
            for row in rows
        ]
    
    def _combine_and_rerank(
        self,
        cif_results: List[Dict],
        global_results: List[Dict]
    ) -> List[Dict[str, Any]]:
        # Give slight preference to CIF-specific results
        for result in cif_results:
            result["adjusted_score"] = result["similarity_score"] * 1.1
        
        for result in global_results:
            result["adjusted_score"] = result["similarity_score"]
        
        # Combine and sort by adjusted score
        all_results = cif_results + global_results
        all_results.sort(key=lambda x: x["adjusted_score"], reverse=True)
        
        return all_results
    
    async def aggregate_queries(
        self,
        db: AsyncSession,
        cif: str,
        query_type: str
    ) -> Dict[str, Any]:
        """Perform aggregation queries on transaction data"""
        
        if query_type == "total_spending":
            query = text("""
                SELECT 
                    SUM(amount) as total,
                    COUNT(*) as transaction_count,
                    AVG(amount) as avg_amount
                FROM transactions_raw
                WHERE cif = :cif AND amount < 0
            """)
        elif query_type == "category_breakdown":
            query = text("""
                SELECT 
                    category,
                    SUM(ABS(amount)) as total,
                    COUNT(*) as count
                FROM transactions_raw
                WHERE cif = :cif AND category IS NOT NULL
                GROUP BY category
                ORDER BY total DESC
            """)
        elif query_type == "merchant_frequency":
            query = text("""
                SELECT 
                    merchant_name,
                    COUNT(*) as frequency,
                    SUM(ABS(amount)) as total_spent
                FROM transactions_raw
                WHERE cif = :cif AND merchant_name IS NOT NULL
                GROUP BY merchant_name
                ORDER BY frequency DESC
                LIMIT 20
            """)
        else:
            return {"error": "Unknown query type"}
        
        result = await db.execute(query, {"cif": cif})
        
        if query_type in ["total_spending"]:
            row = result.fetchone()
            return {
                "total": float(row.total or 0),
                "transaction_count": row.transaction_count,
                "avg_amount": float(row.avg_amount or 0)
            }
        else:
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

search_service = SearchService()