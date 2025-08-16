"""
Base Query Agent class for multi-agent query system.
Follows Wondr Architecture Guidelines for async patterns and error handling.
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class BaseQueryAgent(ABC):
    """
    Abstract base class for all query agents.
    Provides common functionality for SQL-based query agents.
    """
    
    def __init__(self, name: str):
        """
        Initialize base query agent.
        
        Args:
            name: Agent identifier for logging and tracing
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    async def can_handle(self, context: Dict[str, Any]) -> bool:
        """
        Determine if this agent should handle the given query context.
        
        Args:
            context: Parsed query context with extracted entities
            
        Returns:
            True if agent should process this query
        """
        pass
    
    @abstractmethod
    async def execute(
        self, 
        db: AsyncSession,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the agent's query logic.
        
        Args:
            db: Async database session
            context: Query context with extracted parameters
            
        Returns:
            Query results with metadata
        """
        pass
    
    async def run(
        self,
        db: AsyncSession,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point for agent execution with error handling.
        
        Args:
            db: Async database session
            context: Query context
            
        Returns:
            Agent results with metadata and timing
        """
        start_time = datetime.utcnow()
        
        try:
            # Check if agent should handle this query
            if not await self.can_handle(context):
                return {
                    "agent": self.name,
                    "handled": False,
                    "reason": "Context not applicable for this agent"
                }
            
            # Execute agent logic
            self.logger.info(f"Executing query with context: {json.dumps(context, default=str)}")
            results = await self.execute(db, context)
            
            # Calculate execution time
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return {
                "agent": self.name,
                "handled": True,
                "results": results,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return {
                "agent": self.name,
                "handled": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_filters(self, filters: Dict[str, Any]) -> List[str]:
        """
        Build SQL WHERE clause conditions from filter dictionary.
        
        Args:
            filters: Dictionary of field names and values
            
        Returns:
            List of SQL condition strings
        """
        conditions = []
        
        for field, value in filters.items():
            if value is None:
                continue
                
            if isinstance(value, list):
                if value:  # Only add if list is not empty
                    placeholders = ', '.join([f":{field}_{i}" for i in range(len(value))])
                    conditions.append(f"{field} IN ({placeholders})")
            elif isinstance(value, dict):
                # Handle range queries
                if "min" in value and value["min"] is not None:
                    conditions.append(f"{field} >= :min_{field}")
                if "max" in value and value["max"] is not None:
                    conditions.append(f"{field} <= :max_{field}")
            else:
                conditions.append(f"{field} = :{field}")
                
        return conditions
    
    def _build_filter_params(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build parameter dictionary for SQL query from filters.
        
        Args:
            filters: Dictionary of field names and values
            
        Returns:
            Flattened parameter dictionary for SQL execution
        """
        params = {}
        
        for field, value in filters.items():
            if value is None:
                continue
                
            if isinstance(value, list):
                for i, item in enumerate(value):
                    params[f"{field}_{i}"] = item
            elif isinstance(value, dict):
                if "min" in value and value["min"] is not None:
                    params[f"min_{field}"] = value["min"]
                if "max" in value and value["max"] is not None:
                    params[f"max_{field}"] = value["max"]
            else:
                params[field] = value
                
        return params