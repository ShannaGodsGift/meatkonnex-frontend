from app.database import SessionLocal
from app.models import Animal, MeatPart

# Open a new database session
db = SessionLocal()

# Get all animals
animals = db.query(Animal).all()

# Loop through and print each animal and its parts
for animal in animals:
    print(f"Animal: {animal.name}")
    print(f"  Weight (kg): {animal.total_weight_kg}")
    print(f"  Purchase Price (JMD): {animal.purchase_price_jmd}")
    print("  Meat Parts:")

    for part in animal.meat_parts:
        print(f"    - {part.part_name}: {part.weight_lb} lb @ {part.price_per_lb_jmd} JMD/lb")

    print("\n" + "-" * 40)

# Close the session
db.close()
