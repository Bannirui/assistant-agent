from dataclasses import dataclass
from typing import Optional

from ..mocks.seed_data import SEED_TICKETS, SEED_ORDERS, SEED_CUSTOMERS, SEED_POLICIES


@dataclass
class TicketContext:
    ticket_id: str
    category: str
    issue_type: str
    customer_id: str
    related_orders: list[str]
    title: str
    description: str
    priority: str
    status: str
    raw: dict


CATEGORY_TO_SYSTEM = {
    "机票": "flight",
    "酒店": "hotel",
    "火车": "train",
    "打车": "ride",
}

CATEGORY_NAMES = {
    "flight": "机票",
    "hotel": "酒店",
    "train": "火车",
    "ride": "打车",
}


class OrderRouter:
    def get_ticket(self, ticket_id: str) -> Optional[TicketContext]:
        ticket = SEED_TICKETS.get(ticket_id)
        if not ticket:
            return None
        return TicketContext(
            ticket_id=ticket["ticket_id"],
            category=ticket["category"],
            issue_type=ticket["issue_type"],
            customer_id=ticket["customer_id"],
            related_orders=ticket["related_orders"],
            title=ticket["title"],
            description=ticket["description"],
            priority=ticket["priority"],
            status=ticket["status"],
            raw=ticket,
        )

    def get_order(self, order_id: str, category: Optional[str] = None) -> Optional[dict]:
        if category:
            system = CATEGORY_TO_SYSTEM.get(category, "")
            if system and system in SEED_ORDERS:
                return SEED_ORDERS[system].get(order_id)

        for system_data in SEED_ORDERS.values():
            if order_id in system_data:
                return system_data[order_id]
        return None

    def get_customer(self, customer_id: str) -> Optional[dict]:
        return SEED_CUSTOMERS.get(customer_id)

    def get_policy(self, category: str, issue_type: Optional[str] = None) -> Optional[dict]:
        cat_policies = SEED_POLICIES.get(category, {})
        if not issue_type:
            return cat_policies
        return cat_policies.get(issue_type)

    def resolve_category(self, ticket_id: str) -> Optional[str]:
        ticket = SEED_TICKETS.get(ticket_id)
        if not ticket:
            return None
        return ticket.get("category")


router = OrderRouter()
