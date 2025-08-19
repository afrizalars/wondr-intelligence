"""
Enhanced Brain Service using LLM for intelligent query parsing.
Uses Claude/GPT for context extraction with fuzzy matching and typo correction.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import json
import os
from anthropic import AsyncAnthropic
from services.agents.transactions_agent import TransactionsAgent
from services.agents.customers_agent import CustomersAgent
from services.agents.contact_agent import ContactAgent
from utils.simple_logger import setup_logger

# Use enhanced logger
logger = setup_logger(__name__)


class BrainServiceLLM:
    """
    Brain service that uses LLM for intelligent query parsing.
    Handles typos, fuzzy matching, and contextual understanding.
    """
    
    def __init__(self):
        """Initialize Brain service with available agents and LLM client."""
        self.agents = {
            "transactions": TransactionsAgent(),
            "customers": CustomersAgent(),
            "contact": ContactAgent()
        }
        
        # Initialize Anthropic client
        self.anthropic = AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def parse_query_with_llm(self, query: str, cif: str) -> Dict[str, Any]:
        """
        Use LLM to intelligently parse the query and extract context.
        
        Args:
            query: Natural language query (could have typos)
            cif: Customer identifier
            
        Returns:
            Extracted context dictionary
        """
        # Detect language
        language = "id" if any(word in query.lower() for word in [
            "saya", "aku", "berapa", "pengeluaran", "belanja", "transaksi",
            "bulan", "minggu", "hari", "tahun", "kemarin", "lalu"
        ]) else "en"
        
        # Get current date for context
        today = date.today()
        current_month_start = today.replace(day=1)
        
        system_prompt = """You are a financial query parser for Wondr Intelligence. 
Extract context from user queries about financial transactions.

IMPORTANT RULES:
1. Fix typos and misspellings (e.g., "spotyfy" → "spotify", "starbuck" → "starbucks")
2. Extract search keywords that should be used for database queries
3. For merchants/brands, provide common variations (e.g., spotify → ["spotify", "spotify.com", "spotify premium"])
4. For categories, think about what category the merchant/service belongs to
5. Default to current month if no date specified for spending queries
6. Detect query language and respond accordingly

Output JSON with these fields:
{
  "search_keywords": ["keyword1", "keyword2"],  // Keywords to search in merchant_name, description, or category
  "merchants": ["merchant1", "merchant2"],      // Likely merchant names (fixed typos)
  "categories": ["category1"],                  // Transaction categories if applicable
  "description_keywords": ["keyword1"],         // Keywords to search in description field
  "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},  // null if not specified
  "transaction_type": "debit/credit/transfer",  // null if not specified
  "language": "en/id",                         // Detected language
  "corrected_query": "fixed query"             // Query with typos fixed
}

Examples:
- "my spends on spotyfy" → search_keywords: ["spotify", "spotify.com"], categories: ["entertainment", "subscription"]
- "pengeluaran di starbuck" → search_keywords: ["starbucks", "starbuck"], categories: ["food", "coffee", "cafe"]
- "belanja di indomart minggu ini" → search_keywords: ["indomaret", "indomart"], categories: ["grocery", "shopping"]
"""

        user_prompt = f"""Parse this query: "{query}"
Current date: {today}
Current month: {current_month_start} to {today}"""

        try:
            response = await self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Extract JSON from response
            content = response.content[0].text
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = json.loads(content)
            
            # Build context from LLM response
            context = {
                "query": query,
                "cif": cif,
                "timestamp": datetime.utcnow().isoformat(),
                "language": parsed.get("language", language),
                "corrected_query": parsed.get("corrected_query", query)
            }
            
            # Add search keywords for flexible matching
            if parsed.get("search_keywords"):
                context["search_keywords"] = parsed["search_keywords"]
            
            # Add specific fields if present
            if parsed.get("merchants"):
                context["merchants"] = parsed["merchants"]
            
            if parsed.get("categories"):
                context["categories"] = parsed["categories"]
            
            if parsed.get("description_keywords"):
                context["description"] = " ".join(parsed["description_keywords"])
            
            if parsed.get("date_range"):
                date_range = parsed["date_range"]
                if date_range and date_range.get("start"):
                    context["date_range"] = {
                        "start": datetime.strptime(date_range["start"], "%Y-%m-%d").date(),
                        "end": datetime.strptime(date_range["end"], "%Y-%m-%d").date()
                    }
            else:
                # Default to current month for spending queries
                if any(word in query.lower() for word in [
                    "spending", "spent", "expense", "pengeluaran", "belanja", "transaksi"
                ]):
                    context["date_range"] = {
                        "start": current_month_start,
                        "end": today
                    }
                    logger.info(f"[BrainServiceLLM] No date specified, defaulting to current month: {current_month_start} to {today}")
            
            if parsed.get("transaction_type"):
                context["transaction_type"] = parsed["transaction_type"]
            
            logger.info(f"[BrainServiceLLM] LLM parsed context: {context}")
            return context
            
        except Exception as e:
            logger.error(f"[BrainServiceLLM] Error parsing with LLM: {e}")
            # Fallback to basic parsing
            return self.fallback_parse(query, cif)
    
    def fallback_parse(self, query: str, cif: str) -> Dict[str, Any]:
        """
        Fallback parsing without LLM.
        """
        context = {
            "query": query,
            "cif": cif,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Basic date defaulting
        if any(word in query.lower() for word in ["spending", "spent", "expense", "pengeluaran", "belanja"]):
            today = date.today()
            context["date_range"] = {
                "start": today.replace(day=1),
                "end": today
            }
        
        # Try to extract any obvious keywords
        query_lower = query.lower()
        if any(word in query_lower for word in ["debit", "payment", "purchase", "withdrawal", "spending"]):
            context["transaction_type"] = "debit"
        
        return context
    
    async def execute_query(
        self,
        db: AsyncSession,
        query: str,
        cif: str
    ) -> Dict[str, Any]:
        """
        Execute query through appropriate agents.
        
        Args:
            db: Database session
            query: User query
            cif: Customer identifier
            
        Returns:
            Query results with language-appropriate response
        """
        # Parse query with LLM
        context = await self.parse_query_with_llm(query, cif)
        
        # Determine which agents can handle this query
        capable_agents = []
        for agent_name, agent in self.agents.items():
            if await agent.can_handle(context):
                capable_agents.append(agent_name)
        
        if not capable_agents:
            logger.warning(f"[BrainServiceLLM] No specific agent matched, checking transaction agent")
            # Default to transaction agent for financial queries
            capable_agents = ["transactions"]
        
        logger.info(f"[BrainServiceLLM] Agents that will handle query: {capable_agents}")
        
        # Execute queries through capable agents
        results = {}
        for agent_name in capable_agents:
            agent = self.agents[agent_name]
            try:
                result = await agent.execute(db, context)
                results[agent_name] = result
                logger.info(f"[BrainServiceLLM] Agent '{agent_name}' executed successfully")
            except Exception as e:
                logger.error(f"[BrainServiceLLM] Agent '{agent_name}' failed: {e}")
                results[agent_name] = {"error": str(e)}
        
        # Return combined results with language context
        return {
            "context": context,
            "results": results,
            "language": context.get("language", "en"),
            "corrected_query": context.get("corrected_query", query)
        }