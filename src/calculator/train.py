from .base import BaseCalculator


class TrainChangeCalculator(BaseCalculator):
    def _validate_order(self, order: dict):
        if order.get("product_type") != "火车票":
            raise ValueError("Not a train order")

    def _get_base_fee_rate(self, order: dict) -> float:
        from datetime import datetime

        departure_str = order.get("departure_time", "")
        departure = datetime.fromisoformat(departure_str)
        hours_before = (departure - datetime.now()).total_seconds() / 3600

        if hours_before < 0:
            return 1.00
        elif hours_before < 2:
            return 1.20
        elif hours_before < 24:
            return 0.80
        elif hours_before < 48:
            return 0.50
        else:
            return 0.30

    def _build_detail(
        self, order: dict, customer: dict,
        raw_rate: float, fee_rate: float, fee_amount: float, settle_amount: float,
    ) -> str:
        if settle_amount >= 0:
            return f"改签手续费¥{fee_amount} | 退还¥{settle_amount}"
        else:
            return f"改签手续费¥{fee_amount} | 需补差价¥{-settle_amount}"
