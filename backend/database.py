from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from pathlib import Path
from .models import Base
from .config import get_settings

# database set up
settings = get_settings()

is_sqlite = settings.database_url.startswith("sqlite")

# Resolve SQLite path relative to this file, not the working directory
if is_sqlite:
    # strip sqlite:/// prefix to get the raw path
    raw_path = settings.database_url[len("sqlite:///"):]
    db_path = Path(raw_path) if Path(raw_path).is_absolute() else Path(__file__).parent / raw_path
    database_url = f"sqlite:///{db_path}"
else:
    database_url = settings.database_url
    db_path = None

connect_args = {"check_same_thread": False} if is_sqlite else {}
engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=(settings.environment == "dev"),
    pool_pre_ping=True,
)

def create_db_and_tables():
    if db_path and db_path.exists():
        db_path.unlink()
    Base.metadata.create_all(engine)

def close_db():
    engine.dispose()

def delete_db():
    if db_path and db_path.exists():
        db_path.unlink()

def get_session():
    with Session(engine) as session:
        yield session
