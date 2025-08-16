"""
Transactions Query Agent for querying transactions_raw table.
Handles transaction-specific queries with filters on dates, merchants, categories, etc.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date, datetime
from decimal import Decimal
from .base_agent import BaseQueryAgent
import logging
from utils.simple_logger import setup_logger

# Use enhanced logger
logger = setup_logger(__name__)


class TransactionsAgent(BaseQueryAgent):
    """
    Agent specialized for querying transaction data.
    Queries the transactions_raw table with various filters.
    """
    
    def __init__(self):
        super().__init__("transactions")
        self.supported_fields = {
            "transaction_date",
            "description", 
            "merchant_name",
            "transaction_type",
            "category",
            "amount",
            "mcc",
            "location",
            "reference_number"
        }
    
    async def can_handle(self, context: Dict[str, Any]) -> bool:
        """
        Check if context contains transaction-related parameters.
        
        Args:
            context: Query context with extracted entities
            
        Returns:
            True if transaction-related fields are present
        """
        # Handle if any transaction-related field is present
        transaction_indicators = [
            "transaction_date",
            "date_range",
            "merchant_name",
            "merchants",
            "category",
            "categories",
            "transaction_type",
            "amount",
            "amount_range",
            "spending",
            "payment",
            "transfer"
        ]
        
        return any(key in context for key in transaction_indicators)
    
    async def execute(
        self,
        db: AsyncSession,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute transaction queries based on context.
        
        Args:
            db: Async database session
            context: Query context with filters
            
        Returns:
            Transaction query results
        """
        cif = context.get("cif")
        if not cif:
            return {
                "error": "CIF is required for transaction queries",
                "code": "MISSING_CIF"
            }
        
        # Determine query type
        query_type = self._determine_query_type(context)
        
        if query_type == "aggregation":
            return await self._execute_aggregation_query(db, cif, context)
        elif query_type == "detail":
            return await self._execute_detail_query(db, cif, context)
        else:
            return await self._execute_search_query(db, cif, context)
    
    def _determine_query_type(self, context: Dict[str, Any]) -> str:
        """
        Determine the type of query to execute based on context.
        
        Args:
            context: Query context
            
        Returns:
            Query type: 'aggregation', 'detail', or 'search'
        """
        # Check for aggregation keywords
        aggregation_keywords = ["total", "sum", "average", "count", "breakdown", "spending"]
        query_text = context.get("query", "").lower()
        
        if any(keyword in query_text for keyword in aggregation_keywords):
            return "aggregation"
        
        # Check if specific transaction details are requested
        if context.get("transaction_id") or context.get("reference_number"):
            return "detail"
        
        return "search"
    
    async def _execute_aggregation_query(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute aggregation queries on transactions.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context
            
        Returns:
            Aggregation results
        """
        # Build WHERE conditions
        conditions = ["cif = :cif"]
        params = {"cif": cif}
        
        # Add date range filter
        if "date_range" in context:
            date_range = context["date_range"]
            if date_range.get("start"):
                conditions.append("transaction_date >= :start_date")
                params["start_date"] = date_range["start"]
            if date_range.get("end"):
                conditions.append("transaction_date <= :end_date")
                params["end_date"] = date_range["end"]
        
        # Add category filter
        if "categories" in context and context["categories"]:
            categories = context["categories"]
            category_placeholders = ', '.join([f":cat_{i}" for i in range(len(categories))])
            conditions.append(f"category IN ({category_placeholders})")
            for i, cat in enumerate(categories):
                params[f"cat_{i}"] = cat
        
        # Add merchant filter
        if "merchants" in context and context["merchants"]:
            merchants = context["merchants"]
            merchant_placeholders = ', '.join([f":merchant_{i}" for i in range(len(merchants))])
            conditions.append(f"merchant_name IN ({merchant_placeholders})")
            for i, merchant in enumerate(merchants):
                params[f"merchant_{i}"] = merchant
        
        where_clause = " AND ".join(conditions)
        
        # Determine aggregation type
        query_text = context.get("query", "").lower()
        
        if "category" in query_text and "breakdown" in query_text:
            # Category breakdown
            query = text(f"""
                SELECT 
                    category,
                    COUNT(*) as transaction_count,
                    SUM(ABS(amount)) as total_amount,
                    AVG(ABS(amount)) as avg_amount,
                    MIN(transaction_date) as first_transaction,
                    MAX(transaction_date) as last_transaction
                FROM transactions_raw
                WHERE {where_clause} AND category IS NOT NULL
                GROUP BY category
                ORDER BY total_amount DESC
            """)
        elif "merchant" in query_text and ("breakdown" in query_text or "frequency" in query_text):
            # Merchant breakdown
            query = text(f"""
                SELECT 
                    merchant_name,
                    COUNT(*) as transaction_count,
                    SUM(ABS(amount)) as total_amount,
                    AVG(ABS(amount)) as avg_amount,
                    MIN(transaction_date) as first_transaction,
                    MAX(transaction_date) as last_transaction
                FROM transactions_raw
                WHERE {where_clause} AND merchant_name IS NOT NULL
                GROUP BY merchant_name
                ORDER BY transaction_count DESC
                LIMIT 50
            """)
        else:
            # General aggregation
            query = text(f"""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_spending,
                    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
                    AVG(ABS(amount)) as avg_transaction_amount,
                    MAX(ABS(amount)) as max_transaction,
                    MIN(transaction_date) as first_transaction_date,
                    MAX(transaction_date) as last_transaction_date,
                    COUNT(DISTINCT merchant_name) as unique_merchants,
                    COUNT(DISTINCT category) as unique_categories
                FROM transactions_raw
                WHERE {where_clause}
            """)
        
        # Log the query being executed
        logger.info(f"[TransactionsAgent] Executing aggregation query")
        logger.info(f"  Context: CIF={cif}, dates={context.get('dates')}, categories={context.get('categories')}, merchants={context.get('merchants')}")
        logger.debug(f"  SQL: {str(query).replace(':cif', cif)[:200]}...")
        logger.debug(f"  Parameters: {params}")
        
        result = await db.execute(query, params)
        
        if "breakdown" in query_text:
            rows = result.fetchall()
            logger.info(f"[TransactionsAgent] Query returned {len(rows)} groups/categories")
            return {
                "type": "breakdown",
                "items": [
                    {
                        key: (
                            float(value) if isinstance(value, Decimal) 
                            else value.isoformat() if isinstance(value, date)
                            else value
                        )
                        for key, value in row._mapping.items()
                    }
                    for row in rows
                ],
                "total_groups": len(rows)
            }
        else:
            row = result.fetchone()
            logger.info(f"[TransactionsAgent] Aggregation result fetched")
            if row:
                # Log summary of results
                row_dict = row._mapping
                logger.info(f"  Total transactions: {row_dict.get('total_transactions', 0)}")
                spending = row_dict.get('total_spending', 0)
                if spending is not None:
                    logger.info(f"  Total spending: Rp {float(spending):,.2f}")
                else:
                    logger.info(f"  Total spending: Rp 0")
                logger.info(f"  Unique merchants: {row_dict.get('unique_merchants', 0)}")
            if row:
                return {
                    "type": "aggregation",
                    "summary": {
                        key: (
                            float(value) if isinstance(value, Decimal)
                            else value.isoformat() if isinstance(value, date)
                            else value
                        )
                        for key, value in row._mapping.items()
                    }
                }
            return {"type": "aggregation", "summary": {}}
    
    async def _execute_detail_query(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute detailed transaction queries.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context
            
        Returns:
            Detailed transaction results
        """
        conditions = ["cif = :cif"]
        params = {"cif": cif}
        
        if context.get("transaction_id"):
            conditions.append("id = :transaction_id")
            params["transaction_id"] = context["transaction_id"]
        
        if context.get("reference_number"):
            conditions.append("reference_number = :reference_number")
            params["reference_number"] = context["reference_number"]
        
        where_clause = " AND ".join(conditions)
        
        query = text(f"""
            SELECT 
                id,
                transaction_date,
                posting_date,
                description,
                merchant_name,
                mcc,
                amount,
                currency,
                balance,
                transaction_type,
                category,
                location,
                reference_number,
                metadata,
                created_at
            FROM transactions_raw
            WHERE {where_clause}
            ORDER BY transaction_date DESC
            LIMIT 1
        """)
        
        result = await db.execute(query, params)
        row = result.fetchone()
        
        if row:
            return {
                "type": "detail",
                "transaction": {
                    key: (
                        float(value) if isinstance(value, Decimal)
                        else value.isoformat() if isinstance(value, (date, datetime))
                        else str(value) if value is not None
                        else None
                    )
                    for key, value in row._mapping.items()
                }
            }
        
        return {
            "type": "detail",
            "transaction": None,
            "message": "Transaction not found"
        }
    
    async def _execute_search_query(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute transaction search queries.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context
            
        Returns:
            Search results
        """
        conditions = ["cif = :cif"]
        params = {"cif": cif}
        
        # Add filters based on context
        if "date_range" in context:
            date_range = context["date_range"]
            if date_range.get("start"):
                conditions.append("transaction_date >= :start_date")
                params["start_date"] = date_range["start"]
            if date_range.get("end"):
                conditions.append("transaction_date <= :end_date")
                params["end_date"] = date_range["end"]
        
        if "merchants" in context and context["merchants"]:
            merchants = context["merchants"]
            merchant_placeholders = ', '.join([f":merchant_{i}" for i in range(len(merchants))])
            conditions.append(f"merchant_name IN ({merchant_placeholders})")
            for i, merchant in enumerate(merchants):
                params[f"merchant_{i}"] = merchant
        
        if "categories" in context and context["categories"]:
            categories = context["categories"]
            category_placeholders = ', '.join([f":cat_{i}" for i in range(len(categories))])
            conditions.append(f"category IN ({category_placeholders})")
            for i, cat in enumerate(categories):
                params[f"cat_{i}"] = cat
        
        if "transaction_type" in context:
            conditions.append("transaction_type = :transaction_type")
            params["transaction_type"] = context["transaction_type"]
        
        if "amount_range" in context:
            amount_range = context["amount_range"]
            if amount_range.get("min") is not None:
                conditions.append("ABS(amount) >= :min_amount")
                params["min_amount"] = abs(amount_range["min"])
            if amount_range.get("max") is not None:
                conditions.append("ABS(amount) <= :max_amount")
                params["max_amount"] = abs(amount_range["max"])
        
        where_clause = " AND ".join(conditions)
        
        # Determine limit
        limit = min(context.get("limit", 100), 500)
        params["limit"] = limit
        
        query = text(f"""
            SELECT 
                id,
                transaction_date,
                description,
                merchant_name,
                amount,
                category,
                transaction_type,
                location,
                reference_number
            FROM transactions_raw
            WHERE {where_clause}
            ORDER BY transaction_date DESC, created_at DESC
            LIMIT :limit
        """)
        
        # Log the search query
        logger.info(f"[TransactionsAgent] Executing search query")
        logger.info(f"  Filters: dates={context.get('date_range')}, merchants={context.get('merchants')}, categories={context.get('categories')}")
        logger.info(f"  Limit: {limit}")
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        logger.info(f"[TransactionsAgent] Found {len(rows)} transactions")
        if rows:
            # Log sample of results
            sample = rows[:3]
            for i, row in enumerate(sample, 1):
                r = row._mapping
                amount = r.get('amount', 0)
                amount_str = f"Rp {float(amount):,.2f}" if amount is not None else "Rp 0"
                logger.info(f"  Sample {i}: {r.get('transaction_date')} | {r.get('merchant_name')} | {amount_str}")
            if len(rows) > 3:
                logger.info(f"  ... and {len(rows) - 3} more transactions")
        
        return {
            "type": "search",
            "transactions": [
                {
                    key: (
                        float(value) if isinstance(value, Decimal)
                        else value.isoformat() if isinstance(value, date)
                        else str(value) if value is not None
                        else None
                    )
                    for key, value in row._mapping.items()
                }
                for row in rows
            ],
            "count": len(rows),
            "limit": limit
        }