# Wondr Intelligence - AI Assistant Guidelines

## Project Overview
Wondr Intelligence is an AI-powered financial insights platform using a multi-agent query system to provide intelligent transaction analysis in Indonesian Rupiah (IDR).

## Response Style Guidelines

### Core Principles
- **Tone**: Clear, human, approachable, non-technical
- **Length**: Keep responses concise (2-3 sentences for summaries, 5-8 items for details)
- **Currency**: Always format as Rp with thousand separators (e.g., Rp 1,234,567)
- **Language**: Use everyday terms, avoid jargon

### Response Templates

#### 1. Summary Questions
**Triggers**: "show my spending", "how much did I spend", "total"

**Format**:
```
You've spent [TOTAL] on [CATEGORY] this [PERIOD].
Your top merchants are [MERCHANT1] ([AMOUNT1]) and [MERCHANT2] ([AMOUNT2]).
[ONE INSIGHT about spending pattern].
```

**Example**:
"You've spent Rp 4,429,731 on food this month. Your top merchants are Alfamart (Rp 791,990) and Starbucks (Rp 506,773). Food spending is up 23% from last month."

#### 2. Detail Questions
**Triggers**: "show details", "list transactions", "what exactly", "breakdown"

**Format**:
```
Here are your recent [CATEGORY] transactions:
" [DATE]: [MERCHANT] - [AMOUNT] ([CATEGORY])
" [DATE]: [MERCHANT] - [AMOUNT] ([CATEGORY])
" [DATE]: [MERCHANT] - [AMOUNT] ([CATEGORY])
[...up to 8 items]
[ONE CLOSING INSIGHT].
```

**Example**:
```
Here are your recent food transactions:
" Aug 15: McDonald's - Rp 112,732 (restaurant)
" Aug 15: Alfamart - Rp 31,723 (grocery)
" Aug 13: Starbucks - Rp 158,964 (cafe)
" Aug 11: Gojek - Rp 267,690 (food delivery)
You're averaging Rp 138,429 per food transaction.
```

#### 3. Merchant-Specific Questions
**Triggers**: "at [MERCHANT]", "from [MERCHANT]"

**Format**:
```
You've spent [TOTAL] at [MERCHANT] across [COUNT] visits.
That's [AVERAGE] per visit on average.
[COMPARISON or RANKING].
```

**Example**:
"You've spent Rp 506,773 at Starbucks across 3 visits. That's Rp 168,924 per visit on average, making Starbucks your 4th highest food merchant this month."

#### 4. Category Analysis
**Triggers**: "[CATEGORY] spending", "[CATEGORY] expenses"

**Format**:
```
Your [CATEGORY] spending is [TOTAL] this [PERIOD], making up [PERCENTAGE]% of your [PARENT_CATEGORY] budget.
Most of this is at [TOP_MERCHANT1] ([AMOUNT1]) and [TOP_MERCHANT2] ([AMOUNT2]).
```

**Example**:
"Your grocery spending is Rp 1,343,692 this month, making up 30% of your food budget. Most of this is at Alfamart (Rp 791,990) and Transmart (Rp 551,701)."

## Technical Implementation Notes

### Multi-Agent System
- **Brain Service**: Parses queries and routes to appropriate agents
- **Transaction Agent**: Handles spending, merchant, and transaction queries
- **Customer Agent**: Handles profile and demographic queries
- **Contact Agent**: Handles transfer contact queries
- **Reasoning Service**: Synthesizes multi-agent results

### Query Intent Detection
The system detects user intent to determine response format:
- `detailed_listing`: User wants transaction details
- `aggregation`: User wants summary totals
- `analysis`: User wants insights and patterns
- `comparison`: User wants comparative analysis

### Database Queries
- Direct SQL queries for structured data (no vector search)
- Optimized indexes on transaction_date, merchant_name, category, transaction_type
- Parallel agent execution for performance

### Testing Commands
```bash
# Run backend
cd backend && python main.py

# Test queries
"Show my food spending" -> Summary response
"Show me food transaction details" -> Detailed listing
"How much at Starbucks?" -> Merchant-specific
"Grocery expenses" -> Category analysis
```

## Important Reminders
1. Always use Rp prefix for Indonesian Rupiah
2. Format numbers with thousand separators
3. Show 5-8 transactions max for detail queries
4. Keep summaries to 2-3 sentences
5. Use bullet points (") for transaction lists
6. Include merchant names exactly as in database
7. Add category only when it adds value