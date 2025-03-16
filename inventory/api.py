from database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from models import AdjustInventoryDto, Product, Inventory, Warehouse, CreateProductDto

router = APIRouter()

# Create new product


@router.post("/product")
def create_product(dto: CreateProductDto, db: Session = Depends(get_db)):
    product = Product(name=dto.name, description=dto.description)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# Get all products


@router.get("/product")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# Get product by id


@router.get("/product/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Get all warehouses


@router.get("/warehouse")
def list_warehouses(db: Session = Depends(get_db)):
    return db.query(Warehouse).all()

# Get warehouse inventory


@router.get("/inventory/{warehouse_id}")
def get_inventory(warehouse_id: int, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id).all()
    return inventory


@router.post("/inventory/adjust")
def adjust_inventory(dto: AdjustInventoryDto, db: Session = Depends(get_db)):
    inventory_item = db.query(Inventory).filter(
        Inventory.warehouse_id == dto.warehouse_id,
        Inventory.product_id == dto.product_id
    ).first()

    if inventory_item:
        inventory_item.quantity += dto.quantity
    else:
        inventory_item = Inventory(
            warehouse_id=dto.warehouse_id, product_id=dto.product_id, quantity=dto.quantity)
        db.add(inventory_item)

    db.commit()
    db.refresh(inventory_item)

    return {"message": "Inventory updated successfully"}
