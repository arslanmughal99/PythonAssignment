import os
import json
import redis

from models import Inventory
from database import SessionLocal

REDIS_URL = os.getenv("REDIS_URL", "redis://192.168.1.5:6379")
redis_client = redis.Redis.from_url(REDIS_URL)


def process_order_event(message):
    data = json.loads(message["data"].decode("utf-8"))
    db = SessionLocal()
    
    if data["event"] == "order_created":
        for item in data["items"]:
            inventory_item = db.query(Inventory).filter(Inventory.product_id == item["product_id"]).first()
            if inventory_item and inventory_item.quantity >= item["quantity"]:
                inventory_item.quantity -= item["quantity"]
            else:
                print(f"Insufficient stock for product {item['product_id']}")
        db.commit()
    
    elif data["event"] == "order_canceled":
        print(f"Restoring inventory for canceled order {data['order_id']}")
        # implement restore inventory if necessary
    
    db.close()


def order_event_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("order_events")
    for message in pubsub.listen():
        if message["type"] == "message":
            process_order_event(message)