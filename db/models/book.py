import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.config import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)

def generate_uuid():
    return str(uuid.uuid4())


class Menu(Base):
    __tablename__ = "menus"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(String, index=True)

    submenus = relationship(
        "Submenu", cascade="all, delete", back_populates="main_menu", passive_deletes=True,
    )


class Submenu(Base):
    __tablename__ = "submenus"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    main_menu_id = Column(String, ForeignKey("menus.id", ondelete="CASCADE"))

    main_menu = relationship("Menu", back_populates="submenus")
    dishes = relationship(
        "Dish", cascade="all, delete", back_populates="relate_sub", passive_deletes=True,
    )


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(String)
    submenu_id = Column(String, ForeignKey("submenus.id", ondelete="CASCADE"))

    relate_sub = relationship("Submenu", back_populates="dishes")
