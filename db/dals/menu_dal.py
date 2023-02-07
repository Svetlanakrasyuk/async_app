from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload

from db.models.book import Menu, Submenu, Dish
from db.models import schemas
from db.config import redis
from db.cashe import cashe


class MenuDAL():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_menus(self) -> List[Menu]:
        # Get data from redis
        redis_data = await cashe.get_cash("menus")
        if redis_data:
            return redis_data
        else:
            # Get data from postgres
            q = await self.db_session.execute(select(Menu).options(selectinload(Menu.submenus).options(selectinload(Submenu.dishes))))
            my_db = q.scalars().all()
            if my_db:
                res = []
                for instance in my_db:
                    menu_dict = jsonable_encoder(instance)
                    menu_dict["submenus_count"] = (len(instance.submenus))
                    dishes = 0
                    for d in instance.submenus:
                        dishes += len(d.dishes)
                    menu_dict["dishes_count"] = dishes
                    res.append(menu_dict)
                await cashe.set_cash(res, "menus")
                return res
            await cashe.set_cash(my_db, "menus")
            return my_db
    
    async def create_menu(self, menu: schemas.MenuCreate):
        new_menu = Menu(title=menu.title, description=menu.description)
        self.db_session.add(new_menu)
        await self.db_session.flush()
        await cashe.del_cashe("menus")
        await cashe.change_menu_cashe()
        return new_menu

    async def get_menu_by_title(self, title: str):
        q = await self.db_session.execute(select(Menu).where(Menu.title == title))
        q = q.scalars().all()
        print(q)
        if q:
            raise HTTPException(status_code=400, detail="Menu already exist")
        
    async def get_menu(self, menu_id: str):
    # Get data from redis
        redis_data = await cashe.get_cash("menu" + menu_id)
        if redis_data:
            return redis_data
        else:
        #     Get data from postgres
            my_db = await self.db_session.execute(select(Menu).where(Menu.id == menu_id).options(selectinload(Menu.submenus).options(selectinload(Submenu.dishes))))
            my_db = my_db.scalars().all()
            if my_db:
                res = jsonable_encoder(my_db)
                res[0]["submenus_count"] = len(res[0]["submenus"])
                dishes = 0
                for d in res[0]["submenus"]:
                    dishes += len(d["dishes"])
                res[0]["dishes_count"] = dishes
                del res[0]["submenus"]
                # Set data to redis
                await cashe.set_cash(res, "menu" + menu_id)
                return res[0]
            # Set data to redis
            await cashe.set_cash(my_db, "menu" + menu_id)
            return my_db

    async def update_menu(self, menu: schemas.MenuBase, api_test_menu_id):
        q = update(Menu).where(Menu.id == api_test_menu_id)
        q = q.values(title=menu.title)
        q = q.values(description=menu.description)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        await cashe.change_menu_cashe(api_test_menu_id)
        db_menu = await self.get_menu(menu_id=api_test_menu_id)
        await cashe.change_menu_cashe(api_test_menu_id)
        return db_menu

    async def delete_menu(self, menu_id: str):
        q = delete(Menu).where(Menu.id == menu_id)
        res = await self.db_session.execute(q)
        result = {"status": True, "message": "The menu has been deleted"}
        await cashe.change_menu_cashe(menu_id)
        return result
    
    async def get_submenus(self):
        redis_data = await cashe.get_cash("submenus")
        if redis_data:
            return redis_data
        else:
            # Get data from postgres
            q = await self.db_session.execute(select(Submenu).options(selectinload(Submenu.dishes)))
            my_db = q.scalars().all()
            if my_db:
                res = []
                for instance in my_db:
                    menu_dict = jsonable_encoder(instance)
                    menu_dict["dishes_count"] = (len(instance.dishes))
                    res.append(menu_dict)
                await cashe.set_cash(res, "menus")
                return res
            await cashe.set_cash(my_db, "submenus")
            return my_db

    async def create_submenu(self, submenu: schemas.SubmenuCreate, main_menu_id: str):
        new_submenu = Submenu(title=submenu.title, description=submenu.description, main_menu_id=main_menu_id)
        self.db_session.add(new_submenu)
        await self.db_session.flush()
        await cashe.change_submenu_cashe(main_menu_id)
        return new_submenu

    async def get_submenu(self, submenu_id: str):
        # Get data from redis
        redis_data = await cashe.get_cash("submenu" + submenu_id)
        if redis_data:
            return redis_data
        else:
            my_db = await self.db_session.execute(select(Submenu).where(Submenu.id == submenu_id).options(selectinload(Submenu.dishes)))
            my_db = my_db.scalars().all()
            if my_db:
                res = jsonable_encoder(my_db)
                res[0]["dishes_count"] = len(res[0]["dishes"])
                del res[0]["dishes"]
                print(res)
                await cashe.set_cash(res, "submenu" + submenu_id)
                return res[0]
            await cashe.set_cash(my_db, "submenu" + submenu_id)
            return my_db

    async def update_submenu(self, submenu: schemas.SubmenuBase, api_test_submenu_id):
        q = update(Submenu).where(Submenu.id == api_test_submenu_id)
        q = q.values(title=submenu.title)
        q = q.values(description=submenu.description)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        await cashe.change_submenu_cashe("", api_test_submenu_id)
        db_submenu = await self.get_submenu(submenu_id=api_test_submenu_id)
        await cashe.change_submenu_cashe("", api_test_submenu_id)
        return db_submenu

    async def delete_submenu(self, submenu_id: str, menu_id: str):
        q = delete(Submenu).where(Submenu.id == submenu_id)
        res = await self.db_session.execute(q)
        result = {"status": True, "message": "The submenu has been deleted"}
        await cashe.change_submenu_cashe(menu_id, submenu_id)
        return result

    async def create_dish(self, dish: schemas.DishCreate, submenu_id: str, menu_id: str):
        new_dish = Dish(title=dish.title, description=dish.description, price=dish.price, submenu_id=submenu_id)
        self.db_session.add(new_dish)
        await self.db_session.flush()
        await cashe.change_dish_cashe(menu_id, submenu_id)
        return new_dish

    async def get_dishes(self):
        redis_data =await cashe.get_cash("dishes")
        if redis_data:
            return redis_data
        else:
            # Get data from postgres
            q = await self.db_session.execute(select(Dish))
            res = q.scalars().all()
            await cashe.set_cash(res, "dishes")
            return res

    async def get_dish(self, dish_id: str):
        redis_data = await cashe.get_cash("dish" + dish_id)
        if redis_data:
            return redis_data
        else:
            # Get data from postgres
            my_db = await self.db_session.execute(select(Dish).where(Dish.id == dish_id))
            my_db = my_db.scalars().all()
            if not my_db:
                raise HTTPException(status_code=404, detail="dish not found")
            await cashe.set_cash(my_db[0], "dish" + dish_id)
            return my_db[0]

    async def update_dish(self, dish: schemas.DishBase, api_test_dish_id: str, api_test_submenu_id: str, api_test_menu_id: str):
        q = update(Dish).where(Dish.id == api_test_dish_id)
        q = q.values(title=dish.title)
        q = q.values(description=dish.description)
        q = q.values(price=dish.price)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        db_dish = await self.get_dish(dish_id=api_test_dish_id)
        await cashe.change_dish_cashe(
            api_test_menu_id, api_test_submenu_id, api_test_dish_id,
        )
        db_dish = await self.get_dish(dish_id=api_test_dish_id)
        return db_dish

    async def delete_dish(self, dish_id: str, api_test_submenu_id: str, api_test_menu_id: str):
        q = delete(Dish).where(Dish.id == dish_id)
        res = await self.db_session.execute(q)
        result = {"status": True, "message": "The dish has been deleted"}
        await cashe.change_dish_cashe(api_test_menu_id, api_test_submenu_id, dish_id)
        return result

    async def fill_base(self):
        menu1 = Menu(title="Меню", description="Основное меню")
        r = await self.create_menu(menu1)
        menu1_id = r.id
        submenu1 = Submenu(title="Холодные закуски", description="К пиву")
        sub1 = await self.create_submenu(submenu1, main_menu_id=menu1_id)
        sub1_id = sub1.id
        dish1 = Dish(title="Селедь Бисмарк", description="Традиционное блюдо из сельди", price="182,99")
        await self.create_dish(dish1, sub1_id, menu1_id)
        dish2 = Dish(title="Мясная тарелка", description="Нарезка из мяса", price="170,10")
        await self.create_dish(dish2, sub1_id, menu1_id)
        dish3 = Dish(title="Рыбная тарелка", description="Нарезка из рыбы", price="162,20")
        await self.create_dish(dish3, sub1_id, menu1_id)
        submenu2 = Submenu(title="Рамен", description="Горячий рамен")
        sub2 = await self.create_submenu(submenu2, main_menu_id=menu1_id)
        sub2_id = sub2.id
        dish4 = Dish(title="Дайзи", description="Рамен на куринном бульоне", price="167,99")
        await self.create_dish(dish4, sub2_id, menu1_id)
        dish5 = Dish(title="Унаги", description="Рамен на рыбном бульоне", price="123,50")
        await self.create_dish(dish5, sub2_id, menu1_id)
        dish6 = Dish(title="Чиизу", description="Рамен на сырном бульоне", price="188,90")
        await self.create_dish(dish6, sub2_id, menu1_id)
        menu2 = Menu(title="Алкоголь", description="Алкогольные напитки")
        r = await self.create_menu(menu2)
        menu2_id = r.id
        submenu3 = Submenu(title="Красные вина", description="Для романтического вечера")
        sub3 = await self.create_submenu(submenu3, main_menu_id=menu2_id)
        sub3_id = sub3.id
        dish7 = Dish(title="Вино красное", description="Фруктовое", price="382,99")
        await self.create_dish(dish7, sub3_id, menu2_id)
        dish8 = Dish(title="Вино красное", description="Сухое", price="270,10")
        await self.create_dish(dish8, sub3_id, menu2_id)
        submenu4 = Submenu(title="Виски", description="Для интересных бесед")
        sub4 = await self.create_submenu(submenu4, main_menu_id=menu2_id)
        sub4_id = sub4.id
        dish9 = Dish(title="Чивас", description="5 лет", price="547,99")
        await self.create_dish(dish9, sub4_id, menu2_id)
        dish10 = Dish(title="Джек", description="7 лет", price="475,10")
        await self.create_dish(dish10, sub4_id, menu2_id)
        return "База данных заполнена тестовым меню"