from anthropic import AsyncAnthropic
from typing import List, Dict, Any, Optional
from app.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-haiku-20240307"  # Fast, cost-effective
        
    async def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        prompt_template: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        
        # Build the prompt
        system_prompt = self._build_system_prompt(prompt_template)
        user_prompt = self._build_user_prompt(query, context)
        
        # Prepare messages
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 exchanges
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = await self.client.messages.create(
                model=model or self.default_model,
                max_tokens=200,  # Shorter responses for Apple Intelligence style
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                system=system_prompt,
                messages=messages
            )
            
            answer = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return {
                "answer": answer,
                "model": model or self.default_model,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "citations": self._extract_citations(context)
            }
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your request.",
                "error": str(e),
                "model": model or self.default_model,
                "latency_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000)
            }
    
    def _build_system_prompt(self, template: Optional[str] = None) -> str:
        base_prompt = """You are an AI assistant that delivers concise, friendly, and data-driven insights in a clean, natural language style similar to Apple Intelligence.

Tone: Clear, human, approachable, and non-technical.
Sentence length: Short and easy to scan.
Formatting: Use plain text, no extra decoration unless specified.

Structure:
1. Start with the most important number or fact.
2. Compare it with a relevant baseline (e.g., last month, average, target).
3. Give one short contextual insight or takeaway.

Rules:
- No jargon or overly complex terms.
- Always format currency amounts in Indonesian Rupiah (Rp) with proper thousand separators.
- Use everyday language ("more than", "less than", "up from", "makes up X%").
- Avoid unnecessary filler words.
- Never explain how you calculated — just give the result confidently.
- Keep responses to 2-3 sentences maximum.
- All monetary values are in IDR (Indonesian Rupiah) - always use "Rp" prefix.
- Format large numbers with commas as thousand separators (e.g., Rp 2,036,100.41).

Example style:
"You've spent Rp 31,910 at Starbucks this month, which is Rp 9,000 more than last month. Starbucks makes up 12% of your total Food and Drink spending this month."

When analyzing transactions:
- Focus on the key metric first
- Make one meaningful comparison
- Add one insight that matters
- Always use Rp for currency amounts"""
        
        if template:
            return f"{base_prompt}\n\nAdditional context:\n{template}"
        return base_prompt
    
    def _build_user_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        prompt = f"Question: {query}\n\n"
        prompt += "Data:\n"
        
        # Group transactions by type for better context
        transactions = []
        knowledge = []
        
        for item in context[:10]:
            if item.get("source") == "cif":
                transactions.append(item)
            else:
                knowledge.append(item)
        
        # Add transaction data
        if transactions:
            prompt += "\nTransactions (all amounts in IDR):\n"
            for item in transactions:
                text = item.get('text', '')
                # Ensure currency is mentioned if there's an amount
                if 'amount' in text.lower() or any(char.isdigit() for char in text):
                    if 'IDR' not in text and 'Rp' not in text:
                        text = text.replace('Amount:', 'Amount (IDR):')
                prompt += f"- {item.get('title', 'Transaction')}: {text}"
                if item.get('metadata'):
                    metadata = item['metadata']
                    if isinstance(metadata, dict) and 'currency' in metadata:
                        prompt += f" (Currency: {metadata['currency']})"
                    else:
                        prompt += f" ({metadata})"
                prompt += "\n"
        
        # Add knowledge data
        if knowledge:
            prompt += "\nContext:\n"
            for item in knowledge:
                prompt += f"- {item.get('text', '')}\n"
        
        prompt += "\nIMPORTANT: All amounts are in Indonesian Rupiah (IDR). Format them with 'Rp' prefix."
        prompt += "\nProvide a brief, data-driven response following the style guidelines."
        return prompt
    
    def _extract_citations(self, context: List[Dict[str, Any]]) -> List[Dict]:
        citations = []
        for item in context[:5]:  # Top 5 citations
            citation = {
                "source": item.get("source"),
                "title": item.get("title") or item.get("filename"),
                "text_snippet": item.get("text", "")[:200],
                "similarity_score": item.get("similarity_score", 0)
            }
            citations.append(citation)
        return citations
    
    async def check_content_safety(self, text: str) -> Dict[str, Any]:
        """Check if content is safe using Claude's built-in safety features"""
        try:
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0,
                system="You are a content safety classifier. Analyze if the text contains harmful, inappropriate, or sensitive content. Respond with only: SAFE or UNSAFE followed by a brief reason.",
                messages=[{"role": "user", "content": f"Analyze this text: {text}"}]
            )
            
            result = response.content[0].text
            is_safe = result.startswith("SAFE")
            
            return {
                "is_safe": is_safe,
                "reason": result.split(":", 1)[1].strip() if ":" in result else ""
            }
        except Exception as e:
            logger.error(f"Safety check error: {e}")
            return {"is_safe": True, "reason": "Safety check unavailable"}

llm_service = LLMService()