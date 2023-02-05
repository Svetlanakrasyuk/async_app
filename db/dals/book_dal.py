from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload

from db.models.book import Book, Menu, Submenu, Dish
from db.models import schemas


class BookDAL():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    # async def create_book(self, name: str, author: str,   release_year: int):
    #     new_book = Book(name=name,author=author, release_year=release_year)
    #     self.db_session.add(new_book)
    #     await self.db_session.flush()

    # async def get_all_books(self) -> List[Book]:
    #     q = await self.db_session.execute(select(Book).order_by(Book.id))
    #     return q.scalars().all()

    # async def update_book(self, book_id: int, name: Optional[str], author: Optional[str], release_year: Optional[int]):
    #     q = update(Book).where(Book.id == book_id)
    #     if name:
    #         q = q.values(name=name)
    #     if author:
    #         q = q.values(author=author)
    #     if release_year:
    #         q = q.values(release_year=release_year)
    #     q.execution_options(synchronize_session="fetch")
    #     await  self.db_session.execute(q)


    async def get_menus(self) -> List[Menu]:
        # q = await self.db_session.execute(select(Menu).order_by(Menu.id))
        # return q.scalars().all()
        # Get data from redis
        # redis_data = cashe.get_cash("menus")
        # if redis_data:
        #     return redis_data
        # else:
            # my_db = db.query(models.Menu).all()
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
            # cashe.set_cash(res, "menus")
            return res
        # cashe.set_cash(my_db, "menus")
        return my_db
    
    async def create_menu(self, menu: schemas.MenuCreate):
        new_menu = Menu(title=menu.title, description=menu.description)
        self.db_session.add(new_menu)
        await self.db_session.flush()
        # self.db_session.refresh(new_menu)
        # cashe.del_cashe("menus")
        # cashe.change_menu_cashe()
        return new_menu

    async def get_menu_by_title(self, title: str):
        q = await self.db_session.execute(select(Menu).where(Menu.title == title))
        q = q.scalars().all()
        print(q)
        if q:
            raise HTTPException(status_code=400, detail="Menu already exist")
        
    async def get_menu(self, menu_id: str):
    # Get data from redis
    # redis_data = cashe.get_cash("menu" + menu_id)
    # if redis_data:
    #     return redis_data
    # else:
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
            # cashe.set_cash(res, "menu" + menu_id)
            return res[0]
        # cashe.set_cash(my_db, "menu" + menu_id)
        return my_db

    async def update_menu(self, menu: schemas.MenuBase, api_test_menu_id):
        q = update(Menu).where(Menu.id == api_test_menu_id)
        q = q.values(title=menu.title)
        q = q.values(description=menu.description)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        db_menu = await self.get_menu(menu_id=api_test_menu_id)
        return db_menu

    async def delete_menu(self, menu_id: str):
        q = delete(Menu).where(Menu.id == menu_id)
        res = await self.db_session.execute(q)
        result = {"status": True, "message": "The menu has been deleted"}
        # cashe.change_menu_cashe(menu_id)
        return result
    
    async def get_submenus(self):
    # redis_data = cashe.get_cash("submenus")
    # if redis_data:
    #     return redis_data
    # else:
        # Get data from postgres
        q = await self.db_session.execute(select(Submenu).options(selectinload(Submenu.dishes)))
        my_db = q.scalars().all()
        if my_db:
            res = []
            for instance in my_db:
                menu_dict = jsonable_encoder(instance)
                menu_dict["dishes_count"] = (len(instance.dishes))
                res.append(menu_dict)
            # cashe.set_cash(res, "menus")
            return res
        # cashe.set_cash(res, "submenus")
        return my_db

    async def create_submenu(self, submenu: schemas.SubmenuCreate, main_menu_id: str):
        new_submenu = Submenu(title=submenu.title, description=submenu.description, main_menu_id=main_menu_id)
        self.db_session.add(new_submenu)
        await self.db_session.flush()
        # cashe.change_submenu_cashe(main_menu_id)
        return new_submenu

    async def get_submenu(self, submenu_id: str):
        # Get data from redis
        # redis_data = cashe.get_cash("submenu" + submenu_id)
        # if redis_data:
        #     return redis_data
        # else:
        my_db = await self.db_session.execute(select(Submenu).where(Submenu.id == submenu_id).options(selectinload(Submenu.dishes)))
        my_db = my_db.scalars().all()
        if my_db:
            res = jsonable_encoder(my_db)
            res[0]["dishes_count"] = len(res[0]["dishes"])
            del res[0]["dishes"]
            print(res)
            # cashe.set_cash(res, "submenu" + submenu_id)
            return res[0]
        # cashe.set_cash(my_db, "submenu" + submenu_id)
        return my_db

    async def update_submenu(self, submenu: schemas.SubmenuBase, api_test_submenu_id):
        q = update(Submenu).where(Submenu.id == api_test_submenu_id)
        q = q.values(title=submenu.title)
        q = q.values(description=submenu.description)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        db_submenu = await self.get_submenu(submenu_id=api_test_submenu_id)
        # cashe.change_submenu_cashe("", api_test_submenu_id)
        return db_submenu

    async def delete_submenu(self, submenu_id: str, menu_id: str):
        q = delete(Submenu).where(Submenu.id == submenu_id)
        res = await self.db_session.execute(q)
        result = {"status": True, "message": "The submenu has been deleted"}
        # cashe.change_submenu_cashe(menu_id, submenu_id)
        return result

    async def create_dish(self, dish: schemas.DishCreate, submenu_id: str, menu_id: str):
        new_dish = Dish(title=dish.title, description=dish.description, price=dish.price, submenu_id=submenu_id)
        self.db_session.add(new_dish)
        await self.db_session.flush()
        # cashe.change_dish_cashe(menu_id, submenu_id)
        return new_dish

    async def get_dishes(self):
        # redis_data = cashe.get_cash("dishes")
        # if redis_data:
        #     return redis_data
        # else:
            # Get data from postgres
        q = await self.db_session.execute(select(Dish))
        res = q.scalars().all()
        # cashe.set_cash(res, "dishes")
        return res

    async def get_dish(self, dish_id: str):
        # redis_data = cashe.get_cash("dish" + dish_id)
        # if redis_data:
        #     return redis_data
        # else:
            # Get data from postgres
        my_db = await self.db_session.execute(select(Dish).where(Dish.id == dish_id))
        my_db = my_db.scalars().all()
        if not my_db:
            raise HTTPException(status_code=404, detail="dish not found")
        # cashe.set_cash(res, "dish" + dish_id)
        return my_db[0]

    async def update_dish(self, dish: schemas.DishBase, api_test_dish_id: str, api_test_submenu_id: str, api_test_menu_id: str):
        q = update(Dish).where(Dish.id == api_test_dish_id)
        q = q.values(title=dish.title)
        q = q.values(description=dish.description)
        q = q.values(price=dish.price)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        db_dish = await self.get_dish(dish_id=api_test_dish_id)
        # cashe.change_dish_cashe(
        #     api_test_menu_id, api_test_submenu_id, api_test_dish_id,
        # )
        db_dish = await self.get_dish(dish_id=api_test_dish_id)
        return db_dish

    async def delete_dish(self, dish_id: str, api_test_submenu_id: str, api_test_menu_id: str):
        q = delete(Dish).where(Dish.id == dish_id)
        res = await self.db_session.execute(q)
        result = {"status": True, "message": "The dish has been deleted"}
        # cashe.change_dish_cashe(api_test_menu_id, api_test_submenu_id, dish_id)
        return result
