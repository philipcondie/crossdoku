from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from .models import Base
from .config import get_settings

# database set up
settings = get_settings()

is_sqlite = settings.database_url.startswith("sqlite")
is_memory = ":memory:" in settings.database_url

if is_memory:
    # In-memory SQLite: use StaticPool so all connections share the same DB
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=(settings.environment == "dev"),
    )
else:
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=(settings.environment == "dev"),
        pool_pre_ping=True,
    )

def create_db_and_tables():
    Base.metadata.create_all(engine)

def close_db():
    engine.dispose()

def get_session():
    with Session(engine) as session:
        yield session
