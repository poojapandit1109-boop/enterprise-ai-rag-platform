from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


DATABASE_URL = "postgresql+psycopg://ai_user:ai_password@localhost:5432/enterprise_ai"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def create_tables():
    Base.metadata.create_all(bind=engine)