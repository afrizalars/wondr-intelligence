"""
Brain Service for multi-agent query system.
Parses natural language queries, extracts context, and routes to appropriate agents.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import re
import logging
from services.agents.transactions_agent import TransactionsAgent
from services.agents.customers_agent import CustomersAgent
from services.agents.contact_agent import ContactAgent
from utils.simple_logger import setup_logger

# Use enhanced logger
logger = setup_logger(__name__)


class BrainService:
    """
    Brain service that coordinates multi-agent query processing.
    Parses queries, determines routing, and aggregates results.
    """
    
    def __init__(self):
        """Initialize Brain service with available agents."""
        self.agents = {
            "transactions": TransactionsAgent(),
            "customers": CustomersAgent(),
            "contact": ContactAgent()
        }
        
        # Common date patterns
        self.date_patterns = {
            "today": lambda: date.today(),
            "yesterday": lambda: date.today() - timedelta(days=1),
            "this_week": lambda: (date.today() - timedelta(days=date.today().weekday()), date.today()),
            "last_week": lambda: (
                date.today() - timedelta(days=date.today().weekday() + 7),
                date.today() - timedelta(days=date.today().weekday() + 1)
            ),
            "this_month": lambda: (date.today().replace(day=1), date.today()),
            "last_month": lambda: self._get_last_month_range(),
            "this_year": lambda: (date.today().replace(month=1, day=1), date.today()),
            "last_year": lambda: (
                date.today().replace(year=date.today().year - 1, month=1, day=1),
                date.today().replace(year=date.today().year - 1, month=12, day=31)
            )
        }
        
        # Transaction type keywords
        self.transaction_types = {
            "debit": ["debit", "payment", "purchase", "withdrawal", "spending"],
            "credit": ["credit", "deposit", "income", "salary", "refund"],
            "transfer": ["transfer", "send", "wire", "remittance"]
        }
        
        # Common merchant categories
        self.categories = {
            "food": ["food", "restaurant", "dining", "meal", "cafe", "coffee"],
            "transport": ["transport", "taxi", "uber", "grab", "fuel", "parking"],
            "shopping": ["shopping", "retail", "store", "mall", "online"],
            "entertainment": ["entertainment", "movie", "game", "sport", "leisure"],
            "bills": ["bill", "utility", "electricity", "water", "internet", "phone"],
            "health": ["health", "medical", "pharmacy", "doctor", "hospital"],
            "education": ["education", "school", "course", "training", "book"]
        }
    
    def _get_last_month_range(self) -> Tuple[date, date]:
        """Get the date range for last month."""
        today = date.today()
        first_day_current_month = today.replace(day=1)
        last_day_last_month = first_day_current_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        return (first_day_last_month, last_day_last_month)
    
    def parse_query(self, query: str, cif: str) -> Dict[str, Any]:
        """
        Parse natural language query to extract context.
        
        Args:
            query: Natural language query
            cif: Customer identifier
            
        Returns:
            Extracted context dictionary
        """
        context = {
            "query": query,
            "cif": cif,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        query_lower = query.lower()
        
        # Extract date ranges
        date_context = self._extract_dates(query_lower)
        if date_context:
            context.update(date_context)
        
        # Extract merchants
        merchants = self._extract_merchants(query_lower)
        if merchants:
            context["merchants"] = merchants
        
        # Extract categories
        categories = self._extract_categories(query_lower)
        if categories:
            context["categories"] = categories
        
        # Extract transaction types
        transaction_type = self._extract_transaction_type(query_lower)
        if transaction_type:
            context["transaction_type"] = transaction_type
        
        # Extract amounts
        amount_context = self._extract_amounts(query_lower)
        if amount_context:
            context.update(amount_context)
        
        # Extract contact-related information
        contact_context = self._extract_contact_info(query_lower)
        if contact_context:
            context.update(contact_context)
        
        # Extract limit if specified
        limit_match = re.search(r'(?:top|first|last|limit)\s+(\d+)', query_lower)
        if limit_match:
            context["limit"] = min(int(limit_match.group(1)), 500)
        
        return context
    
    def _extract_dates(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract date information from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            Date context or None
        """
        context = {}
        
        # Check for relative date patterns
        for pattern, date_func in self.date_patterns.items():
            if pattern.replace("_", " ") in query:
                result = date_func()
                if isinstance(result, tuple):
                    context["date_range"] = {"start": result[0], "end": result[1]}
                else:
                    context["date_range"] = {"start": result, "end": result}
                return context
        
        # Check for specific month names
        months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        
        for month_name, month_num in months.items():
            if month_name in query:
                # Check if year is specified
                year_match = re.search(rf'{month_name}\s+(\d{{4}})', query)
                if year_match:
                    year = int(year_match.group(1))
                else:
                    year = date.today().year
                
                # Get month range
                first_day = date(year, month_num, 1)
                if month_num == 12:
                    last_day = date(year, 12, 31)
                else:
                    last_day = date(year, month_num + 1, 1) - timedelta(days=1)
                
                context["date_range"] = {"start": first_day, "end": last_day}
                return context
        
        # Check for date range patterns (e.g., "from X to Y")
        range_match = re.search(r'from\s+(\S+)\s+to\s+(\S+)', query)
        if range_match:
            # Parse dates (simplified - would need more robust parsing in production)
            try:
                start_str = range_match.group(1)
                end_str = range_match.group(2)
                # Add date parsing logic here
                pass
            except:
                pass
        
        # Check for specific date patterns (YYYY-MM-DD)
        date_matches = re.findall(r'\d{4}-\d{2}-\d{2}', query)
        if date_matches:
            if len(date_matches) == 1:
                parsed_date = datetime.strptime(date_matches[0], "%Y-%m-%d").date()
                context["date_range"] = {"start": parsed_date, "end": parsed_date}
            elif len(date_matches) >= 2:
                start_date = datetime.strptime(date_matches[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(date_matches[1], "%Y-%m-%d").date()
                context["date_range"] = {"start": start_date, "end": end_date}
            return context
        
        return context if context else None
    
    def _extract_merchants(self, query: str) -> Optional[List[str]]:
        """
        Extract merchant names from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            List of merchant names or None
        """
        merchants = []
        
        # Common merchant patterns
        merchant_keywords = [
            "starbucks", "mcdonald", "kfc", "pizza hut", "amazon", "tokopedia",
            "shopee", "gojek", "grab", "uber", "netflix", "spotify", "apple",
            "google", "microsoft", "indomaret", "alfamart", "ace hardware"
        ]
        
        for merchant in merchant_keywords:
            if merchant in query:
                merchants.append(merchant.title())
        
        # Check for "at <merchant>" pattern
        at_pattern = re.findall(r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', query.title())
        merchants.extend(at_pattern)
        
        return merchants if merchants else None
    
    def _extract_categories(self, query: str) -> Optional[List[str]]:
        """
        Extract transaction categories from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            List of categories or None
        """
        found_categories = []
        
        for category, keywords in self.categories.items():
            if any(keyword in query for keyword in keywords):
                found_categories.append(category)
        
        return found_categories if found_categories else None
    
    def _extract_transaction_type(self, query: str) -> Optional[str]:
        """
        Extract transaction type from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            Transaction type or None
        """
        for trans_type, keywords in self.transaction_types.items():
            if any(keyword in query for keyword in keywords):
                return trans_type
        
        return None
    
    def _extract_amounts(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract amount information from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            Amount context or None
        """
        context = {}
        
        # Extract specific amounts
        amount_patterns = [
            r'(?:idr|rp|rupiah)?\s*(\d+(?:[.,]\d+)?(?:k|m|jt|juta|ribu)?)',
            r'(\d+(?:[.,]\d+)?(?:k|m|jt|juta|ribu)?)\s*(?:idr|rp|rupiah)?'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, query)
            if matches:
                amounts = []
                for match in matches:
                    # Convert to numeric value
                    value = match.replace(",", "").replace(".", "")
                    multiplier = 1
                    if "k" in match.lower() or "ribu" in match.lower():
                        multiplier = 1000
                    elif "m" in match.lower() or "jt" in match.lower() or "juta" in match.lower():
                        multiplier = 1000000
                    
                    # Extract numeric part
                    numeric_match = re.search(r'(\d+)', value)
                    if numeric_match:
                        amounts.append(float(numeric_match.group(1)) * multiplier)
                
                if amounts:
                    if "above" in query or "more than" in query or "greater than" in query:
                        context["amount_range"] = {"min": min(amounts), "max": None}
                    elif "below" in query or "less than" in query or "under" in query:
                        context["amount_range"] = {"min": None, "max": max(amounts)}
                    elif "between" in query and len(amounts) >= 2:
                        context["amount_range"] = {"min": min(amounts), "max": max(amounts)}
                    elif amounts:
                        context["amount"] = amounts[0]
                    
                    return context
        
        return None
    
    def _extract_contact_info(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract contact-related information from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            Contact context or None
        """
        context = {}
        
        # Check for bank names
        banks = [
            "bca", "mandiri", "bni", "bri", "cimb", "danamon", "permata",
            "maybank", "ocbc", "hsbc", "citibank", "standard chartered"
        ]
        
        for bank in banks:
            if bank in query:
                context["bank_name"] = bank.upper()
                break
        
        # Check for contact type
        if "personal" in query:
            context["contact_type"] = "personal"
        elif "business" in query or "company" in query:
            context["contact_type"] = "business"
        
        # Check for frequency requirements
        freq_match = re.search(r'(?:at least|minimum|more than)\s+(\d+)\s+(?:times|transfers)', query)
        if freq_match:
            context["min_frequency"] = int(freq_match.group(1))
        
        return context if context else None
    
    async def determine_agents(
        self,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Determine which agents should handle the query.
        
        Args:
            context: Parsed query context
            
        Returns:
            List of agent names to activate
        """
        active_agents = []
        
        # Check each agent's capability
        for agent_name, agent in self.agents.items():
            if await agent.can_handle(context):
                active_agents.append(agent_name)
                logger.info(f"Agent '{agent_name}' will handle query")
        
        # If no specific agent can handle, try all agents
        if not active_agents:
            logger.warning("No specific agent matched, activating all agents")
            active_agents = list(self.agents.keys())
        
        return active_agents
    
    async def execute_query(
        self,
        db: AsyncSession,
        query: str,
        cif: str
    ) -> Dict[str, Any]:
        """
        Execute multi-agent query processing.
        
        Args:
            db: Database session
            query: Natural language query
            cif: Customer identifier
            
        Returns:
            Aggregated results from all agents
        """
        start_time = datetime.utcnow()
        
        try:
            # Parse query to extract context
            context = self.parse_query(query, cif)
            logger.info(f"Parsed context: {context}")
            
            # Determine which agents to activate
            active_agents = await self.determine_agents(context)
            
            # Execute agents in parallel
            tasks = []
            for agent_name in active_agents:
                agent = self.agents[agent_name]
                tasks.append(agent.run(db, context))
            
            # Wait for all agents to complete
            agent_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            failed_results = []
            
            for i, result in enumerate(agent_results):
                agent_name = active_agents[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Agent '{agent_name}' failed with exception: {result}")
                    failed_results.append({
                        "agent": agent_name,
                        "error": str(result),
                        "error_type": type(result).__name__
                    })
                elif isinstance(result, dict) and result.get("handled"):
                    successful_results.append(result)
                else:
                    # Agent chose not to handle or had an error
                    if "error" in result:
                        failed_results.append(result)
            
            # Calculate total execution time
            total_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return {
                "query": query,
                "cif": cif,
                "context": context,
                "active_agents": active_agents,
                "results": successful_results,
                "failed_agents": failed_results,
                "total_execution_time_ms": total_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Brain service execution failed: {str(e)}", exc_info=True)
            return {
                "query": query,
                "cif": cif,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }


# Singleton instance
brain_service = BrainService()