from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DB_URL
# -------------------------------------------------------------------------

engine = create_async_engine(DB_URL)
LocalSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
BaseModel = declarative_base()
