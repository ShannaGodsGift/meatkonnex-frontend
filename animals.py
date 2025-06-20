from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Animal, MeatPart
from pydantic import BaseModel
from typing import List, Optional
import datetime

router = APIRouter()

# Pydantic schemas
class MeatPartCreate(BaseModel):
    part_name: str
    weight_lb: float
    price_per_lb_jmd: float

class AnimalCreate(BaseModel):
    name: str
    total_weight_kg: float
    purchase_price_jmd: float
    date_purchased: Optional[datetime.datetime] = None
    meat_parts: List[MeatPartCreate] = []

class AnimalOut(BaseModel):
    id: int
    name: str
    total_weight_kg: float
    purchase_price_jmd: float
    date_purchased: datetime.datetime
    meat_parts: List[dict]

    class Config:
        orm_mode = True

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create animal with meat parts
@router.post("/animals", response_model=AnimalOut)
def create_animal(data: AnimalCreate, db: Session = Depends(get_db)):
    animal = Animal(
        name=data.name,
        total_weight_kg=data.total_weight_kg,
        purchase_price_jmd=data.purchase_price_jmd,
        date_purchased=data.date_purchased or datetime.datetime.utcnow()
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)

    for part in data.meat_parts:
        meat_part = MeatPart(
            animal_id=animal.id,
            part_name=part.part_name,
            weight_lb=part.weight_lb,
            price_per_lb_jmd=part.price_per_lb_jmd
        )
        db.add(meat_part)

    db.commit()
    return animal

# List animals
@router.get("/animals", response_model=List[AnimalOut])
def list_animals(db: Session = Depends(get_db)):
    animals = db.query(Animal).all()
    return [
        {
            **animal.__dict__,
            "meat_parts": [
                {
                    "id": part.id,
                    "part_name": part.part_name,
                    "weight_lb": part.weight_lb,
                    "price_per_lb_jmd": part.price_per_lb_jmd
                }
                for part in animal.meat_parts
            ]
        }
        for animal in animals
    ]
