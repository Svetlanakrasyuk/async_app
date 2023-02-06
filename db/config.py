from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import aioredis
import asyncio

# DATABASE_URL = "sqlite+aiosqlite:///./test.db"
DATABASE_URL = "postgresql+asyncpg://postgres:my_password@localhost:5432/mydb"

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# async def main():
redis = aioredis.from_url("redis://localhost")
# await redis.set("my-key", "value")
# value = await redis.get("my-key")
    # print(value)


# if __name__ == "__main__":
#     asyncio.run(main())