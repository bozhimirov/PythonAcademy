
from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# # create an in-memory SQLite database
# engine = create_engine('sqlite:///mydatabase.db')
# # engine_in_memory = create_engine('sqlite:///:memory:', echo=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30))
    mail: Mapped[str] = mapped_column(String(50))

    fridge_id: Mapped[int] = mapped_column(ForeignKey('fridge.id'))
    fridge: Mapped['Fridge'] = relationship(back_populates='fridge_users')

    def __repr__(self) -> str:
        return f'{self.username}'


class Fridge(Base):
    __tablename__ = 'fridge'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    content: Mapped[List["Item"]] = relationship(
        back_populates='fridge', cascade='all, delete-orphan'
    )
    favourite_recipes: Mapped[List['Recipe']] = relationship(
        back_populates='fridge', cascade='all, delete-orphan'
    )

    fridge_users: Mapped[List['User']] = relationship(
        back_populates='fridge', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'name={self.name!r}'


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))
    amount: Mapped[str] = mapped_column(String(10))
    unit: Mapped[str] = mapped_column(String(20))
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipe.id'))
    recipe: Mapped['Recipe'] = relationship(back_populates='ingredients')

    def __repr__(self) -> str:
        return f'{self.name}'


class SubCategory(Base):
    __tablename__ = 'sub_category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    items: Mapped[List['Item']] = relationship(back_populates='sub_category', cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.name}'


class Item(Base):
    __tablename__ = 'item'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))
    amount: Mapped[str] = mapped_column(String(10))
    unit: Mapped[str] = mapped_column(String(20))
    expiry: Mapped[str] = mapped_column(String)
    sub_category_id: Mapped[int] = mapped_column(ForeignKey('sub_category.id'))
    sub_category: Mapped['SubCategory'] = relationship(back_populates='items')
    fridge_id: Mapped[int] = mapped_column(ForeignKey('fridge.id'))
    fridge: Mapped['Fridge'] = relationship(back_populates='content')

    def __repr__(self) -> str:
        return f'{self.name}'


class Recipe(Base):
    __tablename__ = 'recipe'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(30))
    image: Mapped[str] = mapped_column(String(60))
    instructions: Mapped[str] = mapped_column(String(600))
    ingredients: Mapped[List['Ingredient']] = relationship(back_populates='recipe', cascade="all,delete",)

    fridge_id: Mapped[int] = mapped_column(ForeignKey('fridge.id'))
    fridge: Mapped['Fridge'] = relationship(back_populates='favourite_recipes')

    def __repr__(self) -> str:
        return f'{self.title}'


# # ----------------------------------------------------------------------------------------------------
# testing TODO - to be deleted
# ----------------------------------------------------------------------------------------------------

#
# engine = create_engine('sqlite:///mydatabase.db')
# Base.metadata.create_all(engine)
