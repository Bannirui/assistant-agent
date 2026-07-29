from .base import BaseCalculator


class HotelCancellationCalculator(BaseCalculator):
    def _validate_order(self, order: dict):
        if order.get("product_type") != "酒店":
            raise ValueError("Not a hotel order")

    def _get_base_fee_rate(self, order: dict) -> float:
        from datetime import datetime
        # 入住时间
        checkin_str = order.get("check_in", "")
        # 入住时间
        checkin = datetime.fromisoformat(checkin_str)
        # 现在是入住前几个小时
        hours_before = (checkin - datetime.now()).total_seconds() / 3600

        if hours_before < 0:
            # 超过了入住时间 不退 也就是说收手续费全部 那么计算出来的退款金额就是0
            return 1.00
        elif hours_before < 24:
            return 0.50
        elif hours_before < 48:
            return 0.30
        else:
            return 0.00

    def _build_detail(
        self, order: dict, customer: dict,
        raw_rate: float, fee_rate: float, fee_amount: float, settle_amount: float,
    ) -> str:
        if fee_rate == 0:
            return "入住48h前免费取消 | 全额退款"
        elif fee_rate >= 1.0:
            return "已入住不可退款"
        return f"距入住不足{'24' if fee_rate == 0.50 else '48'}小时 | 取消费率{int(fee_rate * 100)}% | 退费¥{settle_amount}"
