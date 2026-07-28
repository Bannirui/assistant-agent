## ADDED Requirements

### Requirement: Workstation has ticket input and analysis trigger

The system SHALL provide a ticket ID input field and an analysis trigger button in the workstation header.

#### Scenario: Agent submits a ticket ID for analysis
- **WHEN** Customer service agent enters ticket ID "TK-20240728-00123" and clicks "分析" (Analyze)
- **THEN** System calls the Copilot API with the ticket ID and displays a loading state in the right panel

#### Scenario: Invalid ticket ID shows error
- **WHEN** Customer service agent submits an invalid ticket ID
- **THEN** System displays an error message in the right panel indicating the ticket was not found

### Requirement: Left panel displays conversation view

The system SHALL provide a conversation panel on the left side showing customer messages and agent reply input.

#### Scenario: Display customer conversation
- **WHEN** A ticket is loaded
- **THEN** Left panel shows the customer's original complaint message(s) and provides a text input area for the agent to compose or edit replies

### Requirement: Right panel shows Copilot analysis results

The system SHALL display Copilot analysis results in the right panel, organized into clearly labeled sections.

#### Scenario: Display complete analysis for a ticket
- **WHEN** Copilot analysis completes successfully
- **THEN** Right panel displays: intent and risk summary at top, suggested reply in an editable text area with [Copy] and [Send] buttons, order snapshot card, suggested action buttons, and reference information at bottom

#### Scenario: Display analysis with warnings
- **WHEN** Analysis includes risk warnings (e.g., "12315投诉倾向")
- **THEN** Right panel highlights warnings with a distinct visual treatment (e.g., red/orange banner) to draw agent attention

### Requirement: Suggested reply can be copied or edited

The system SHALL allow the agent to copy the suggested reply to clipboard or edit it before sending.

#### Scenario: Agent copies suggested reply
- **WHEN** Agent clicks [Copy] on the suggested reply
- **THEN** The reply text is copied to clipboard

#### Scenario: Agent edits and sends reply
- **WHEN** Agent clicks [编辑后发送] (Edit and Send)
- **THEN** The suggested reply is populated into the left panel's message input area, where the agent can edit before sending

### Requirement: Suggested actions are rendered as clickable buttons

The system SHALL render suggested actions from the Copilot output as styled buttons, each displaying its label and optional parameters.

#### Scenario: Render refund action button
- **WHEN** Suggested action is `{type: "refund", label: "发起退款 ¥234"}`
- **THEN** A button [发起退款 ¥234] is rendered; clicking it navigates the agent to the refund system with pre-filled amount

#### Scenario: Render escalate action button
- **WHEN** Suggested action is `{type: "escalate", label: "升级主管"}`
- **THEN** A button [升级主管] is rendered; clicking it opens an escalation dialog

### Requirement: Order snapshot displays key order information

The system SHALL display a condensed order information card showing the most relevant order details.

#### Scenario: Display flight order snapshot
- **WHEN** Order details include a flight booking
- **THEN** Order snapshot card shows: flight_number, departure_time, fare_basis, price, passenger_name, booking_status

#### Scenario: Display hotel order snapshot
- **WHEN** Order details include a hotel booking
- **THEN** Order snapshot card shows: hotel_name, check_in, check_out, room_type, price, guest_name, booking_status

### Requirement: Analysis can be re-triggered

The system SHALL allow the agent to re-trigger analysis for the same ticket, for example after additional information becomes available.

#### Scenario: Agent re-analyzes ticket
- **WHEN** Agent clicks "重新分析" (Re-analyze) button
- **THEN** System re-runs the full Copilot analysis pipeline and updates the right panel with fresh results
