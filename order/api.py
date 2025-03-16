import json
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from events import redis_client
from models import CreateCustomerDto, CreateOrderDto, Customer, Order, OrderItem, UpdateOrderStatusDto

router = APIRouter()

# Create customer


@router.post("/customer")
def create_customer(dto: CreateCustomerDto, db: Session = Depends(get_db)):
    existing_customer = db.query(Customer).filter(
        Customer.email == dto.email).first()
    if existing_customer:
        raise HTTPException(
            status_code=400, detail="Customer with this email already exists")

    customer = Customer(name=dto.name, email=dto.email)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

# Create order


@router.post("/order")
def create_order(dto: CreateOrderDto, db: Session = Depends(get_db)):
    order = Order(customer_id=dto.customer_id, status="pending")
    db.add(order)
    db.commit()
    db.refresh(order)

    order_items = []
    for item in dto.items:
        order_item = OrderItem(
            order_id=order.id, product_id=item["product_id"], quantity=item["quantity"])
        db.add(order_item)
        order_items.append(
            {"product_id": item["product_id"], "quantity": item["quantity"]})
    db.commit()

    # Publish event to Redis
    event = {"event": "order_created",
             "order_id": order.id, "items": order_items}
    redis_client.publish("order_events", json.dumps(event))
    return {"order_id": order.id, "message": "Order created successfully"}


# Get order by id
@router.get("/order/{id}")
def get_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Get all orders


@router.get("/order")
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

# Update order status


@router.put("/order/status")
def update_order_status(dto: UpdateOrderStatusDto, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == dto.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    prev_status = order.status
    order.status = dto.status
    db.commit()

    # order cancelation event
    if prev_status == "pending" and dto.status == "canceled":
        event = {"event": "order_canceled", "order_id": dto.id}
        redis_client.publish("order_events", json.dumps(event))

    # order status update to notify inventory service
    event = {"event": "order_updated",
             "order_id": dto.id, "status": dto.status}
    redis_client.publish("order_events", json.dumps(event))

    return {"message": "Order status updated successfully"}
