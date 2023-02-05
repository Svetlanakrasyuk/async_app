from pydantic import BaseModel, Field


class DishBase(BaseModel):
    title: str = Field(example="Dish")
    description: str | None = Field(example="Main dish")
    price: str | None = Field(example="10.20")

    class Config:
        schema_extra = {
            "example": {
                "title": "Dish vegetable",
                "description": "Fruit",
                "price": 10.20,
            },
        }


class DishCreate(DishBase):
    pass


class Dish(DishBase):
    id: str
    submenu_id: str

    class Config:
        orm_mode = True


class SubmenuBase(BaseModel):
    title: str = Field(example="Submenu")
    description: str | None = Field(example="Main submenu")

    class Config:
        schema_extra = {
            "example": {
                "title": "Submenu",
                "description": "Main submenu",
            },
        }


class SubmenuCreate(SubmenuBase):
    pass


class Submenu(SubmenuBase):
    id: str
    main_menu_id: str
    dishes_count: int = 0

    class Config:
        orm_mode = True


class MenuBase(BaseModel):
    title: str = Field(example="Menu")
    description: str | None = Field(example="Main menu")

    class Config:
        schema_extra = {
            "example": {
                "title": "Menu",
                "description": "Main menu",
            },
        }


class MenuCreate(MenuBase):
    pass


class Menu(MenuBase):
    id: str
    submenus_count: int = 0
    dishes_count: int = 0

    class Config:
        orm_mode = True
