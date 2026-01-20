from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine with connection pool settings optimized for long-running processes
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=5,  # Reduce pool size
    max_overflow=10,  # Allow overflow connections
    pool_recycle=3600,  # Recycle connections every hour to avoid timeout
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    echo=False,  # Set to True for SQL debugging
)

# Listen for pool events to handle lost connections
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Called when a connection is created"""
    pass

@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Called when a connection is closed"""
    pass

@event.listens_for(engine, "detach")
def receive_detach(dbapi_conn, connection_record):
    """Called when a connection is removed from the pool"""
    pass

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=True
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")
