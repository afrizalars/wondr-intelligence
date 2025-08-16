"""
Transfer Contact Query Agent for querying transfer_contacts table.
Handles queries about transfer contacts, beneficiaries, and payment recipients.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date, datetime
from .base_agent import BaseQueryAgent
import logging
from utils.simple_logger import setup_logger

# Use enhanced logger
logger = setup_logger(__name__)


class ContactAgent(BaseQueryAgent):
    """
    Agent specialized for querying transfer contact data.
    Queries the transfer_contacts table without total_amount field.
    """
    
    def __init__(self):
        super().__init__("contact")
        self.supported_fields = {
            "contact_name",
            "account_number",
            "bank_name",
            "contact_type",
            "frequency",
            "last_transfer_date"
        }
    
    async def can_handle(self, context: Dict[str, Any]) -> bool:
        """
        Check if context contains contact-related parameters.
        
        Args:
            context: Query context with extracted entities
            
        Returns:
            True if contact-related fields are requested
        """
        # Handle if any contact-related field is present
        contact_indicators = [
            "contact",
            "beneficiary",
            "beneficiaries",
            "recipient",
            "transfer",
            "send_money",
            "payment_to",
            "bank",
            "account_number",
            "frequent_contacts"
        ]
        
        query_text = context.get("query", "").lower()
        return any(indicator in query_text for indicator in contact_indicators)
    
    async def execute(
        self,
        db: AsyncSession,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute contact queries based on context.
        
        Args:
            db: Async database session
            context: Query context with filters
            
        Returns:
            Contact query results
        """
        cif = context.get("cif")
        if not cif:
            return {
                "error": "CIF is required for contact queries",
                "code": "MISSING_CIF"
            }
        
        # Determine query type based on context
        query_text = context.get("query", "").lower()
        
        if "frequent" in query_text or "top" in query_text:
            return await self._get_frequent_contacts(db, cif, context)
        elif "bank" in query_text and ("breakdown" in query_text or "group" in query_text):
            return await self._get_contacts_by_bank(db, cif)
        elif "search" in query_text or "find" in query_text:
            return await self._search_contacts(db, cif, context)
        elif "recent" in query_text or "latest" in query_text:
            return await self._get_recent_contacts(db, cif, context)
        else:
            return await self._get_all_contacts(db, cif, context)
    
    async def _get_all_contacts(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get all contacts for a customer.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context
            
        Returns:
            All contacts
        """
        limit = min(context.get("limit", 100), 500)
        
        query = text("""
            SELECT 
                id,
                contact_name,
                account_number,
                bank_name,
                contact_type,
                frequency,
                last_transfer_date,
                metadata,
                created_at
            FROM transfer_contacts
            WHERE cif = :cif
            ORDER BY frequency DESC, last_transfer_date DESC NULLS LAST
            LIMIT :limit
        """)
        
        # Log the query
        logger.info(f"[ContactAgent] Fetching all contacts for CIF: {cif}, limit: {limit}")
        
        result = await db.execute(query, {"cif": cif, "limit": limit})
        rows = result.fetchall()
        
        logger.info(f"[ContactAgent] Found {len(rows)} contacts")
        if rows:
            # Log sample of contacts
            for i, row in enumerate(rows[:3], 1):
                r = row._mapping
                logger.info(f"  Contact {i}: {r.get('contact_name')} | {r.get('bank_name')} | Frequency: {r.get('frequency', 0)}")
            if len(rows) > 3:
                logger.info(f"  ... and {len(rows) - 3} more contacts")
        
        contacts = []
        for row in rows:
            contact = dict(row._mapping)
            # Convert dates to ISO format
            if contact.get("last_transfer_date"):
                contact["last_transfer_date"] = contact["last_transfer_date"].isoformat()
            if contact.get("created_at"):
                contact["created_at"] = contact["created_at"].isoformat()
            # Convert UUID to string
            if contact.get("id"):
                contact["id"] = str(contact["id"])
            contacts.append(contact)
        
        return {
            "type": "all_contacts",
            "contacts": contacts,
            "count": len(contacts),
            "limit": limit
        }
    
    async def _get_frequent_contacts(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get most frequently used contacts.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context
            
        Returns:
            Frequent contacts
        """
        top_n = min(context.get("top_n", 10), 50)
        
        query = text("""
            SELECT 
                id,
                contact_name,
                account_number,
                bank_name,
                contact_type,
                frequency,
                last_transfer_date,
                CASE 
                    WHEN last_transfer_date IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (CURRENT_DATE - last_transfer_date)) / 86400
                    ELSE NULL
                END as days_since_last_transfer
            FROM transfer_contacts
            WHERE cif = :cif AND frequency > 0
            ORDER BY frequency DESC, last_transfer_date DESC NULLS LAST
            LIMIT :limit
        """)
        
        result = await db.execute(query, {"cif": cif, "limit": top_n})
        rows = result.fetchall()
        
        contacts = []
        for row in rows:
            contact = dict(row._mapping)
            # Convert dates to ISO format
            if contact.get("last_transfer_date"):
                contact["last_transfer_date"] = contact["last_transfer_date"].isoformat()
            # Convert UUID to string
            if contact.get("id"):
                contact["id"] = str(contact["id"])
            # Convert days to int if exists
            if contact.get("days_since_last_transfer") is not None:
                contact["days_since_last_transfer"] = int(contact["days_since_last_transfer"])
            contacts.append(contact)
        
        # Calculate statistics
        total_frequency = sum(c["frequency"] for c in contacts)
        avg_frequency = total_frequency / len(contacts) if contacts else 0
        
        return {
            "type": "frequent_contacts",
            "contacts": contacts,
            "count": len(contacts),
            "statistics": {
                "total_transfers": total_frequency,
                "average_frequency": round(avg_frequency, 2),
                "most_frequent": contacts[0] if contacts else None
            }
        }
    
    async def _get_recent_contacts(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get recently used contacts.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context
            
        Returns:
            Recent contacts
        """
        limit = min(context.get("limit", 20), 100)
        
        query = text("""
            SELECT 
                id,
                contact_name,
                account_number,
                bank_name,
                contact_type,
                frequency,
                last_transfer_date,
                CASE 
                    WHEN last_transfer_date IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (CURRENT_DATE - last_transfer_date)) / 86400
                    ELSE NULL
                END as days_since_last_transfer
            FROM transfer_contacts
            WHERE cif = :cif AND last_transfer_date IS NOT NULL
            ORDER BY last_transfer_date DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, {"cif": cif, "limit": limit})
        rows = result.fetchall()
        
        contacts = []
        for row in rows:
            contact = dict(row._mapping)
            # Convert dates to ISO format
            if contact.get("last_transfer_date"):
                contact["last_transfer_date"] = contact["last_transfer_date"].isoformat()
            # Convert UUID to string
            if contact.get("id"):
                contact["id"] = str(contact["id"])
            # Convert days to int if exists
            if contact.get("days_since_last_transfer") is not None:
                contact["days_since_last_transfer"] = int(contact["days_since_last_transfer"])
            contacts.append(contact)
        
        return {
            "type": "recent_contacts",
            "contacts": contacts,
            "count": len(contacts)
        }
    
    async def _get_contacts_by_bank(
        self,
        db: AsyncSession,
        cif: str
    ) -> Dict[str, Any]:
        """
        Get contacts grouped by bank.
        
        Args:
            db: Database session
            cif: Customer identifier
            
        Returns:
            Contacts grouped by bank
        """
        query = text("""
            SELECT 
                bank_name,
                COUNT(*) as contact_count,
                SUM(frequency) as total_frequency,
                MAX(last_transfer_date) as most_recent_transfer,
                ARRAY_AGG(
                    json_build_object(
                        'contact_name', contact_name,
                        'account_number', account_number,
                        'frequency', frequency,
                        'contact_type', contact_type
                    )
                    ORDER BY frequency DESC
                    LIMIT 5
                ) as top_contacts
            FROM transfer_contacts
            WHERE cif = :cif AND bank_name IS NOT NULL
            GROUP BY bank_name
            ORDER BY total_frequency DESC
        """)
        
        result = await db.execute(query, {"cif": cif})
        rows = result.fetchall()
        
        banks = []
        for row in rows:
            bank_data = {
                "bank_name": row.bank_name,
                "contact_count": row.contact_count,
                "total_frequency": row.total_frequency,
                "most_recent_transfer": (
                    row.most_recent_transfer.isoformat()
                    if row.most_recent_transfer
                    else None
                ),
                "top_contacts": row.top_contacts
            }
            banks.append(bank_data)
        
        return {
            "type": "contacts_by_bank",
            "banks": banks,
            "total_banks": len(banks),
            "total_contacts": sum(b["contact_count"] for b in banks)
        }
    
    async def _search_contacts(
        self,
        db: AsyncSession,
        cif: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search contacts based on filters.
        
        Args:
            db: Database session
            cif: Customer identifier
            context: Query context with search parameters
            
        Returns:
            Search results
        """
        conditions = ["cif = :cif"]
        params = {"cif": cif}
        
        # Add search filters
        if context.get("contact_name"):
            conditions.append("LOWER(contact_name) LIKE LOWER(:contact_name)")
            params["contact_name"] = f"%{context['contact_name']}%"
        
        if context.get("bank_name"):
            conditions.append("LOWER(bank_name) = LOWER(:bank_name)")
            params["bank_name"] = context["bank_name"]
        
        if context.get("account_number"):
            conditions.append("account_number = :account_number")
            params["account_number"] = context["account_number"]
        
        if context.get("contact_type"):
            conditions.append("contact_type = :contact_type")
            params["contact_type"] = context["contact_type"]
        
        if context.get("min_frequency"):
            conditions.append("frequency >= :min_frequency")
            params["min_frequency"] = context["min_frequency"]
        
        where_clause = " AND ".join(conditions)
        limit = min(context.get("limit", 50), 200)
        params["limit"] = limit
        
        query = text(f"""
            SELECT 
                id,
                contact_name,
                account_number,
                bank_name,
                contact_type,
                frequency,
                last_transfer_date,
                metadata,
                created_at
            FROM transfer_contacts
            WHERE {where_clause}
            ORDER BY frequency DESC, contact_name
            LIMIT :limit
        """)
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        contacts = []
        for row in rows:
            contact = dict(row._mapping)
            # Convert dates to ISO format
            if contact.get("last_transfer_date"):
                contact["last_transfer_date"] = contact["last_transfer_date"].isoformat()
            if contact.get("created_at"):
                contact["created_at"] = contact["created_at"].isoformat()
            # Convert UUID to string
            if contact.get("id"):
                contact["id"] = str(contact["id"])
            contacts.append(contact)
        
        return {
            "type": "contact_search",
            "contacts": contacts,
            "count": len(contacts),
            "search_criteria": {
                k: v for k, v in context.items()
                if k in ["contact_name", "bank_name", "account_number", "contact_type", "min_frequency"]
            }
        }