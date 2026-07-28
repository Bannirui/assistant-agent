## 1. Project Scaffolding

- [x] 1.1 Initialize Python project with FastAPI, add dependencies (fastapi, uvicorn, openai, qdrant-client, langchain-core, httpx, pyyaml, python-dotenv)
- [x] 1.2 Create Docker Compose with backend service (Qdrant runs in-process via local mode, no separate container)
- [x] 1.3 Create project directory structure (src/ with modules: agent, router, sop, calculator, rag, mocks, api, workstation)
- [x] 1.4 Configure environment variables (.env.example with OPENAI_API_KEY, DB_URL, etc.) and settings loader

## 2. Mock External Systems

- [x] 2.1 Create Ticket System Mock API — GET /api/tickets/{ticket_id} returns structured ticket with category, issue_type, customer_id, related_orders, title, description, priority, status
- [x] 2.2 Create Flight OMS Mock — GET /api/mock/flight/orders/{order_id} returns flight booking details (flight_number, departure_time, fare_basis, price, passenger_name, status)
- [x] 2.3 Create Hotel OMS Mock — GET /api/mock/hotel/orders/{order_id} returns hotel booking details
- [x] 2.4 Create Train OMS Mock — GET /api/mock/train/orders/{order_id} returns train ticket details
- [x] 2.5 Create Ride OMS Mock — GET /api/mock/ride/orders/{order_id} returns ride order details
- [x] 2.6 Create CRM Mock — GET /api/mock/customers/{customer_id} returns customer profile (name, vip_level, contact, history)
- [x] 2.7 Create Policy Mock — GET /api/mock/policies?category=&issue_type= returns policy rules for given category
- [x] 2.8 Seed mock data for at least 2 scenarios per product category (机票/酒店/火车/打车)

## 3. Order Router

- [x] 3.1 Implement Router module with category-to-system mapping configuration
- [x] 3.2 Implement `get_order(order_id)` — routes to correct OMS Mock based on category (determined from ticket context)
- [x] 3.3 Implement `get_customer(customer_id)` — routes to CRM Mock
- [x] 3.4 Implement `get_policy(category, issue_type)` — routes to Policy Mock
- [x] 3.5 Write unit tests for Router covering all 4 product categories and unknown category fallback

## 4. SOP Engine

- [x] 4.1 Define SOP YAML schema (id, category, issue_types, steps, compensation_rules, templates, suggested_actions)
- [x] 4.2 Create SOP documents for at least 4 scenarios: flight refund dispute, hotel cancellation, ride driver late, train ticket change
- [x] 4.3 Implement SOP loader that reads YAML files from SOP directory into in-memory index on startup
- [x] 4.4 Implement `search_sop(category, issue_type)` — exact match first, partial match fallback, "no match" return
- [x] 4.5 Implement SOP reload endpoint POST /admin/sop/reload
- [x] 4.6 Write tests for SOP matching (exact match, partial match, no match)

## 5. Refund Calculator

- [x] 5.1 Define BaseCalculator abstract interface (method: calculate(order, customer) → RefundResult)
- [x] 5.2 Implement FlightRefundCalculator with fare basis × time × VIP rules (Y/H/K/L/T舱)
- [x] 5.3 Implement HotelCancellationCalculator with time-before-checkin × room_type × VIP rules
- [x] 5.4 Implement CalculatorRegistry that dispatches to correct calculator by category
- [x] 5.5 Implement `calculate_refund(order, customer)` tool function
- [x] 5.6 Write tests for each calculator with known inputs and expected outputs (edge cases: non-refundable, VIP discounts, time boundaries)

## 6. RAG Knowledge Base

- [x] 6.1 Configure Qdrant client in local mode with persistent storage path (no external service needed)
- [x] 6.2 Create knowledge base directory with sample company documents (退改政策.md, 客诉处理规范.md, etc.)
- [x] 6.3 Implement document chunker (split by sections/paragraphs with overlap)
- [x] 6.4 Implement embedding generation (call configured embedding API)
- [x] 6.5 Implement document ingestion pipeline: chunk → embed → store in Qdrant with source metadata
- [x] 6.6 Implement `search_knowledge(query, top_k=5)` — embed query → Qdrant search → return ranked chunks
- [x] 6.7 Implement ingestion trigger endpoint POST /admin/knowledge/ingest
- [x] 6.8 Write tests for search returning relevant results and empty results

## 7. Agent (ReAct Loop)

- [x] 7.1 Define Tool schemas (get_ticket, get_order, get_customer, get_policy, search_sop, calculate_refund, search_knowledge) using OpenAI function calling format
- [x] 7.2 Write System Prompt with role definition, tool usage rules, output format specification, and key constraints (no amount fabrication, read-only operations, SOP-priority-then-RAG)
- [x] 7.3 Implement ReAct loop: call LLM → parse function_call → execute tool → inject result → repeat until final response or max_iterations
- [x] 7.4 Implement output parser that extracts structured JSON from final LLM response (analysis, reply_template, suggested_actions, references, warnings)
- [x] 7.5 Implement max_iterations guard and graceful fallback on limit reached
- [x] 7.6 Write integration tests with mocked tool responses for key scenarios (price dispute, driver late, SOP match, SOP miss → RAG fallback)

## 8. Copilot API Endpoints

- [x] 8.1 Implement POST /api/copilot/analyze — accepts {ticket_id}, runs full Agent pipeline, returns structured analysis
- [x] 8.2 Implement GET /api/copilot/status — returns agent health and loaded components status
- [x] 8.3 Add request validation and error handling (invalid ticket_id, agent timeout, external system errors)
- [ ] 8.4 Add streaming support for real-time progress updates (optional, SSE based)

## 9. Frontend Workstation

- [x] 9.1 Initialize React + TypeScript project (Vite) with dependencies (zustand)
- [x] 9.2 Build Header component with ticket ID input, analyze button, and ticket summary display
- [x] 9.3 Build Left Panel — conversation view with customer message display and agent reply input area
- [x] 9.4 Build Right Panel — tabbed/sectioned layout for: intent/risk summary, suggested reply (with Copy/Edit-Send buttons), order snapshot card, suggested action buttons, reference info
- [x] 9.5 Implement state management (Zustand store) for ticket data, analysis results, loading states
- [x] 9.6 Connect frontend to Copilot API — submit ticket ID → display loading → render analysis results
- [x] 9.7 Implement Copy to clipboard and Edit-Then-Send functionality for suggested replies
- [x] 9.8 Implement action button rendering with click handlers
- [x] 9.9 Style workstation with clean, professional layout (CSS modules or Tailwind)

## 10. Integration and Polish

- [x] 10.1 Write end-to-end test: submit ticket ID → Agent analyzes → frontend displays results with correct actions and amounts
- [ ] 10.2 Verify Docker Compose starts backend service correctly, Qdrant data persists to local directory
- [x] 10.3 Add README with setup instructions and architecture overview
- [ ] 10.4 Performance check: ensure Agent completes analysis within acceptable time (<15s for typical ticket)
