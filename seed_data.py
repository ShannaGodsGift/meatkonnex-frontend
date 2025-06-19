from app.database import SessionLocal
from app.models import Animal, MeatPart, Inventory, SeasoningPackage

db = SessionLocal()

animals_data = [
    ("Goat", 22.0, 22000),
    ("Chicken", 10.0, 6000),
    ("Pig", 80.0, 42000),
    ("Cow", 300.0, 280000),
]

for name, weight, price in animals_data:
    existing = db.query(Animal).filter_by(name=name).first()
    if not existing:
        animal = Animal(name=name, total_weight_kg=weight, purchase_price_jmd=price)
        db.add(animal)
        db.commit()

meat_parts_by_animal = {
    "Goat": [
        ("Standard Goat Meat", 5.0, 1500),
        ("Goat Head", 3.0, 900),
        ("Goat Liver", 1.5, 800)
    ],
    "Chicken": [
        ("Standard Chicken Meat", 4.0, 700),
        ("Chicken Neck", 1.0, 300),
        ("Chicken Liver", 1.0, 400)
    ],
    "Pig": [
        ("Standard Pork Meat", 6.0, 1200),
        ("Pig Tail", 2.5, 950),
        ("Pork Belly", 4.0, 1400),
        ("Pork Shoulder", 5.0, 1300)
    ],
    "Cow": [
        ("Standard Beef Meat", 6.0, 1800),
        ("Cow Head", 5.0, 1000),
        ("Cow Tail", 4.0, 1500),
        ("Cow Skin", 3.0, 1100),
        ("Ribeye", 2.5, 2000),
        ("Sirloin", 2.0, 1900),
        ("Steak", 3.0, 1950),
        ("Oxtail", 3.5, 2200)
    ]
}

for animal_name, parts in meat_parts_by_animal.items():
    animal = db.query(Animal).filter_by(name=animal_name).first()
    for part_name, weight, price in parts:
        existing = db.query(MeatPart).filter_by(part_name=part_name, animal_id=animal.id).first()
        if not existing:
            meat_part = MeatPart(
                animal_id=animal.id,
                part_name=part_name,
                weight_lb=weight,
                price_per_lb_jmd=price
            )
            db.add(meat_part)
            db.commit()

        meat_part = db.query(MeatPart).filter_by(part_name=part_name, animal_id=animal.id).first()
        existing_inventory = db.query(Inventory).filter_by(meat_part_id=meat_part.id).first()
        if not existing_inventory:
            inventory = Inventory(
                meat_part_id=meat_part.id,
                current_stock_lb=20.0,
                is_seasoned=False,
                location="St. Thomas",
                is_active=True
            )
            db.add(inventory)
            db.commit()

seasonings_data = [
    ("Basic", "Salt, Pepper, Garlic, Thyme"),
    ("Curry", "Curry Powder, Onion, Pimento, Garlic, Thyme"),
    ("Jerk", "Jerk Seasoning, Scallion, Scotch Bonnet, Thyme")
]

for name, ingredients in seasonings_data:
    exists = db.query(SeasoningPackage).filter_by(name=name).first()
    if not exists:
        seasoning = SeasoningPackage(name=name, ingredients=ingredients)
        db.add(seasoning)
        db.commit()

print("Safe seeding complete.")
db.close()
