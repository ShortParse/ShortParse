import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from shortparse.settings import STORAGE_DIR, DATABASE_URL as CFG_DATABASE_URL

logger = logging.getLogger("shortparse.database")

# Ensure storage directory exists
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Determine the final database URL
is_postgresql = False
if CFG_DATABASE_URL:
    db_url = CFG_DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    is_postgresql = db_url.startswith("postgresql://")
else:
    db_url = None

if is_postgresql:
    DATABASE_URL = db_url
    logger.info("Configuring PostgreSQL connection engine with pooling...")
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )
else:
    DB_PATH = STORAGE_DIR / "shortparse.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    logger.info(f"Configuring local SQLite engine at: {DB_PATH}")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def get_db():
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
