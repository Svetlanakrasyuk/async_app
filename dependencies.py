from db.config import async_session
from db.dals.menu_dal import MenuDAL


async def get_menu_dal():
    async with async_session() as session:
        async with session.begin():
            yield MenuDAL(session)