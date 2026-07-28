## ADDED Requirements

### Requirement: Agent receives ticket ID and retrieves ticket details

The system SHALL accept a ticket ID as input and retrieve the full structured ticket from the existing ticket system API.

#### Scenario: Agent retrieves a valid ticket
- **WHEN** Agent receives ticket ID "TK-20240728-00123"
- **THEN** Agent calls `get_ticket("TK-20240728-00123")` and receives a structured ticket object containing: ticket_id, category, issue_type, customer_id, related_orders, title, description, priority, status

#### Scenario: Agent receives an invalid ticket ID
- **WHEN** Agent receives ticket ID "TK-INVALID"
- **THEN** System returns an error indicating ticket not found, and Agent informs the user that the ticket does not exist

### Requirement: Agent autonomously decides which tools to call

The system SHALL implement a ReAct loop where the LLM Agent decides which tools to invoke based on ticket content, without a predefined fixed pipeline.

#### Scenario: Ticket with related orders triggers order and customer lookup
- **WHEN** Agent retrieves a ticket with `related_orders: ["ORD-001"]` and `customer_id: "10086"`
- **THEN** Agent autonomously calls `get_order("ORD-001")` and `get_customer("10086")` in parallel

#### Scenario: Ticket with price-related issue triggers refund calculation
- **WHEN** Agent identifies the ticket issue_type involves price dispute or refund
- **THEN** Agent calls `calculate_refund(order_data, customer_data)` to get deterministic calculation results

#### Scenario: Ticket with common issue triggers SOP lookup
- **WHEN** Agent identifies the ticket issue_type matches a known SOP category
- **THEN** Agent calls `search_sop(category, issue_type)` to retrieve the structured SOP

#### Scenario: Ticket with unfamiliar issue triggers knowledge search
- **WHEN** Agent cannot find a matching SOP for the issue_type
- **THEN** Agent calls `search_knowledge(query)` to search the RAG knowledge base for relevant documents

### Requirement: Agent synthesizes final output for customer service agent

The system SHALL generate a structured output containing suggested reply, suggested actions, risk alerts, and reference information.

#### Scenario: Complete analysis for a price dispute ticket
- **WHEN** Agent has completed all tool calls for a price dispute ticket
- **THEN** System returns a JSON response containing: `analysis` (intent and risk summary), `reply_template` (suggested reply text), `suggested_actions` (list of action buttons with labels and parameters), `references` (order snapshot, policy excerpts), `warnings` (risk alerts)

#### Scenario: Suggested actions include amounts from calculation engine
- **WHEN** Agent output includes a refund action suggestion
- **THEN** The refund amount in the suggested action SHALL come from `calculate_refund` output, NOT from LLM generation

### Requirement: Agent respects operation depth boundary

The system SHALL only generate suggestions and SHALL NOT execute any write operations (refunds, cancellations, ticket status changes).

#### Scenario: Agent is prompted to execute a refund
- **WHEN** User asks Agent to "直接帮我退款"
- **THEN** Agent responds that it can only provide refund suggestions and amounts, not execute the refund

### Requirement: Agent handles errors gracefully

The system SHALL handle external system failures without crashing, and inform the user which information could not be retrieved.

#### Scenario: External system times out
- **WHEN** `get_order` call to OMS times out
- **THEN** Agent notes that order information is temporarily unavailable and continues analysis with available data, flagging the missing information

### Requirement: Agent has configurable iteration limit

The system SHALL limit the maximum number of tool-calling iterations to prevent infinite loops.

#### Scenario: Agent reaches iteration limit
- **WHEN** Agent exceeds the configured max_iterations (default: 10)
- **THEN** Agent stops further tool calls and synthesizes output with whatever information it has collected so far
