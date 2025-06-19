from app.database import Base, engine
from app.models import Animal, MeatPart, Inventory, Seasoning, Order, OrderItem

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")
