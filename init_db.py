from app.database import engine
from app.models import Base

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
