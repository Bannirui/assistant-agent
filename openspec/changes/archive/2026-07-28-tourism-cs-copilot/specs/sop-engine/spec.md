## ADDED Requirements

### Requirement: SOP engine matches SOP by category and issue type

The system SHALL match a ticket to the correct SOP document using category and issue_type as composite keys.

#### Scenario: Exact match found
- **WHEN** `search_sop(category="打车", issue_type="司机迟到")` is called
- **THEN** SOP engine returns the matching SOP document containing: sop_id, title, steps, compensation rules (with conditions and values), templates (with keys and message texts), suggested_actions

#### Scenario: No exact match found
- **WHEN** `search_sop(category="打车", issue_type="行李丢失")` is called but no matching SOP exists
- **THEN** SOP engine returns a "no match" result with `matched: false`, signaling Agent to fall back to RAG knowledge search

#### Scenario: Partial match by category only
- **WHEN** `search_sop(category="机票", issue_type="unknown_issue")` is called
- **THEN** SOP engine returns the most general SOP for category "机票" if available, with a `match_confidence` indicating partial match

### Requirement: SOP documents contain structured compensation rules

The system SHALL define SOP compensation rules as structured condition-value pairs that can be programmatically evaluated.

#### Scenario: Match compensation based on wait time
- **WHEN** SOP "司机迟到" has compensation tiers: "<5min" → "致歉", "5-15min" → "10元券", "15-30min" → "20元券", ">30min" → "免单+50元券"
- **THEN** Given wait_time=20 minutes, the engine returns the "15-30min" tier: "20元券"

### Requirement: SOP documents contain reply templates

The system SHALL define SOP reply templates as keyed message texts with variable placeholders.

#### Scenario: Render reply template with customer data
- **WHEN** SOP template contains "您好{customer_name}，非常抱歉给您带来不便，已为您申请一张{coupon_amount}元打车券..."
- **THEN** With variables {customer_name: "张三", coupon_amount: "10"}, the rendered reply is: "您好张三，非常抱歉给您带来不便，已为您申请一张10元打车券..."

### Requirement: SOP documents support suggested action definitions

The system SHALL define suggested actions in SOP as structured objects with type, label, and parameters.

#### Scenario: SOP defines a re-dispatch action
- **WHEN** SOP "司机迟到" includes suggested_action `{type: "redispatch", label: "重新派单"}`
- **THEN** The frontend renders a [重新派单] button that, when clicked, navigates the agent to the ride dispatch system

### Requirement: SOP documents are loaded from YAML files

The system SHALL load SOP documents from YAML files in a designated directory, supporting version management via file system.

#### Scenario: Load all SOPs on startup
- **WHEN** System starts up
- **THEN** All YAML files in the SOP directory are loaded into an in-memory index, keyed by (category, issue_type)

#### Scenario: Reload SOPs without restart
- **WHEN** A new SOP YAML file is added to the directory
- **THEN** System supports a reload endpoint `POST /admin/sop/reload` that refreshes the in-memory index without service restart
