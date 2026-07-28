import pytest
from datetime import datetime, timedelta
from src.calculator.engine import (
    FlightRefundCalculator,
    HotelCancellationCalculator,
    CalculatorRegistry,
    calculator_registry,
    RefundResult,
    CalculatorState,
)


def _make_flight_order(fare_basis="Y", hours_before=36, price=1560.0):
    departure = (datetime.now() + timedelta(hours=hours_before)).isoformat()
    return {
        "order_id": "ORD-F-TEST",
        "product_type": "机票",
        "fare_basis": fare_basis,
        "departure_time": departure,
        "price": price,
    }


def _make_hotel_order(hours_before=48, price=1200.0):
    checkin = (datetime.now() + timedelta(hours=hours_before)).isoformat()
    return {
        "order_id": "ORD-H-TEST",
        "product_type": "酒店",
        "check_in": checkin,
        "price": price,
    }


def _make_customer(vip="regular"):
    return {"customer_id": "C-TEST", "vip_level": vip, "name": "Test"}


class TestFlightRefundCalculator:
    def test_y_class_before_24h_regular(self):
        calc = FlightRefundCalculator()
        order = _make_flight_order("Y", 36, 1560)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert result.refundable
        assert result.fee_rate == 0.05
        assert result.fee_amount == 78.0
        assert result.refund_amount == 1482.0
        assert result.state == CalculatorState.COMPLETE

    def test_h_class_before_24h_regular(self):
        calc = FlightRefundCalculator()
        order = _make_flight_order("H", 36, 2300)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert result.refundable
        assert result.fee_rate == 0.30
        assert result.fee_amount == 690.0
        assert result.refund_amount == 1610.0

    def test_h_class_before_24h_gold(self):
        calc = FlightRefundCalculator()
        order = _make_flight_order("H", 36, 2300)
        customer = _make_customer("gold")
        result = calc.calculate(order, customer)
        assert result.refundable
        assert result.fee_rate == 0.15
        assert result.fee_amount == 345.0
        assert result.refund_amount == 1955.0

    def test_y_class_within_2h(self):
        calc = FlightRefundCalculator()
        order = _make_flight_order("Y", 1, 2000)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert result.refundable
        assert result.fee_rate == 0.20
        assert result.fee_amount == 400.0
        assert result.refund_amount == 1600.0

    def test_t_class_non_refundable(self):
        calc = FlightRefundCalculator()
        order = _make_flight_order("T", 36, 500)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert not result.refundable
        assert result.fee_rate == 1.0

    def test_t_class_non_refundable_even_gold(self):
        calc = FlightRefundCalculator()
        order = _make_flight_order("T", 36, 500)
        customer = _make_customer("gold")
        result = calc.calculate(order, customer)
        assert not result.refundable
        assert result.fee_rate == 1.0


class TestHotelCancellationCalculator:
    def test_before_48h_full_refund(self):
        calc = HotelCancellationCalculator()
        order = _make_hotel_order(72, 1200)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert result.refundable
        assert result.fee_rate == 0.0
        assert result.fee_amount == 0.0
        assert result.refund_amount == 1200.0

    def test_between_24h_48h_30_percent(self):
        calc = HotelCancellationCalculator()
        order = _make_hotel_order(36, 1200)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert result.refundable
        assert result.fee_rate == 0.30
        assert result.fee_amount == 360.0
        assert result.refund_amount == 840.0

    def test_within_24h_50_percent(self):
        calc = HotelCancellationCalculator()
        order = _make_hotel_order(6, 800)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert result.refundable
        assert result.fee_rate == 0.50
        assert result.fee_amount == 400.0
        assert result.refund_amount == 400.0

    def test_after_checkin_no_refund(self):
        calc = HotelCancellationCalculator()
        order = _make_hotel_order(-2, 800)
        customer = _make_customer("regular")
        result = calc.calculate(order, customer)
        assert not result.refundable
        assert result.fee_rate == 1.0


class TestCalculatorRegistry:
    def test_flight_registered(self):
        calc = calculator_registry.get("机票")
        assert calc is not None
        assert isinstance(calc, FlightRefundCalculator)

    def test_hotel_registered(self):
        calc = calculator_registry.get("酒店")
        assert calc is not None
        assert isinstance(calc, HotelCancellationCalculator)

    def test_unknown_category(self):
        result = calculator_registry.calculate("游轮", {}, {})
        assert not result.refundable
        assert result.state == CalculatorState.ERROR
