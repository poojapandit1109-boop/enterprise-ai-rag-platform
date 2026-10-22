import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
"DATABASE_URL",
"postgresql+psycopg://ai_user:ai_password@localhost:5432/enterprise_ai",
)

engine = create_engine(
DATABASE_URL,
pool_pre_ping=True,
)

SessionLocal = sessionmaker(
autocommit=False,
autoflush=False,
bind=engine,
)
