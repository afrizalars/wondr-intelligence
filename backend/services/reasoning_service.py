"""
Reasoning Service for multi-agent query system.
Synthesizes results from multiple agents and formats for LLM processing.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ReasoningService:
    """
    Reasoning service that synthesizes multi-agent results.
    Formats data for LLM processing and generates coherent responses.
    """
    
    def __init__(self):
        """Initialize reasoning service."""
        self.logger = logging.getLogger(__name__)
        
        # Response templates for different query types
        self.response_templates = {
            "transaction_summary": self._format_transaction_summary,
            "customer_profile": self._format_customer_profile,
            "contact_list": self._format_contact_list,
            "spending_analysis": self._format_spending_analysis,
            "multi_source": self._format_multi_source_response
        }
    
    def synthesize_results(
        self,
        agent_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize results from multiple agents into a coherent response.
        
        Args:
            agent_results: Results from brain service with multiple agent outputs
            
        Returns:
            Synthesized response ready for LLM processing
        """
        start_time = datetime.utcnow()
        
        try:
            # Extract successful agent results
            successful_results = agent_results.get("results", [])
            failed_agents = agent_results.get("failed_agents", [])
            context = agent_results.get("context", {})
            
            if not successful_results:
                return self._format_no_results(agent_results)
            
            # Determine response type based on active agents and results
            response_type = self._determine_response_type(successful_results, context)
            
            # Format response based on type
            formatted_response = self._format_response(response_type, successful_results, context)
            
            # Add metadata
            synthesis_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return {
                "status": "success",
                "query": agent_results.get("query"),
                "cif": agent_results.get("cif"),
                "response_type": response_type,
                "data": formatted_response,
                "sources": self._extract_sources(successful_results),
                "metadata": {
                    "total_agents": len(agent_results.get("active_agents", [])),
                    "successful_agents": len(successful_results),
                    "failed_agents": len(failed_agents),
                    "synthesis_time_ms": synthesis_time_ms,
                    "total_time_ms": agent_results.get("total_execution_time_ms", 0) + synthesis_time_ms
                },
                "llm_context": self._prepare_llm_context(formatted_response, context),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Reasoning synthesis failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "query": agent_results.get("query"),
                "cif": agent_results.get("cif"),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _determine_response_type(
        self,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """
        Determine the type of response based on agent results.
        
        Args:
            results: List of successful agent results
            context: Query context
            
        Returns:
            Response type identifier
        """
        # Count agent types
        agent_types = [r.get("agent") for r in results]
        
        # Check query intent from context
        query_text = context.get("query", "").lower()
        
        # Determine based on agent combination and query
        if len(agent_types) > 1:
            return "multi_source"
        elif "transactions" in agent_types:
            if any(word in query_text for word in ["total", "spending", "breakdown", "analysis"]):
                return "spending_analysis"
            else:
                return "transaction_summary"
        elif "customers" in agent_types:
            return "customer_profile"
        elif "contact" in agent_types:
            return "contact_list"
        else:
            return "multi_source"
    
    def _format_response(
        self,
        response_type: str,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format response based on type.
        
        Args:
            response_type: Type of response to format
            results: Agent results
            context: Query context
            
        Returns:
            Formatted response
        """
        formatter = self.response_templates.get(response_type, self._format_multi_source_response)
        return formatter(results, context)
    
    def _format_transaction_summary(
        self,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format transaction summary response."""
        transaction_data = {}
        
        for result in results:
            if result.get("agent") == "transactions" and "results" in result:
                data = result["results"]
                
                if data.get("type") == "aggregation":
                    transaction_data["summary"] = data.get("summary", {})
                elif data.get("type") == "breakdown":
                    transaction_data["breakdown"] = data.get("items", [])
                    transaction_data["breakdown_count"] = data.get("total_groups", 0)
                elif data.get("type") == "search":
                    transaction_data["transactions"] = data.get("transactions", [])
                    transaction_data["transaction_count"] = data.get("count", 0)
                elif data.get("type") == "detail":
                    transaction_data["transaction_detail"] = data.get("transaction")
        
        # Add date range context if available
        if "date_range" in context:
            transaction_data["period"] = {
                "start": context["date_range"]["start"].isoformat() if hasattr(context["date_range"]["start"], "isoformat") else str(context["date_range"]["start"]),
                "end": context["date_range"]["end"].isoformat() if hasattr(context["date_range"]["end"], "isoformat") else str(context["date_range"]["end"])
            }
        
        return transaction_data
    
    def _format_customer_profile(
        self,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format customer profile response."""
        profile_data = {}
        
        for result in results:
            if result.get("agent") == "customers" and "results" in result:
                data = result["results"]
                
                if data.get("type") == "profile":
                    profile_data["profile"] = data.get("customer", {})
                    profile_data["has_profile"] = data.get("has_profile", False)
                elif data.get("type") == "complete_profile":
                    profile_data["profile"] = data.get("customer", {})
                    profile_data["statistics"] = data.get("statistics", {})
                elif data.get("type") == "segment":
                    profile_data["profile"] = data.get("customer_profile", {})
                    profile_data["segment"] = data.get("segment", {})
        
        return profile_data
    
    def _format_contact_list(
        self,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format contact list response."""
        contact_data = {}
        
        for result in results:
            if result.get("agent") == "contact" and "results" in result:
                data = result["results"]
                
                if data.get("type") == "all_contacts":
                    contact_data["contacts"] = data.get("contacts", [])
                    contact_data["total_contacts"] = data.get("count", 0)
                elif data.get("type") == "frequent_contacts":
                    contact_data["frequent_contacts"] = data.get("contacts", [])
                    contact_data["statistics"] = data.get("statistics", {})
                elif data.get("type") == "recent_contacts":
                    contact_data["recent_contacts"] = data.get("contacts", [])
                    contact_data["recent_count"] = data.get("count", 0)
                elif data.get("type") == "contacts_by_bank":
                    contact_data["banks"] = data.get("banks", [])
                    contact_data["total_banks"] = data.get("total_banks", 0)
                elif data.get("type") == "contact_search":
                    contact_data["search_results"] = data.get("contacts", [])
                    contact_data["search_criteria"] = data.get("search_criteria", {})
        
        return contact_data
    
    def _format_spending_analysis(
        self,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format spending analysis response."""
        analysis_data = self._format_transaction_summary(results, context)
        
        # Add insights based on data
        if "summary" in analysis_data:
            summary = analysis_data["summary"]
            
            # Calculate insights
            insights = []
            
            if summary.get("total_spending"):
                insights.append({
                    "type": "spending_total",
                    "value": summary["total_spending"],
                    "description": f"Total spending amount"
                })
            
            if summary.get("avg_transaction_amount"):
                insights.append({
                    "type": "average_transaction",
                    "value": summary["avg_transaction_amount"],
                    "description": f"Average transaction amount"
                })
            
            if summary.get("unique_merchants"):
                insights.append({
                    "type": "merchant_diversity",
                    "value": summary["unique_merchants"],
                    "description": f"Number of unique merchants"
                })
            
            analysis_data["insights"] = insights
        
        # Add breakdown insights if available
        if "breakdown" in analysis_data:
            breakdown = analysis_data["breakdown"]
            if breakdown:
                # Find top categories/merchants
                top_items = breakdown[:3] if len(breakdown) >= 3 else breakdown
                analysis_data["top_spending"] = top_items
        
        return analysis_data
    
    def _format_multi_source_response(
        self,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format response combining multiple data sources."""
        combined_data = {}
        
        # Process each agent's results
        for result in results:
            agent = result.get("agent")
            
            if agent == "transactions":
                combined_data["transactions"] = self._format_transaction_summary([result], context)
            elif agent == "customers":
                combined_data["customer"] = self._format_customer_profile([result], context)
            elif agent == "contact":
                combined_data["contacts"] = self._format_contact_list([result], context)
        
        # Add cross-agent insights if multiple sources present
        if len(combined_data) > 1:
            combined_data["cross_insights"] = self._generate_cross_insights(combined_data)
        
        return combined_data
    
    def _generate_cross_insights(
        self,
        combined_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate insights across multiple data sources.
        
        Args:
            combined_data: Combined data from multiple agents
            
        Returns:
            List of cross-source insights
        """
        insights = []
        
        # Example: Combine customer profile with transaction data
        if "customer" in combined_data and "transactions" in combined_data:
            customer = combined_data["customer"].get("profile", {})
            transactions = combined_data["transactions"]
            
            if customer.get("risk_profile") and transactions.get("summary", {}).get("avg_transaction_amount"):
                insights.append({
                    "type": "risk_transaction_correlation",
                    "risk_profile": customer["risk_profile"],
                    "avg_transaction": transactions["summary"]["avg_transaction_amount"],
                    "description": "Customer risk profile and transaction patterns"
                })
        
        # Example: Combine contacts with transaction patterns
        if "contacts" in combined_data and "transactions" in combined_data:
            contacts = combined_data["contacts"]
            
            if contacts.get("frequent_contacts") and transactions.get("summary", {}).get("total_transactions"):
                insights.append({
                    "type": "transfer_activity",
                    "frequent_contacts_count": len(contacts.get("frequent_contacts", [])),
                    "total_transactions": transactions["summary"]["total_transactions"],
                    "description": "Transfer contact relationships and transaction volume"
                })
        
        return insights
    
    def _format_no_results(
        self,
        agent_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format response when no results are available."""
        return {
            "status": "no_results",
            "query": agent_results.get("query"),
            "cif": agent_results.get("cif"),
            "message": "No data found for the specified query",
            "failed_agents": agent_results.get("failed_agents", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_sources(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract data sources from agent results.
        
        Args:
            results: Agent results
            
        Returns:
            List of data sources
        """
        sources = []
        
        for result in results:
            if result.get("handled"):
                sources.append({
                    "agent": result.get("agent"),
                    "execution_time_ms": result.get("execution_time_ms"),
                    "timestamp": result.get("timestamp")
                })
        
        return sources
    
    def _prepare_llm_context(
        self,
        formatted_response: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare context for LLM processing.
        
        Args:
            formatted_response: Formatted response data
            context: Original query context
            
        Returns:
            LLM-ready context
        """
        llm_context = {
            "query_intent": self._infer_query_intent(context),
            "data_summary": self._create_data_summary(formatted_response),
            "response_guidelines": self._get_response_guidelines(context),
            "data": formatted_response
        }
        
        return llm_context
    
    def _infer_query_intent(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        Infer the intent of the query.
        
        Args:
            context: Query context
            
        Returns:
            Query intent description
        """
        query = context.get("query", "").lower()
        
        intents = []
        
        if any(word in query for word in ["total", "sum", "how much"]):
            intents.append("aggregation")
        if any(word in query for word in ["list", "show", "display"]):
            intents.append("listing")
        if any(word in query for word in ["analyze", "insights", "pattern"]):
            intents.append("analysis")
        if any(word in query for word in ["profile", "information", "details"]):
            intents.append("information")
        if any(word in query for word in ["compare", "versus", "difference"]):
            intents.append("comparison")
        
        return ", ".join(intents) if intents else "general_query"
    
    def _create_data_summary(
        self,
        formatted_response: Dict[str, Any]
    ) -> str:
        """
        Create a summary of the data for LLM.
        
        Args:
            formatted_response: Formatted response data
            
        Returns:
            Data summary string
        """
        summary_parts = []
        
        # Summarize available data types
        if "transactions" in formatted_response:
            trans_data = formatted_response["transactions"]
            if "transaction_count" in trans_data:
                summary_parts.append(f"{trans_data['transaction_count']} transactions found")
            if "summary" in trans_data:
                summary_parts.append("Transaction summary available")
        
        if "customer" in formatted_response:
            summary_parts.append("Customer profile data available")
        
        if "contacts" in formatted_response:
            contact_data = formatted_response["contacts"]
            if "total_contacts" in contact_data:
                summary_parts.append(f"{contact_data['total_contacts']} contacts found")
        
        return "; ".join(summary_parts) if summary_parts else "Data retrieved successfully"
    
    def _get_response_guidelines(
        self,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Get response guidelines for LLM.
        
        Args:
            context: Query context
            
        Returns:
            List of guidelines
        """
        guidelines = [
            "Provide a clear and concise answer to the user's query",
            "Use the data provided to support your response",
            "Format numbers appropriately (e.g., currency, percentages)",
            "Highlight key insights or patterns if relevant"
        ]
        
        # Add context-specific guidelines
        if "date_range" in context:
            guidelines.append("Mention the time period being analyzed")
        
        if "limit" in context:
            guidelines.append(f"Note that results are limited to {context['limit']} items")
        
        return guidelines
    
    def format_for_llm(
        self,
        synthesized_results: Dict[str, Any]
    ) -> str:
        """
        Format synthesized results as a prompt for LLM.
        
        Args:
            synthesized_results: Synthesized results from reasoning service
            
        Returns:
            Formatted prompt string for LLM
        """
        if synthesized_results.get("status") == "error":
            return f"An error occurred while processing the query: {synthesized_results.get('error')}"
        
        if synthesized_results.get("status") == "no_results":
            return "No data was found for your query. Please try with different parameters."
        
        # Build prompt
        prompt_parts = []
        
        # Add query context
        prompt_parts.append(f"Query: {synthesized_results.get('query')}")
        prompt_parts.append(f"Customer: {synthesized_results.get('cif')}")
        
        # Add data summary
        llm_context = synthesized_results.get("llm_context", {})
        query_intent = llm_context.get('query_intent', '')
        
        # Add specific instructions based on query intent
        if 'detailed_listing' in query_intent:
            prompt_parts.append("\n**IMPORTANT**: User wants DETAILED TRANSACTION INFORMATION.")
            prompt_parts.append("Format response with individual transactions showing:")
            prompt_parts.append("- Date, Merchant name, Amount (with Rp prefix)")
            prompt_parts.append("- Use bullet points for each transaction")
            prompt_parts.append("- Show 5-8 most relevant transactions")
        elif 'aggregation' in query_intent:
            prompt_parts.append("\n**IMPORTANT**: User wants SUMMARY INFORMATION.")
            prompt_parts.append("Provide totals and high-level insights without listing individual transactions.")
        
        prompt_parts.append(f"\nData Summary: {llm_context.get('data_summary')}")
        prompt_parts.append(f"Query Intent: {query_intent}")
        
        # Add formatted data
        prompt_parts.append("\n--- Retrieved Data ---")
        prompt_parts.append(json.dumps(synthesized_results.get("data", {}), indent=2, default=str))
        
        # Add response guidelines
        prompt_parts.append("\n--- Response Guidelines ---")
        for guideline in llm_context.get("response_guidelines", []):
            prompt_parts.append(f"- {guideline}")
        
        # Add instruction based on intent
        if 'detailed_listing' in query_intent:
            prompt_parts.append("\nProvide a response with detailed transaction listings as requested.")
        else:
            prompt_parts.append("\nProvide a helpful and informative response based on the data above.")
        
        return "\n".join(prompt_parts)


# Singleton instance
reasoning_service = ReasoningService()