import pytest
from src.router.order_router import OrderRouter


@pytest.fixture
def router():
    return OrderRouter()


class TestOrderRouter:
    def test_get_ticket_exists(self, router):
        ticket = router.get_ticket("TK-20240728-001")
        assert ticket is not None
        assert ticket.category == "机票"
        assert ticket.issue_type == "退差价"
        assert ticket.customer_id == "C10086"
        assert "ORD-F-001" in ticket.related_orders

    def test_get_ticket_not_found(self, router):
        ticket = router.get_ticket("TK-NOT-EXIST")
        assert ticket is None

    def test_get_order_by_category_flight(self, router):
        order = router.get_order("ORD-F-001", category="机票")
        assert order is not None
        assert order["flight_number"] == "CA1234"
        assert order["fare_basis"] == "Y"

    def test_get_order_by_category_hotel(self, router):
        order = router.get_order("ORD-H-001", category="酒店")
        assert order is not None
        assert order["hotel_name"] == "杭州西湖希尔顿酒店"
        assert order["room_type"] == "标准间"

    def test_get_order_by_category_train(self, router):
        order = router.get_order("ORD-T-001", category="火车")
        assert order is not None
        assert order["train_number"] == "G101"

    def test_get_order_by_category_ride(self, router):
        order = router.get_order("ORD-R-001", category="打车")
        assert order is not None
        assert order["driver_name"] == "刘师傅"
        assert order["wait_minutes"] == 20

    def test_get_order_without_category(self, router):
        order = router.get_order("ORD-F-001")
        assert order is not None
        assert order["flight_number"] == "CA1234"

    def test_get_order_not_found(self, router):
        order = router.get_order("ORD-NOT-EXIST")
        assert order is None

    def test_get_customer_exists(self, router):
        customer = router.get_customer("C10086")
        assert customer is not None
        assert customer["name"] == "张三"
        assert customer["vip_level"] == "gold"

    def test_get_customer_not_found(self, router):
        customer = router.get_customer("C-NOT-EXIST")
        assert customer is None

    def test_get_policy_exists(self, router):
        policy = router.get_policy("机票", "退票")
        assert policy is not None
        assert "rules" in policy

    def test_get_policy_not_found(self, router):
        policy = router.get_policy("机票", "行李遗失")
        assert policy is None

    def test_get_policy_category_not_found(self, router):
        policy = router.get_policy("游轮", "退票")
        assert policy is None

    def test_resolve_category(self, router):
        assert router.resolve_category("TK-20240728-001") == "机票"
        assert router.resolve_category("TK-20240728-003") == "打车"
        assert router.resolve_category("TK-NOT-EXIST") is None
