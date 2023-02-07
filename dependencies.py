from db.config import async_session
from db.dals.book_dal import MenuDAL


async def get_book_dal():
    async with async_session() as session:
        async with session.begin():
            yield MenuDAL(session)