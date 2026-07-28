## ADDED Requirements

### Requirement: Calculator computes flight refund fees

The system SHALL calculate flight refund fees based on fare basis, time before departure, and VIP level.

#### Scenario: H-class ticket refunded 36 hours before departure by gold member
- **WHEN** `calculate_refund` receives order with fare_basis="H", departure in 36 hours, price=1560, and customer vip_level="gold"
- **THEN** Calculator returns: refundable=true, fee_rate=0.15, fee_amount=234, refund_amount=1326, detail="折扣舱退票费50% × 金卡半价 = 15%"

#### Scenario: Y-class ticket refunded 1 hour before departure
- **WHEN** `calculate_refund` receives order with fare_basis="Y", departure in 1 hour, price=2000, and customer vip_level="regular"
- **THEN** Calculator returns: refundable=true, fee_rate=0.20, fee_amount=400, refund_amount=1600, detail="起飞前2h内退票费20%"

#### Scenario: Special-fare ticket cannot be refunded
- **WHEN** `calculate_refund` receives order with fare_basis="T" (special fare), departure in any time, and any VIP level
- **THEN** Calculator returns: refundable=false, detail="特价舱位不可退票"

### Requirement: Calculator computes hotel cancellation fees

The system SHALL calculate hotel cancellation fees based on time before check-in, room type, and VIP level.

#### Scenario: Standard room cancelled 48 hours before check-in
- **WHEN** `calculate_refund` receives hotel order with room_type="standard", check_in in 48 hours, price=800, vip_level="regular"
- **THEN** Calculator returns: refundable=true, fee_rate=0.0, fee_amount=0, refund_amount=800, detail="入住48h前免费取消"

#### Scenario: Standard room cancelled 6 hours before check-in
- **WHEN** `calculate_refund` receives hotel order with room_type="standard", check_in in 6 hours, price=800, vip_level="regular"
- **THEN** Calculator returns: refundable=true, fee_rate=0.50, fee_amount=400, refund_amount=400, detail="入住24h内取消收50%"

### Requirement: Calculator is called by Agent but Agent does not produce the result

The system SHALL return calculation results from the `calculate_refund` tool as deterministic outputs, and Agent SHALL use the returned values verbatim in its output.

#### Scenario: Agent uses calculator output in reply
- **WHEN** Calculator returns refund_amount=234
- **THEN** Agent's reply template SHALL contain the value "234" exactly as returned by the calculator, not a rounded or LLM-generated approximation

#### Scenario: Calculator returns non-refundable
- **WHEN** Calculator returns refundable=false
- **THEN** Agent SHALL generate reply explaining the ticket cannot be refunded, and SHALL NOT suggest any refund action button

### Requirement: Calculator supports extensible product types

The system SHALL support adding calculation rules for new product types without modifying existing calculator logic.

#### Scenario: Add train ticket refund calculation
- **WHEN** Developer registers a new `TrainRefundCalculator` implementing the `BaseCalculator` interface
- **THEN** `calculate_refund` calls the train calculator for orders of category "火车" without changes to other calculator implementations
