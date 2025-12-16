from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL from environment variable
# Default to PostgreSQL for production, but tests will override this
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://lighthouse:lighthouse@postgres:5432/lighthouse"
)

# Create SQLAlchemy engine
# Add check_same_thread=False for SQLite compatibility in tests
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()