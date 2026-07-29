from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class CalculatorState(Enum):
    INIT = "init"
    FETCH_ORDER = "fetch_order"
    CHECK_RULES = "check_rules"
    APPLY_VIP = "apply_vip"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class CalcResult:
    # 是不是要用户补差价
    payable: bool
    # 费率
    fee_rate: float
    # 手续费
    fee_amount: float
    # 结算金额
    settle_amount: float
    # 展示给用户的文案
    detail: str
    # 状态机 让调用方知道在哪一步计算出错了
    state: CalculatorState = CalculatorState.COMPLETE


class BaseCalculator(ABC):
    def calculate(self, order: dict, customer: dict) -> CalcResult:
        state = CalculatorState.INIT
        try:
            # 1 订单校验
            state = CalculatorState.FETCH_ORDER
            self._validate_order(order)
            # 2 基础费率
            state = CalculatorState.CHECK_RULES
            fee_rate = self._get_base_fee_rate(order)
            # 3 对VIP有费率折扣
            state = CalculatorState.APPLY_VIP
            # 原始费率
            raw_rate = fee_rate
            # 折扣之后的费率
            fee_rate = self._apply_discount(fee_rate, customer)
            # 4 计算结果
            state = CalculatorState.COMPLETE
            # 订单金额
            price = float(order.get("price", 0))
            # 手续费
            fee_amount = round(price * fee_rate, 2)
            # 结算金额 正数=要退的钱 负数=要补的钱
            settle_amount = round(price - fee_amount, 2)

            return CalcResult(
                # 用户是不是要补差价
                payable=settle_amount < 0,
                # 费率
                fee_rate=fee_rate,
                # 手续费
                fee_amount=fee_amount,
                # 结算金额
                settle_amount=settle_amount,
                # 展示给用户的文案
                detail=self._build_detail(order, customer, raw_rate, fee_rate, fee_amount, settle_amount),
            )
        except Exception as e:
            # 出错了就通过状态机告诉调用方是哪一步出现了错误
            return CalcResult(
                payable=False,
                fee_rate=1.0,
                fee_amount=0,
                settle_amount=0,
                detail=f"Calculation error: {e}",
                state=CalculatorState.ERROR,
            )

    @abstractmethod
    def _validate_order(self, order: dict):
        r"""
        订单校验
        不同的子类要校验自己负责的产品品类
        机票校验product_type==机票
        酒店校验product_type==酒店
        :param order: 里面字段product_type是子类要关注的 看看符不符合自己关注的品类
        """
        ...

    @abstractmethod
    def _get_base_fee_rate(self, order: dict) -> float:
        r"""
        基础费率的查询
        机票按照 舱位*距离起飞时间查表
        酒店按照 距离入住时间分段
        :return: 0到1.x
        """
        ...

    def _apply_discount(self, fee_rate: float, customer: dict) -> float:
        r"""
        对VIP用户 有退改手续费优惠
        :param fee_rate: 原始的费率
        :param customer: 要是普通用户就不变 VIP用户就打折
        :return: 打过折之后的费率
        """
        if fee_rate >= 1.0:
            # 不可退 不可改的场景下VIP也不生效
            return fee_rate
        # vip等级
        vip = customer.get("vip_level", "regular")
        # 金-减半 白金-免费 普通用户-全价
        discounts = {"gold": 0.5, "platinum": 0.0, "regular": 1.0}
        discount = discounts.get(vip, 1.0)
        return fee_rate * discount

    @abstractmethod
    def _build_detail(
            self, order: dict, customer: dict,
            raw_rate: float, fee_rate: float, fee_amount: float, settle_amount: float,
    ) -> str:
        r"""
        告诉给用户的文案信息
        :param raw_rate: 原始的手续费费率
        :param fee_rate: 最终的手续费费率
        """
        ...
