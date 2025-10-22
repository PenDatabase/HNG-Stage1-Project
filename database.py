from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

import os

load_dotenv()


def _build_database_url() -> str:
    """Return a database URL that works locally and on Heroku."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Heroku still supplies a postgres:// style URL; SQLAlchemy expects postgresql+psycopg2://
        return database_url.replace("postgres://", "postgresql+psycopg2://", 1)

    default_path = Path(__file__).resolve().parent / "app.db"
    # SQLite is a convenient default for local development.
    return f"sqlite:///{default_path}"


DATABASE_URL = _build_database_url()
CONNECT_ARGS = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
ECHO_SQL = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"

engine = create_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    connect_args=CONNECT_ARGS,
    pool_pre_ping=True,
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session