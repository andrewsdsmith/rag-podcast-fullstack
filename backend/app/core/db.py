from sqlmodel import Session, create_engine

from app.core.config import settings

# Continue with engine setup
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    # Tables are created with alembic migrations.
    # Seed data requires psql from prestart.sh
    # Nothing to do here
    pass
