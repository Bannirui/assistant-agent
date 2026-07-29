from .base import BaseCalculator


class FlightRefundCalculator(BaseCalculator):
    def _validate_order(self, order: dict):
        if order.get("product_type") != "机票":
            raise ValueError("Not a flight order")

    def _get_base_fee_rate(self, order: dict) -> float:
        from datetime import datetime

        # 仓位 Y全价 H/K经济折扣价 L低折扣 T特价
        fare_basis = order.get("fare_basis", "Y")
        # 航班时间
        departure_str = order.get("departure_time", "")
        departure = datetime.fromisoformat(departure_str)
        # 距离起飞还有多久 >0还没有起飞 距离航班还有x小时 <0已经起飞了 不能退了或者收取高昂的手续费
        hours_before = (departure - datetime.now()).total_seconds() / 3600
        # 二维表 舱位*距离起飞时间
        FARE_TABLE = [
            # 起飞前24H [2,24) [0,2) 已经起飞
            [0.05, 0.10, 0.20, 0.50],  # 舱位Y 全价
            [0.30, 0.50, 0.80, 1.00],  # 舱位H 经济折扣
            [0.30, 0.50, 0.80, 1.00],  # 舱位K 经济折扣
            [0.50, 0.70, 1.00, 1.00],  # 舱位L 低折扣
            [1.00, 1.00, 1.00, 1.00],  # 舱位T 特价
        ]
        FARE_BASIS_IDX = {"Y": 0, "H": 1, "K": 2, "L": 3, "T": 4}
        # 舱位映射到二维表的行号
        row = FARE_BASIS_IDX.get(fare_basis, 1)
        # 起飞时间映射到二维表的列号
        col = 0
        if hours_before < 0:
            col = 3
        elif hours_before < 2:
            col = 2
        elif hours_before < 24:
            col = 1
        # 手续费的费率
        return FARE_TABLE[row][col]

    def _build_detail(
        self, order: dict, customer: dict,
        raw_rate: float, fee_rate: float, fee_amount: float, settle_amount: float,
    ) -> str:
        r"""
        告诉用户的文案信息
        :param order:
        :param customer:
        :param raw_rate: 原始的费率 不含VIP折扣
        :param fee_rate: 最终的费率 如果是会员 已经是打完折之后的费率了
        :param fee_amount:
        :param settle_amount:
        :return:
        """
        # 仓位
        fare_basis = order.get("fare_basis", "?")
        # 会员等级
        vip = customer.get("vip_level", "regular")

        if fee_rate >= 1.0:
            # 手续费已经超过订单价了 没法退
            return f"特价舱位{fare_basis}不可退票"

        parts = [
            f"{fare_basis}舱位退票费{int(raw_rate * 100)}%",
        ]
        if vip in ("gold", "platinum"):
            parts.append(f"{self._vip_name(vip)}会员享受{self._vip_discount_name(vip)}")
        parts.append(f"实际退票费率{int(fee_rate * 100)}%")
        parts.append(f"退费¥{settle_amount}")
        return " | ".join(parts)

    @staticmethod
    def _vip_name(vip: str) -> str:
        r"""
        vip的中文描述
        :param vip: 会员等级
        :return: 对应中文描述
        """
        return {"gold": "金卡", "platinum": "白金卡", "regular": "普通"}.get(vip, vip)

    @staticmethod
    def _vip_discount_name(vip: str) -> str:
        r"""
        vip的享有的折扣描述
        :param vip: 会员等级
        :return: 享受的权益描述
        """
        return {"gold": "退票费减半", "platinum": "免费退票", "regular": ""}.get(vip, "")
