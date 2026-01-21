from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.exc import OperationalError as SAOperationalError
from app.core.config import settings
import logging
import pymysql

logger = logging.getLogger(__name__)

# Create engine with connection pool settings optimized for long-running processes
# Add driver-specific connect_args to help with network timeouts and keepalive.
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=5,  # Reduce pool size
    max_overflow=10,  # Allow overflow connections
    pool_recycle=3600,  # Recycle connections every hour to avoid timeout
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    connect_args={
        # client-side timeouts (seconds) for pymysql driver
        "connect_timeout": 10,
        "read_timeout": 120,
        "write_timeout": 120,
    },
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
        # Rollback may fail if the connection was lost during the request.
        # Attempt rollback but handle OperationalError from either SQLAlchemy
        # or the underlying driver (pymysql) gracefully so we don't raise
        # a secondary exception while handling the original one.
        try:
            db.rollback()
        except (SAOperationalError, pymysql.err.OperationalError, Exception) as re:
            logger.error(f"Rollback failed (likely connection lost): {re}")
            try:
                db.close()
            except Exception as ce:
                logger.error(f"Error closing DB session after rollback failure: {ce}")
            # Dispose the engine to drop any bad connections in the pool.
            try:
                engine.dispose()
            except Exception as de:
                logger.error(f"Engine dispose failed: {de}")
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")
