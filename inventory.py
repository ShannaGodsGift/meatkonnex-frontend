from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/")
def create_inventory(item: dict, db: Session = Depends(get_db)):
    new_item = models.Inventory(
        meat_part_id=item["meat_part_id"],
        current_stock_lb=item["current_stock_lb"],
        is_seasoned=item["is_seasoned"],
        location=item["location"],
        is_active=True
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/")
def get_all_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).filter(models.Inventory.is_active == True).all()


@router.get("/{inventory_id}")
def get_inventory(inventory_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return item


@router.put("/{inventory_id}")
def update_inventory(inventory_id: int, update_data: dict, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory not found")

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{inventory_id}")
def soft_delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory not found")

    item.is_active = False
    db.commit()
    return {"message": "Inventory soft deleted"}


@router.put("/restore/{inventory_id}")
def restore_inventory(inventory_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory not found")

    item.is_active = True
    db.commit()
    return {"message": "Inventory restored"}
