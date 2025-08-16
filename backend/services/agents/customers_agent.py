"""
Customer Profile Query Agent for querying customer_profiles table.
Handles customer demographic and profile-related queries.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from .base_agent import BaseQueryAgent
import logging
import json
from utils.simple_logger import setup_logger

# Use enhanced logger
logger = setup_logger(__name__)


class CustomersAgent(BaseQueryAgent):
    """
    Agent specialized for querying customer profile data.
    Queries the customer_profiles and cifs tables.
    """
    
    def __init__(self):
        super().__init__("customers")
        self.profile_fields = {
            "age",
            "gender",
            "occupation",
            "income_range",
            "risk_profile",
            "preferred_channels"
        }
        self.cif_fields = {
            "customer_name",
            "customer_type",
            "status"
        }
    
    async def can_handle(self, context: Dict[str, Any]) -> bool:
        """
        Check if context contains customer profile-related parameters.
        
        Args:
            context: Query context with extracted entities
            
        Returns:
            True if customer profile fields are requested
        """
        # Handle if any customer-related field is present
        customer_indicators = [
            "profile",
            "customer_info",
            "demographics",
            "age",
            "gender",
            "occupation",
            "income",
            "risk_profile",
            "customer_name",
            "customer_type",
            "preferred_channels"
        ]
        
        query_text = context.get("query", "").lower()
        return any(indicator in query_text for indicator in customer_indicators)
    
    async def execute(
        self,
        db: AsyncSession,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute customer profile queries based on context.
        
        Args:
            db: Async database session
            context: Query context with filters
            
        Returns:
            Customer profile query results
        """
        cif = context.get("cif")
        if not cif:
            return {
                "error": "CIF is required for customer queries",
                "code": "MISSING_CIF"
            }
        
        # Determine query type
        query_text = context.get("query", "").lower()
        
        if "all" in query_text or "complete" in query_text or "full" in query_text:
            return await self._get_complete_profile(db, cif)
        elif "segment" in query_text or "similar" in query_text:
            return await self._get_customer_segment(db, cif)
        else:
            return await self._get_customer_profile(db, cif, context)
    
    async def _get_customer_profile(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get basic customer profile information.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context
            
        Returns:
            Customer profile data
        """
        query = text("""
            SELECT 
                c.cif,
                c.customer_name,
                c.customer_type,
                c.status,
                c.metadata as cif_metadata,
                c.created_at as customer_since,
                cp.age,
                cp.gender,
                cp.occupation,
                cp.income_range,
                cp.risk_profile,
                cp.preferred_channels,
                cp.metadata as profile_metadata,
                cp.updated_at as profile_updated_at
            FROM cifs c
            LEFT JOIN customer_profiles cp ON c.cif = cp.cif
            WHERE c.cif = :cif
        """)
        
        # Log the query
        logger.info(f"[CustomersAgent] Fetching customer profile for CIF: {cif}")
        
        result = await db.execute(query, {"cif": cif})
        row = result.fetchone()
        
        if row:
            logger.info(f"[CustomersAgent] Profile found:")
            logger.info(f"  Customer: {row.customer_name}")
            logger.info(f"  Type: {row.customer_type}")
            logger.info(f"  Status: {row.status}")
            logger.info(f"  Age: {row.age}, Gender: {row.gender}, Occupation: {row.occupation}")
        else:
            logger.info(f"[CustomersAgent] No profile found for CIF: {cif}")
        
        if row:
            profile_data = dict(row._mapping)
            
            # Convert datetime objects to ISO format strings
            if profile_data.get("customer_since"):
                profile_data["customer_since"] = profile_data["customer_since"].isoformat()
            if profile_data.get("profile_updated_at"):
                profile_data["profile_updated_at"] = profile_data["profile_updated_at"].isoformat()
            
            # Parse JSON fields
            if profile_data.get("preferred_channels"):
                profile_data["preferred_channels"] = (
                    profile_data["preferred_channels"]
                    if isinstance(profile_data["preferred_channels"], list)
                    else []
                )
            
            return {
                "type": "profile",
                "customer": profile_data,
                "has_profile": profile_data.get("age") is not None
            }
        
        return {
            "type": "profile",
            "customer": None,
            "message": "Customer not found"
        }
    
    async def _get_complete_profile(
        self,
        db: AsyncSession,
        cif: str
    ) -> Dict[str, Any]:
        """
        Get complete customer profile with additional statistics.
        
        Args:
            db: Database session
            cif: Customer identifier
            
        Returns:
            Complete customer profile with statistics
        """
        # Get basic profile
        profile_result = await self._get_customer_profile(db, cif, {})
        
        if not profile_result.get("customer"):
            return profile_result
        
        # Get transaction statistics
        stats_query = text("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT merchant_name) as unique_merchants,
                COUNT(DISTINCT category) as unique_categories,
                MIN(transaction_date) as first_transaction,
                MAX(transaction_date) as last_transaction,
                SUM(CASE WHEN amount > 0 THEN 1 ELSE 0 END) as credit_count,
                SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) as debit_count,
                AVG(ABS(amount)) as avg_transaction_amount
            FROM transactions_raw
            WHERE cif = :cif
        """)
        
        stats_result = await db.execute(stats_query, {"cif": cif})
        stats_row = stats_result.fetchone()
        
        # Get contact statistics
        contacts_query = text("""
            SELECT 
                COUNT(*) as total_contacts,
                COUNT(DISTINCT bank_name) as unique_banks,
                SUM(frequency) as total_transfer_frequency
            FROM transfer_contacts
            WHERE cif = :cif
        """)
        
        contacts_result = await db.execute(contacts_query, {"cif": cif})
        contacts_row = contacts_result.fetchone()
        
        # Get promo statistics
        promo_query = text("""
            SELECT 
                COUNT(*) as total_promos,
                SUM(CASE WHEN is_used THEN 1 ELSE 0 END) as used_promos,
                COUNT(DISTINCT merchant_category) as promo_categories
            FROM promos
            WHERE cif = :cif
        """)
        
        promo_result = await db.execute(promo_query, {"cif": cif})
        promo_row = promo_result.fetchone()
        
        # Combine all data
        complete_profile = {
            "type": "complete_profile",
            "customer": profile_result["customer"],
            "statistics": {
                "transactions": {
                    "total": stats_row.total_transactions if stats_row else 0,
                    "unique_merchants": stats_row.unique_merchants if stats_row else 0,
                    "unique_categories": stats_row.unique_categories if stats_row else 0,
                    "first_transaction": (
                        stats_row.first_transaction.isoformat()
                        if stats_row and stats_row.first_transaction
                        else None
                    ),
                    "last_transaction": (
                        stats_row.last_transaction.isoformat()
                        if stats_row and stats_row.last_transaction
                        else None
                    ),
                    "credit_count": stats_row.credit_count if stats_row else 0,
                    "debit_count": stats_row.debit_count if stats_row else 0,
                    "avg_amount": float(stats_row.avg_transaction_amount) if stats_row and stats_row.avg_transaction_amount else 0
                },
                "contacts": {
                    "total": contacts_row.total_contacts if contacts_row else 0,
                    "unique_banks": contacts_row.unique_banks if contacts_row else 0,
                    "total_frequency": contacts_row.total_transfer_frequency if contacts_row else 0
                },
                "promos": {
                    "total": promo_row.total_promos if promo_row else 0,
                    "used": promo_row.used_promos if promo_row else 0,
                    "categories": promo_row.promo_categories if promo_row else 0
                }
            }
        }
        
        return complete_profile
    
    async def _get_customer_segment(
        self,
        db: AsyncSession,
        cif: str
    ) -> Dict[str, Any]:
        """
        Get customer segmentation information.
        
        Args:
            db: Database session
            cif: Customer identifier
            
        Returns:
            Customer segment analysis
        """
        # Get customer profile
        profile_query = text("""
            SELECT 
                cp.age,
                cp.gender,
                cp.income_range,
                cp.risk_profile,
                cp.occupation
            FROM customer_profiles cp
            WHERE cp.cif = :cif
        """)
        
        profile_result = await db.execute(profile_query, {"cif": cif})
        profile = profile_result.fetchone()
        
        if not profile:
            return {
                "type": "segment",
                "message": "Customer profile not found",
                "segment": None
            }
        
        # Find similar customers (simplified segmentation)
        conditions = []
        params = {"exclude_cif": cif}
        
        if profile.age:
            conditions.append("ABS(cp.age - :age) <= 5")
            params["age"] = profile.age
        
        if profile.income_range:
            conditions.append("cp.income_range = :income_range")
            params["income_range"] = profile.income_range
        
        if profile.risk_profile:
            conditions.append("cp.risk_profile = :risk_profile")
            params["risk_profile"] = profile.risk_profile
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        segment_query = text(f"""
            SELECT 
                COUNT(DISTINCT cp.cif) as segment_size,
                AVG(cp.age) as avg_age,
                MODE() WITHIN GROUP (ORDER BY cp.gender) as common_gender,
                MODE() WITHIN GROUP (ORDER BY cp.occupation) as common_occupation,
                MODE() WITHIN GROUP (ORDER BY cp.income_range) as common_income_range
            FROM customer_profiles cp
            WHERE {where_clause} AND cp.cif != :exclude_cif
        """)
        
        segment_result = await db.execute(segment_query, params)
        segment = segment_result.fetchone()
        
        # Get spending patterns for the segment
        spending_query = text(f"""
            SELECT 
                t.category,
                COUNT(*) as transaction_count,
                AVG(ABS(t.amount)) as avg_amount
            FROM transactions_raw t
            JOIN customer_profiles cp ON t.cif = cp.cif
            WHERE {where_clause} AND cp.cif != :exclude_cif
                AND t.category IS NOT NULL
            GROUP BY t.category
            ORDER BY transaction_count DESC
            LIMIT 5
        """)
        
        spending_result = await db.execute(spending_query, params)
        top_categories = [
            {
                "category": row.category,
                "transaction_count": row.transaction_count,
                "avg_amount": float(row.avg_amount) if row.avg_amount else 0
            }
            for row in spending_result.fetchall()
        ]
        
        return {
            "type": "segment",
            "customer_profile": {
                "age": profile.age,
                "gender": profile.gender,
                "income_range": profile.income_range,
                "risk_profile": profile.risk_profile,
                "occupation": profile.occupation
            },
            "segment": {
                "size": segment.segment_size if segment else 0,
                "avg_age": float(segment.avg_age) if segment and segment.avg_age else None,
                "common_gender": segment.common_gender if segment else None,
                "common_occupation": segment.common_occupation if segment else None,
                "common_income_range": segment.common_income_range if segment else None,
                "top_spending_categories": top_categories
            }
        }