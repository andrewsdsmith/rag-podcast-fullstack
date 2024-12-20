from sqlmodel import create_engine

from app.core.config import settings

# Continue with engine setup
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
