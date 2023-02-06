import json

# from .database import decoded_connection
from fastapi.encoders import jsonable_encoder
from db.config import redis


async def get_cash(key_redis):
    redis_data = await redis.get(key_redis)
    if redis_data:
        return json.loads(redis_data)
    return None


async def set_cash(postgres_data, key_redis):
    # encode object to json, then json to str
    rescash = json.dumps(jsonable_encoder(postgres_data))
    # set to redis
    await redis.set(key_redis, rescash, 60)


async def del_cashe(key_redis):
    await redis.delete(key_redis)


async def change_dish_cashe(menu_id, submenu_id, dish_id=""):
    await del_cashe("dishes")
    await del_cashe("menus")
    await del_cashe("submenus")
    await del_cashe("menu" + menu_id)
    await del_cashe("submenu" + submenu_id)
    await del_cashe("dish" + dish_id)


async def change_submenu_cashe(menu_id="", submenu_id=""):
    await del_cashe("menus")
    await del_cashe("submenus")
    await del_cashe("menu" + menu_id)
    await del_cashe("submenu" + submenu_id)


async def change_menu_cashe(menu_id=""):
    await del_cashe("menus")
    await del_cashe("menu" + menu_id)
