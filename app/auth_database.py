from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///app.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass

sessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():

    db = sessionLocal()
    try:
        yield db
    finally:
        # db.close()
        await db.close()
