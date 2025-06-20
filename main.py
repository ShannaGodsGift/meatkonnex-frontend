from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import urllib.parse
import random

from app.database import SessionLocal
from app.models import Order, OrderItem, MeatPart, Inventory, Animal

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the MeatKonnex API"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

def get_current_admin_user(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if user != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return {"username": user}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "meat123":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

class MeatType(str, Enum):
    goat = "goat"
    pork = "pork"
    beef = "beef"
    chicken = "chicken"

class SeasoningType(str, Enum):
    none = "none"
    basic = "basic"
    curry = "curry"
    brown_stew = "brown_stew"

class SpiceLevel(str, Enum):
    none = "none"
    mild = "mild"
    medium = "medium"
    hot = "hot"

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=10, max_length=10, pattern="^[0-9]{10}$")
    meat_type: MeatType
    seasoning_package: SeasoningType
    pepper_level: SpiceLevel
    remove_items: Optional[List[str]] = []
    pounds: float = Field(..., gt=0)
    city: str = Field(..., min_length=1)

@app.post("/order")
def place_order(order: OrderRequest, db: Session = Depends(get_db)):
    if order.pounds < 5:
        raise HTTPException(status_code=400, detail="Minimum order for St. Thomas is 5 lbs.")

    prices = {"goat": 1400, "pork": 500, "beef": 500, "chicken": 400}
    seasoning_fees = {"none": 0, "basic": 200, "curry": 250, "brown_stew": 250}

    price_per_pound = prices[order.meat_type.value]
    seasoning_fee = seasoning_fees[order.seasoning_package.value]
    delivery_fee = 300
    base = price_per_pound * order.pounds
    total = base + seasoning_fee + delivery_fee
    customer_pin = str(random.randint(1000, 9999))

    inventory = (
        db.query(Inventory)
        .join(MeatPart)
        .filter(MeatPart.animal_id == MeatType[order.meat_type].value)
        .first()
    )

    if inventory:
        if inventory.current_stock_lb >= order.pounds:
            inventory.current_stock_lb -= order.pounds
        else:
            inventory.current_stock_lb = max(0, inventory.current_stock_lb - order.pounds)
        db.commit()

    new_order = Order(
        customer_name=order.customer_name,
        phone_number=order.phone_number,
        location="St. Thomas",
        customer_pin=customer_pin,
        is_paid=False
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    new_item = OrderItem(
        order_id=new_order.id,
        pounds_ordered=order.pounds,
        seasoned=order.seasoning_package != "none",
        seasonings=order.seasoning_package.value,
        unit_price=price_per_pound,
        total_price=base + seasoning_fee
    )
    db.add(new_item)
    db.commit()

    removed = f" (removed: {', '.join(order.remove_items)})" if order.remove_items else ""
    msg = f"""Thank you, {order.customer_name}!
Your order for {order.pounds} lbs of {order.meat_type.value} 
with {order.seasoning_package.value.replace('_', ' ')} seasoning{removed} 
and pepper: {order.pepper_level.value} to {order.city}, St. Thomas was received.
🗾 Total: JMD {int(total)}
🔒 PIN: {customer_pin}
📞 We’ll call you shortly at {order.phone_number} to confirm."""

    link = f"https://wa.me/{order.phone_number}?text={urllib.parse.quote(msg)}"

    return {
        "message": "Order placed successfully!",
        "order_summary": {
            "customer_name": order.customer_name,
            "phone_number": order.phone_number,
            "meat_type": order.meat_type.value,
            "seasoning_package": order.seasoning_package.value,
            "pepper_level": order.pepper_level.value,
            "removed_items": order.remove_items,
            "pounds": order.pounds,
            "city": order.city,
            "location": "St. Thomas",
            "price_per_pound": price_per_pound,
            "base_cost": base,
            "seasoning_cost": seasoning_fee,
            "delivery_fee": delivery_fee,
            "total_cost_jmd": int(total),
            "confirmation_pin": customer_pin
        },
        "whatsapp_link": link
    }

class PaymentStatusUpdate(BaseModel):
    is_paid: bool

@app.put("/admin/orders/{order_id}/payment-status", dependencies=[Depends(get_current_user)])
def update_payment_status(order_id: int, payment_update: PaymentStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.is_paid = payment_update.is_paid
    db.commit()
    db.refresh(order)
    return {"message": f"Order {order.id} payment status updated to {'paid' if order.is_paid else 'unpaid'}"}

@app.get("/admin/orders", dependencies=[Depends(get_current_user)])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).options(joinedload(Order.items)).all()
    order_list = []
    for order in orders:
        items = []
        for item in order.items:
            items.append({
                "meat_part": db.query(MeatPart).filter(MeatPart.id == item.meat_part_id).first().name if item.meat_part_id else "N/A",
                "pounds_ordered": item.pounds_ordered,
                "seasoned": item.seasoned,
                "seasonings": item.seasonings,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
            })
        order_list.append({
            "id": order.id,
            "customer_name": order.customer_name,
            "phone_number": order.phone_number,
            "location": order.location,
            "customer_pin": order.customer_pin,
            "is_paid": order.is_paid,
            "created_at": order.created_at,
            "items": items
        })
    return JSONResponse(content=jsonable_encoder(order_list))

@app.post("/orders/{order_id}/paid")
def mark_order_paid(order_id: int, paid: bool = Body(...), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.is_paid = paid
    db.commit()
    db.refresh(order)
    return {"message": "Payment status updated", "paid": order.is_paid}

@app.get("/animals")
def get_animals(db: Session = Depends(get_db)):
    return db.query(Animal).all()

@app.get("/meat_parts")
def get_all_meat_parts(db: Session = Depends(get_db)):
    return db.query(MeatPart).all()

@app.get("/meat_parts/{animal_id}")
def get_meat_parts(animal_id: int, db: Session = Depends(get_db)):
    return db.query(MeatPart).filter(MeatPart.animal_id == animal_id).all()

@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    results = (
        db.query(Inventory, MeatPart, Animal)
        .join(MeatPart, Inventory.meat_part_id == MeatPart.id)
        .join(Animal, MeatPart.animal_id == Animal.id)
        .all()
    )
    inventory_data = []
    for inv, part, animal in results:
        inventory_data.append({
            "inventory_id": inv.id,
            "meat_part": part.part_name,
            "animal": animal.name,
            "stock_lb": inv.current_stock_lb,
            "seasoned": inv.is_seasoned,
            "location": inv.location,
        })
    return inventory_data
