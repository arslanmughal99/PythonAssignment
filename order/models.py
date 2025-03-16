from enum import StrEnum
from pydantic import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey


"""
Dto models
"""
class CreateCustomerDto(BaseModel):
    name: str
    email: str

class CreateOrderDto(BaseModel):
    customer_id: int
    items: list[dict]
    
class OrderStatusEnum(StrEnum):
    Completed = "Complete"
    Rejected = "Reject"
class UpdateOrderStatusDto(BaseModel):
    id: int
    status: OrderStatusEnum


"""
Database models
"""
Base = declarative_base()
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String, default="pending")
    customer = relationship("Customer")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    order = relationship("Order")
