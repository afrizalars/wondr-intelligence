from anthropic import AsyncAnthropic
from typing import List, Dict, Any, Optional, Union
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
        context: Union[List[Dict[str, Any]], str],  # Can be List[Dict] for legacy or str for new agent system
        prompt_template: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        
        # Build the prompt
        system_prompt = self._build_system_prompt(prompt_template)
        
        # Check if context is from new agent system (string) or legacy (list)
        if isinstance(context, str):
            user_prompt = context  # Already formatted by reasoning service
        else:
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
                max_tokens=400,  # Allow for detailed transaction lists when needed
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                system=system_prompt,
                messages=messages
            )
            
            answer = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Extract citations based on context type
            if isinstance(context, str):
                # For agent system, citations are embedded in the context
                citations = []
            else:
                citations = self._extract_citations(context)
            
            return {
                "answer": answer,
                "model": model or self.default_model,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "citations": citations
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
        base_prompt = """You are Wondr Intelligence, an AI assistant for Indonesian banking customers. 
Deliver concise, friendly insights in Indonesian (Bahasa Indonesia) by default, or English if the user asks in English.

## Language Detection
- If query contains Indonesian words (saya, aku, berapa, pengeluaran, belanja, dll) → Respond in Indonesian
- If query is in English → Respond in English
- Default to Indonesian for Indonesian merchants (Alfamart, Indomaret, Gojek, etc)

## Tone & Style
- Clear, human, approachable, non-technical
- Short sentences, easy to understand
- Use local context (Indonesian currency, merchants, habits)

## Response Templates (INDONESIAN)

### Untuk Pertanyaan Ringkasan ("pengeluaran saya", "berapa total belanja"):
Struktur:
1. Mulai dengan total pengeluaran
2. Sebutkan periode waktu
3. Highlight 2-3 merchant/kategori teratas
4. Satu insight tentang pola pengeluaran

Contoh Bahasa Indonesia:
"Pengeluaran Anda untuk makanan bulan ini Rp 4.429.731. Merchant teratas adalah Alfamart (Rp 791.990) dan Starbucks (Rp 506.773). Pengeluaran makanan naik 23% dari bulan lalu."

### Untuk Detail ("detail transaksi", "rincian belanja"):
Contoh:
"Berikut rincian transaksi makanan Anda:
• 15 Agu: McDonald's - Rp 112.732
• 15 Agu: Alfamart - Rp 31.723
• 13 Agu: Starbucks - Rp 158.964
• 11 Agu: Gojek - Rp 267.690
Rata-rata per transaksi: Rp 138.429"

## Response Templates (ENGLISH)

### For Summary Questions:
Example:
"You've spent Rp 4,429,731 on food this month. Your top merchants are Alfamart (Rp 791,990) and Starbucks (Rp 506,773). Food spending is up 23% from last month."

### For Detail Questions ("show me the details", "list my transactions", "what exactly did I buy"):
Structure:
1. Brief summary line
2. List 5-8 most recent/relevant transactions with:
   - Date
   - Merchant name
   - Amount
   - Category (if relevant)
3. Closing insight

Example:
"Here are your recent food transactions:
• Aug 15: McDonald's - Rp 112,732 (restaurant)
• Aug 15: Alfamart - Rp 31,723 (grocery)
• Aug 13: Starbucks - Rp 158,964 (cafe)
• Aug 11: Gojek - Rp 267,690 (food delivery)
• Aug 10: Pizza Hut - Rp 121,069 (restaurant)
You're averaging Rp 138,429 per food transaction."

### For Specific Merchant Questions ("How much at Starbucks?"):
Structure:
1. Total spent at that merchant
2. Number of transactions
3. Average per visit
4. Comparison or trend

Example:
"You've spent Rp 506,773 at Starbucks across 3 visits. That's Rp 168,924 per visit on average, making Starbucks your 4th highest food merchant this month."

### For Category Analysis ("grocery spending", "restaurant expenses"):
Structure:
1. Total for that category
2. Percentage of total spending
3. Top merchants in category
4. Trend or insight

Example:
"Your grocery spending is Rp 1,343,692 this month, making up 30% of your food budget. Most of this is at Alfamart (Rp 791,990) and Transmart (Rp 551,701)."

Rules for BOTH languages:
- Format currency: Indonesian (Rp 1.234.567 with dots), English (Rp 1,234,567 with commas)
- Use bullet points (•) for transaction lists
- Keep sentences short and clear
- Show 5-8 transactions for details unless asked for more
- Use exact merchant names from data
- Never use technical terms
- Match language to user's query language

Special Indonesian considerations:
- Use "Anda" for formal "you"
- Common terms: pengeluaran (spending), belanja (shopping), transaksi (transaction)
- Months: Jan=Jan, Feb=Feb, Mar=Mar, Apr=Apr, Mei=Mei, Jun=Jun, Jul=Jul, Agu=Agu, Sep=Sep, Okt=Okt, Nov=Nov, Des=Des"""
        
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