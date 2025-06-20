from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Animal(Base):
    __tablename__ = "animal"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_weight_kg = Column(Float, nullable=False)
    purchase_price_jmd = Column(Float, nullable=False)
    meat_parts = relationship("MeatPart", back_populates="animal")

class MeatPart(Base):
    __tablename__ = "meat_parts"
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animal.id"), nullable=False)
    part_name = Column(String, nullable=False)
    weight_lb = Column(Float, nullable=False)
    price_per_lb_jmd = Column(Float, nullable=False)
    animal = relationship("Animal", back_populates="meat_parts")
    inventory_items = relationship("Inventory", back_populates="meat_part")
    order_items = relationship("OrderItem", back_populates="meat_part")

class SeasoningPackage(Base):
    __tablename__ = "seasoning_packages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    ingredients = Column(String, nullable=False)
    inventory_items = relationship("Inventory", back_populates="seasoning_package")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    meat_part_id = Column(Integer, ForeignKey("meat_parts.id"), nullable=False)
    current_stock_lb = Column(Float, nullable=False)
    is_seasoned = Column(Boolean, default=False)
    location = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    seasoning_package_id = Column(Integer, ForeignKey("seasoning_packages.id"), nullable=True)
    meat_part = relationship("MeatPart", back_populates="inventory_items")
    seasoning_package = relationship("SeasoningPackage", back_populates="inventory_items")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    customer_pin = Column(String, nullable=True)
    location = Column(String, nullable=False)
    status = Column(String, default="pending")
    payment_status = Column(String, default="unpaid")
    date_ordered = Column(DateTime, default=datetime.utcnow)
    is_paid = Column(Boolean, default=False)
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    meat_part_id = Column(Integer, ForeignKey("meat_parts.id"))
    pounds_ordered = Column(Float, nullable=False)
    seasoned = Column(Boolean, default=False)
    seasonings = Column(String)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    meat_part = relationship("MeatPart", back_populates="order_items")
