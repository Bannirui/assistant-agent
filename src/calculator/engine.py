from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class CalculatorState(Enum):
    INIT = "init"
    FETCH_ORDER = "fetch_order"
    CHECK_RULES = "check_rules"
    APPLY_VIP = "apply_vip"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class RefundResult:
    refundable: bool
    fee_rate: float
    fee_amount: float
    refund_amount: float
    detail: str
    state: CalculatorState = CalculatorState.COMPLETE


class BaseCalculator(ABC):
    def calculate(self, order: dict, customer: dict) -> RefundResult:
        state = CalculatorState.INIT
        try:
            state = CalculatorState.FETCH_ORDER
            self._validate_order(order)

            state = CalculatorState.CHECK_RULES
            fee_rate = self._get_base_fee_rate(order)

            state = CalculatorState.APPLY_VIP
            fee_rate = self._apply_vip_discount(fee_rate, customer)

            state = CalculatorState.COMPLETE
            price = float(order.get("price", 0))
            fee_amount = round(price * fee_rate, 2)
            refund_amount = round(price - fee_amount, 2)
            refundable = fee_rate < 1.0

            return RefundResult(
                refundable=refundable,
                fee_rate=fee_rate,
                fee_amount=fee_amount,
                refund_amount=refund_amount,
                detail=self._build_detail(order, customer, fee_rate, fee_amount, refund_amount),
            )
        except Exception as e:
            return RefundResult(
                refundable=False,
                fee_rate=1.0,
                fee_amount=0,
                refund_amount=0,
                detail=f"Calculation error: {e}",
                state=CalculatorState.ERROR,
            )

    @abstractmethod
    def _validate_order(self, order: dict):
        ...

    @abstractmethod
    def _get_base_fee_rate(self, order: dict) -> float:
        ...

    def _apply_vip_discount(self, fee_rate: float, customer: dict) -> float:
        if fee_rate >= 1.0:
            return fee_rate
        vip = customer.get("vip_level", "regular")
        discounts = {"gold": 0.5, "platinum": 0.0, "regular": 1.0}
        discount = discounts.get(vip, 1.0)
        return fee_rate * discount

    @abstractmethod
    def _build_detail(
        self, order: dict, customer: dict,
        fee_rate: float, fee_amount: float, refund_amount: float,
    ) -> str:
        ...


class FlightRefundCalculator(BaseCalculator):
    def _validate_order(self, order: dict):
        if order.get("product_type") != "机票":
            raise ValueError("Not a flight order")

    def _get_base_fee_rate(self, order: dict) -> float:
        from datetime import datetime

        fare_basis = order.get("fare_basis", "Y")
        departure_str = order.get("departure_time", "")
        departure = datetime.fromisoformat(departure_str)
        hours_before = (departure - datetime.now()).total_seconds() / 3600

        fee_table = {
            "Y": {"before_24h": 0.05, "between_2h_24h": 0.10, "within_2h": 0.20, "after_departure": 0.50},
            "H": {"before_24h": 0.30, "between_2h_24h": 0.50, "within_2h": 0.80, "after_departure": 1.00},
            "K": {"before_24h": 0.30, "between_2h_24h": 0.50, "within_2h": 0.80, "after_departure": 1.00},
            "L": {"before_24h": 0.50, "between_2h_24h": 0.70, "within_2h": 1.00, "after_departure": 1.00},
            "T": {"before_24h": 1.00, "between_2h_24h": 1.00, "within_2h": 1.00, "after_departure": 1.00},
        }

        tiers = fee_table.get(fare_basis, fee_table["H"])

        if hours_before < 0:
            return tiers["after_departure"]
        elif hours_before < 2:
            return tiers["within_2h"]
        elif hours_before < 24:
            return tiers["between_2h_24h"]
        else:
            return tiers["before_24h"]

    def _build_detail(
        self, order: dict, customer: dict,
        fee_rate: float, fee_amount: float, refund_amount: float,
    ) -> str:
        fare_basis = order.get("fare_basis", "?")
        vip = customer.get("vip_level", "regular")
        price = order.get("price", 0)

        if fee_rate >= 1.0:
            return f"特价舱位{fare_basis}不可退票"

        parts = [
            f"{fare_basis}舱位退票费{int(fee_rate * 100 / self._vip_multiplier(vip))}%",
        ]
        if vip in ("gold", "platinum"):
            parts.append(f"{self._vip_name(vip)}会员享受{self._vip_discount_name(vip)}")
        parts.append(f"实际退票费率{int(fee_rate * 100)}%")
        parts.append(f"退费¥{refund_amount}")
        return " × ".join(parts) if len(parts) == 1 else " | ".join(parts)

    @staticmethod
    def _vip_multiplier(vip: str) -> float:
        return {"gold": 0.5, "platinum": 0.0, "regular": 1.0}.get(vip, 1.0)

    @staticmethod
    def _vip_name(vip: str) -> str:
        return {"gold": "金卡", "platinum": "白金卡", "regular": "普通"}.get(vip, vip)

    @staticmethod
    def _vip_discount_name(vip: str) -> str:
        return {"gold": "退票费减半", "platinum": "免费退票", "regular": ""}.get(vip, "")


class HotelCancellationCalculator(BaseCalculator):
    def _validate_order(self, order: dict):
        if order.get("product_type") != "酒店":
            raise ValueError("Not a hotel order")

    def _get_base_fee_rate(self, order: dict) -> float:
        from datetime import datetime

        checkin_str = order.get("check_in", "")
        checkin = datetime.fromisoformat(checkin_str)
        hours_before = (checkin - datetime.now()).total_seconds() / 3600

        if hours_before < 0:
            return 1.00
        elif hours_before < 24:
            return 0.50
        elif hours_before < 48:
            return 0.30
        else:
            return 0.00

    def _build_detail(
        self, order: dict, customer: dict,
        fee_rate: float, fee_amount: float, refund_amount: float,
    ) -> str:
        if fee_rate == 0:
            return "入住48h前免费取消 | 全额退款"
        elif fee_rate >= 1.0:
            return "已入住不可退款"
        return f"距入住不足{'24' if fee_rate == 0.50 else '48'}小时 | 取消费率{int(fee_rate * 100)}% | 退费¥{refund_amount}"


class CalculatorRegistry:
    def __init__(self):
        self._calculators: dict[str, BaseCalculator] = {}

    def register(self, category: str, calculator: BaseCalculator):
        self._calculators[category] = calculator

    def get(self, category: str) -> Optional[BaseCalculator]:
        return self._calculators.get(category)

    def calculate(self, category: str, order: dict, customer: dict) -> RefundResult:
        calculator = self.get(category)
        if not calculator:
            return RefundResult(
                refundable=False,
                fee_rate=1.0,
                fee_amount=0,
                refund_amount=0,
                detail=f"No calculator registered for category: {category}",
                state=CalculatorState.ERROR,
            )
        return calculator.calculate(order, customer)


calculator_registry = CalculatorRegistry()
calculator_registry.register("机票", FlightRefundCalculator())
calculator_registry.register("酒店", HotelCancellationCalculator())
