from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from db.dals.book_dal import MenuDAL
from db.models.book import Book
from dependencies import get_book_dal
from db.models import schemas

router = APIRouter()


@router.get("/api/v1/menus",
    response_model=list[schemas.Menu],
    summary="Get all menus",
    description="You can look all of the menus",
)
async def read_menus(book_dal: MenuDAL = Depends(get_book_dal)):
    return await book_dal.get_menus()


@router.post(
    "/api/v1/menus",
    response_model=schemas.Menu,
    status_code=status.HTTP_201_CREATED,
    summary="Create a menu",
    description="Create an menu with all the information, title, description",
)
async def create_menu(menu: schemas.MenuCreate, book_dal: MenuDAL = Depends(get_book_dal)):
    # Проверка уникальности меню
    await book_dal.get_menu_by_title(title=menu.title)
    return await book_dal.create_menu(menu=menu)

@router.get(
    "/api/v1/menus/{api_test_menu_id}",
    response_model=schemas.Menu,
    summary="Get one menu",
    description="You can look at the menu",
)
async def read_menu(api_test_menu_id: str, book_dal: MenuDAL = Depends(get_book_dal)):
    db_menu = await book_dal.get_menu(menu_id=api_test_menu_id)
    if not db_menu:
        raise HTTPException(status_code=404, detail="menu not found")
    return db_menu

@router.patch(
    "/api/v1/menus/{api_test_menu_id}",
    response_model=schemas.Menu,
    summary="Get one menu for update",
    description="You can update the menu with all the information, title, description",
)
async def update_menu(api_test_menu_id: str, menu: schemas.MenuBase, book_dal: MenuDAL = Depends(get_book_dal)):
    db_menu = await book_dal.get_menu(menu_id=api_test_menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return await book_dal.update_menu(menu=menu, api_test_menu_id=api_test_menu_id)

@router.delete(
    "/api/v1/menus/{api_test_menu_id}",
    summary="Get one menu for delete",
    description="You can delete the menu with all submenus and dishes",
)
async def delete_menu(api_test_menu_id: str, book_dal: MenuDAL = Depends(get_book_dal)):
    db_menu = await book_dal.get_menu(menu_id=api_test_menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    res = await book_dal.delete_menu(menu_id=api_test_menu_id)
    return res

@router.get(
    "/api/v1/menus/{api_test_menu_id}/submenus",
    response_model=list[schemas.Submenu],
    summary="Get all submenus",
    description="You can look all information about the submenus",
)
async def read_submenus(book_dal: MenuDAL = Depends(get_book_dal)):
    return await book_dal.get_submenus()

@router.post(
    "/api/v1/menus/{api_test_menu_id}/submenus",
    response_model=schemas.Submenu,
    status_code=status.HTTP_201_CREATED,
    summary="Create a submenu",
    description="Create an submenu with all the information, title, description",
)
async def create_submenu(
    api_test_menu_id: str, submenu: schemas.SubmenuCreate, book_dal: MenuDAL = Depends(get_book_dal),
):
    return await book_dal.create_submenu(submenu=submenu, main_menu_id=api_test_menu_id)

@router.get(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}",
    response_model=schemas.Submenu,
    summary="Get one submenu",
    description="You can look information about the submenu",
)
async def read_submenu(api_test_submenu_id: str, book_dal: MenuDAL = Depends(get_book_dal)):
    db_submenu = await book_dal.get_submenu(submenu_id=api_test_submenu_id)
    if not db_submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    return db_submenu

@router.patch(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}",
    response_model=schemas.Submenu,
    summary="Get one submenu for update",
    description="You can update the submenu with all the information, title, description",
)
async def update_submenu(api_test_submenu_id: str, submenu: schemas.SubmenuBase, book_dal: MenuDAL = Depends(get_book_dal)):
    db_submenu = await book_dal.get_submenu(submenu_id=api_test_submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    return await book_dal.update_submenu(submenu=submenu, api_test_submenu_id=api_test_submenu_id)

@router.delete(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}",
    summary="Delete one submenu",
    description="You can delete the menu with all dishes",
)
async def delete_submenu(api_test_submenu_id: str, api_test_menu_id: str, book_dal: MenuDAL = Depends(get_book_dal)):
    db_submenu = await book_dal.get_submenu(submenu_id=api_test_submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    return await book_dal.delete_submenu(submenu_id=api_test_submenu_id, menu_id=api_test_menu_id)

@router.post(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes",
    response_model=schemas.Dish, status_code=status.HTTP_201_CREATED,
    summary="Create a dish",
    description="Create a dish with all the information, title, description, price",
)
async def create_dish(api_test_submenu_id: str, api_test_menu_id: str, dish: schemas.DishCreate, book_dal: MenuDAL = Depends(get_book_dal)):
    return await book_dal.create_dish(dish=dish, submenu_id=api_test_submenu_id, menu_id=api_test_menu_id)

@router.get(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes",
    response_model=list[schemas.Dish],
    summary="Get all dishes",
    description="You can look all information about the dishes",
)
async def read_dishes(book_dal: MenuDAL = Depends(get_book_dal)):
    dishes = await book_dal.get_dishes()
    return dishes

@router.get(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes/{api_test_dish_id}",
    response_model=schemas.Dish,
    summary="Get one dish",
    description="You can look all information about the dish",
)
async def read_dish(api_test_dish_id: str, book_dal: MenuDAL = Depends(get_book_dal)):
    db_dish = await book_dal.get_dish(dish_id=api_test_dish_id)
    return db_dish

@router.patch(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes/{api_test_dish_id}",
    response_model=schemas.Dish,
    summary="Get one dish for update",
    description="You can update the dish with all the information, title, description, price",
)
async def update_dish(api_test_dish_id: str, api_test_submenu_id: str, api_test_menu_id: str, dish: schemas.DishBase, book_dal: MenuDAL = Depends(get_book_dal)):
    db_dish = await book_dal.get_dish(dish_id=api_test_dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    return await book_dal.update_dish(dish=dish, api_test_dish_id=api_test_dish_id, api_test_submenu_id=api_test_submenu_id, api_test_menu_id=api_test_menu_id)

@router.delete(
    "/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes/{api_test_dish_id}",
    summary="Delete one dish",
    description="You can delete the dish",
)
async def delete_dish(api_test_dish_id: str, api_test_submenu_id: str, api_test_menu_id: str, book_dal: MenuDAL = Depends(get_book_dal)):
    db_dish = await book_dal.get_dish(dish_id=api_test_dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    return await book_dal.delete_dish(dish_id=api_test_dish_id, api_test_submenu_id=api_test_submenu_id, api_test_menu_id=api_test_menu_id)

