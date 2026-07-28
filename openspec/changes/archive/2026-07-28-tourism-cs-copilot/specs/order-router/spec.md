## ADDED Requirements

### Requirement: Router dispatches order queries by product category

The system SHALL route `get_order` calls to the correct backend mock system based on the ticket's `category` field.

#### Scenario: Route flight order query
- **WHEN** `get_order` is called for an order under category "机票"
- **THEN** Router dispatches the call to Flight OMS Mock and returns flight booking details including: flight_number, departure_time, arrival_time, fare_basis, price, passenger_name, booking_status

#### Scenario: Route hotel order query
- **WHEN** `get_order` is called for an order under category "酒店"
- **THEN** Router dispatches the call to Hotel OMS Mock and returns hotel booking details including: hotel_name, check_in, check_out, room_type, price, guest_name, booking_status

#### Scenario: Route train order query
- **WHEN** `get_order` is called for an order under category "火车"
- **THEN** Router dispatches the call to Train OMS Mock and returns train ticket details including: train_number, departure_time, seat_type, price, passenger_name, ticket_status

#### Scenario: Route ride-hailing order query
- **WHEN** `get_order` is called for an order under category "打车"
- **THEN** Router dispatches the call to Ride OMS Mock and returns ride order details including: driver_name, pickup_location, dropoff_location, scheduled_time, actual_time, price, order_status

### Requirement: Router dispatches customer queries to CRM

The system SHALL route `get_customer` calls to the CRM Mock system.

#### Scenario: Retrieve customer profile
- **WHEN** `get_customer("10086")` is called
- **THEN** CRM Mock returns customer profile including: customer_id, name, vip_level, contact, registration_date, total_orders, complaint_history

### Requirement: Router dispatches policy queries by category

The system SHALL route `get_policy` calls to the Policy Mock system, filtered by product category.

#### Scenario: Retrieve flight refund policy
- **WHEN** `get_policy(category="机票", issue_type="退票")` is called
- **THEN** Policy Mock returns flight-specific refund rules including fare basis tiers, time windows, and fee percentages

#### Scenario: Retrieve hotel cancellation policy
- **WHEN** `get_policy(category="酒店", issue_type="取消")` is called
- **THEN** Policy Mock returns hotel-specific cancellation rules including check-in deadline, penalty tiers, and VIP exceptions

### Requirement: Agent sees only generic tool interfaces

The system SHALL expose generic tool interfaces to the Agent (e.g., `get_order(order_id)`) without category-specific variants.

#### Scenario: Agent calls get_order without needing to know category
- **WHEN** Agent calls `get_order("ORD-001")`
- **THEN** The Router internally determines the category from prior context and dispatches correctly, without Agent needing to specify the category parameter

### Requirement: Adding a new product category requires only Router registration

The system SHALL support adding new product categories by registering a new mapping in the Router configuration, without modifying Agent logic or tool interfaces.

#### Scenario: Add "游轮" category
- **WHEN** "游轮" category is registered in Router config with its OMS Mock endpoint
- **THEN** `get_order` calls for tickets with category "游轮" are automatically routed to the new system
