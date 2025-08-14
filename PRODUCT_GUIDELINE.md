# Product Guidelines - Wondr Intelligence

## Product Overview
Wondr Intelligence is an AI-powered financial insights platform that enables users to query their transaction data using natural language, providing instant, actionable insights about spending patterns in Indonesian Rupiah (IDR).

## Current Features (v1.0)

### 1. Authentication System
**Status**: ✅ Fully Implemented

#### Login Screen
- Apple-inspired glassmorphic design
- Email and password authentication
- JWT token-based sessions
- Animated gradient background
- "Forgot Password" link (UI only)

#### Registration Screen
- Full name, email, username, password fields
- Password strength indicator with visual feedback
- Real-time password match validation
- Glassmorphic card design with soft shadows
- Smooth transitions and animations

**User Flow**:
1. User lands on login page
2. New users click "Create Account" → Register page
3. Fill registration form with validation
4. Password strength shown in real-time
5. Submit → Auto-login → Redirect to Playground

### 2. Main Dashboard
**Status**: ✅ Fully Implemented

#### Navigation Sidebar
- **Playground** - Main search interface (Active)
- **Merchants** - Merchant catalog (Placeholder)
- **Guardrails** - Content moderation rules (Placeholder)
- **Prompt Templates** - Template management (Placeholder)
- **API Keys** - API key management (Placeholder)
- **Search History** - Query history viewer (Placeholder)
- **Global Knowledge** - Knowledge base (Placeholder)

#### Top Navigation Bar
- User profile menu
- Notifications icon (UI only)
- Settings access
- Logout functionality
- Collapsible sidebar toggle

### 3. Playground (Core Feature)
**Status**: ✅ Fully Implemented

#### Search Interface
**Components**:
- Natural language query input box
- CIF selector (Customer Identification)
- Suggested query chips
- Real-time search execution
- Response display area

**Suggested Queries**:
- "What are my spending trends?"
- "Show my top merchants"
- "Analyze my food expenses"
- "How much did I save last month?"
- "Show recent transactions"
- "What's my biggest expense category?"

#### Mobile Experience Preview
**Live iPhone Mockup Display**:
- Real-time transaction cards
- Merchant logos with gradient backgrounds
- Transaction amounts in Rupiah (Rp)
- Category badges
- Date grouping
- Search filtering
- Transaction details on tap

**Transaction Card Features**:
- Merchant name and logo
- Amount in IDR format
- Category classification
- Transaction date
- Booking status
- Location details (when available)

#### Intelligence Response Panel
**Response Structure**:
1. **AI Answer**: Natural language response with insights
2. **Transaction Details**: Auto-expanded when relevant
3. **Source Citations**: Vector search results
4. **Performance Metrics**:
   - Response latency (ms)
   - Model used (Claude Haiku)
   - Guardrail status

**Transaction Display**:
- Glass morphism cards
- Hover animations
- Category color coding
- Amount formatting with thousand separators
- Merchant iconography

### 4. Data Processing Pipeline
**Status**: ✅ Fully Implemented

#### Search Flow
1. **Query Input** → User enters natural language question
2. **Context Building** → CIF-based transaction retrieval
3. **Vector Search** → Semantic similarity matching
4. **LLM Processing** → Claude generates response
5. **Response Formatting** → Structured output with citations
6. **Transaction Enrichment** → Related transactions included

#### Supported Query Types
- **Spending Analysis**: "Show my spending patterns"
- **Merchant Queries**: "How much at Starbucks?"
- **Category Analysis**: "Food expenses this month"
- **Trend Detection**: "Am I spending more?"
- **Savings Insights**: "How much did I save?"
- **Transaction Search**: "Recent large purchases"

## User Experience Flow

### Primary User Journey
```
1. Landing → Login/Register
   ↓
2. Authentication → JWT Token
   ↓
3. Dashboard → Playground Default
   ↓
4. Query Input → Natural Language
   ↓
5. AI Response → Insights + Transactions
   ↓
6. Interactive Exploration → Filter/Details
```

### Query Interaction Flow
```
1. Type or Select Query
   ↓
2. Real-time Processing Indicator
   ↓
3. Animated Response Display
   ↓
4. Auto-expand Transaction Details
   ↓
5. Interactive Transaction Cards
   ↓
6. Source Citations Available
```

## Design System Implementation

### Visual Components
- **Glass Cards**: 70% white opacity with 8px blur
- **Gradient Backgrounds**: Purple to violet animated gradients
- **Pastel Accents**: Blue (#A4C8E7), Pink (#E7C8D2), Mint (#C8E7D5)
- **Typography**: SF Pro Display/Text, 16px base
- **Spacing**: 8px grid system
- **Animations**: <200ms transitions

### Interaction Patterns
- **Hover Effects**: Subtle elevation and glow
- **Focus States**: Pastel blue outline with glow
- **Loading States**: Skeleton screens with shimmer
- **Success Feedback**: Mint green indicators
- **Error States**: Soft pink backgrounds

## Technical Integration

### Frontend Architecture
```
React 18.3 + TypeScript
├── Authentication (Context API)
├── API Integration (Axios + React Query)
├── UI Components (Material-UI v6)
├── State Management (React Query)
└── Routing (React Router v6)
```

### Backend Services
```
FastAPI + PostgreSQL
├── Authentication Service (JWT)
├── Search Service (Vector + Semantic)
├── LLM Service (Anthropic Claude)
├── Embedding Service (Multilingual E5)
└── Transaction Service (PostgreSQL)
```

### Data Flow
```
User Query → API Gateway → Search Service
                ↓
        Vector Embeddings
                ↓
        Similarity Search
                ↓
        LLM Processing
                ↓
        Response Formatting
                ↓
        Frontend Display
```

## Current Limitations & Placeholders

### Placeholder Features (UI Only)
1. **Merchants Management** - Catalog interface pending
2. **Guardrails Configuration** - Rules editor pending
3. **Prompt Templates** - Template builder pending
4. **API Keys Management** - Key generation pending
5. **Search History** - History viewer pending
6. **Global Knowledge** - Knowledge base pending

### Known Constraints
- Single CIF support (CIF00000001)
- Indonesian Rupiah only
- 8 transaction display limit
- No real-time data sync
- No export functionality
- No collaborative features

## Performance Specifications

### Response Times
- **Login/Register**: <500ms
- **Query Processing**: <2s average
- **Transaction Display**: Instant (cached)
- **Page Navigation**: <200ms
- **Animation Duration**: 150-200ms

### Capacity
- **Concurrent Users**: 100 (current)
- **Query Rate**: 10/second
- **Transaction Records**: 10,000 per CIF
- **Vector Dimensions**: 768
- **Cache Duration**: Session-based

## Security Features

### Implemented
- JWT authentication with expiry
- Password hashing (bcrypt)
- CORS protection
- SQL injection prevention
- XSS protection

### Pending
- Two-factor authentication
- API rate limiting
- Audit logging
- Data encryption at rest
- Session management

## Localization

### Current Support
- **Currency**: Indonesian Rupiah (IDR/Rp)
- **Language**: English interface
- **Date Format**: International
- **Number Format**: Thousand separators

### Future Expansion
- Bahasa Indonesia translation
- Multi-currency support
- Regional date formats
- Local payment methods

## Success Metrics

### User Engagement
- **Active Sessions**: Track daily usage
- **Query Volume**: Measure search frequency
- **Response Quality**: User satisfaction
- **Feature Adoption**: Navigation patterns

### System Performance
- **Uptime**: 99.9% target
- **Response Time**: <2s p95
- **Error Rate**: <1%
- **Query Success**: >95%

## Roadmap Priorities

### Phase 1 (Current) ✅
- Core search functionality
- Authentication system
- Transaction display
- Mobile preview

### Phase 2 (Next)
- Merchant management
- Search history
- Export functionality
- Real guardrails

### Phase 3 (Future)
- Multi-user support
- Collaborative features
- Advanced analytics
- API marketplace

## Development Guidelines

### Code Standards
- TypeScript strict mode
- Component-based architecture
- Responsive design first
- Accessibility compliance

### Testing Requirements
- Component rendering tests
- API integration tests
- Authentication flow tests
- Performance benchmarks

### Documentation
- API documentation (OpenAPI)
- Component storybook
- User guides
- Developer setup

---

*Last Updated: January 2025*
*Version: 1.0*
*Status: Production Ready (Core Features)*