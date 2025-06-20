from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual database path or URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./meatapp.db"  # Example: SQLite local file

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Import models so they register with Base
from app import models

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
