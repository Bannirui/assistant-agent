from typing import Optional

from .base import BaseCalculator, CalculatorState, CalcResult
from .flight import FlightRefundCalculator
from .hotel import HotelCancellationCalculator
from .train import TrainChangeCalculator


class CalculatorRegistry:
    def __init__(self):
        # 缓存品类跟对应产品的退改计算器实现
        self._calculators: dict[str, BaseCalculator] = {}

    def register(self, category: str, calculator: BaseCalculator):
        r"""
        服务注册
        :param category: 品类 机票/酒店
        :param calculator: 这个品类的退改实现实例
        """
        self._calculators[category] = calculator

    def get(self, category: str) -> Optional[BaseCalculator]:
        r"""
        :param category: 根据品类拿到对应的退改计算实例
        :return: 实例
        """
        return self._calculators.get(category)

    def calculate(self, category: str, order: dict, customer: dict) -> CalcResult:
        r"""
        计算这个退改金额
        :param category: 产品品类
        """
        calculator = self.get(category)
        if not calculator:
            return CalcResult(
                payable=False,
                fee_rate=1.0,
                fee_amount=0,
                settle_amount=0,
                detail=f"No calculator registered for category: {category}",
                state=CalculatorState.ERROR,
            )
        return calculator.calculate(order, customer)


calculator_registry = CalculatorRegistry()
calculator_registry.register("机票", FlightRefundCalculator())
calculator_registry.register("酒店", HotelCancellationCalculator())
calculator_registry.register("火车票", TrainChangeCalculator())
