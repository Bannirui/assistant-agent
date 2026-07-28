from fastapi import APIRouter, HTTPException
from .seed_data import (
    SEED_TICKETS,
    SEED_ORDERS,
    SEED_CUSTOMERS,
    SEED_POLICIES,
)

router = APIRouter(prefix="/api", tags=["mock"])


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    ticket = SEED_TICKETS.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


@router.get("/mock/order/{order_id}")
async def get_order(order_id: str):
    for category_data in SEED_ORDERS.values():
        if order_id in category_data:
            return category_data[order_id]
    raise HTTPException(status_code=404, detail=f"Order {order_id} not found")


@router.get("/mock/flight/orders/{order_id}")
async def get_flight_order(order_id: str):
    order = SEED_ORDERS["flight"].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Flight order {order_id} not found")
    return order


@router.get("/mock/hotel/orders/{order_id}")
async def get_hotel_order(order_id: str):
    order = SEED_ORDERS["hotel"].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Hotel order {order_id} not found")
    return order


@router.get("/mock/train/orders/{order_id}")
async def get_train_order(order_id: str):
    order = SEED_ORDERS["train"].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Train order {order_id} not found")
    return order


@router.get("/mock/ride/orders/{order_id}")
async def get_ride_order(order_id: str):
    order = SEED_ORDERS["ride"].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Ride order {order_id} not found")
    return order


@router.get("/mock/customers/{customer_id}")
async def get_customer(customer_id: str):
    customer = SEED_CUSTOMERS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer


@router.get("/mock/policies")
async def get_policy(category: str = "", issue_type: str = ""):
    if not category:
        return list(SEED_POLICIES.keys())
    cat_policies = SEED_POLICIES.get(category, {})
    if not issue_type:
        return list(cat_policies.values())
    policy = cat_policies.get(issue_type)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy not found: {category}/{issue_type}")
    return policy
