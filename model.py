
from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# # create an in-memory SQLite database
# engine = create_engine('sqlite:///mydatabase.db')
# # engine_in_memory = create_engine('sqlite:///:memory:', echo=True)


class Base(DeclarativeBase):
    """
        A Base class that is needed for creation of the other Classes
    """
    pass


class User(Base):
    """
    A User class that makes users connected to a fridge instance
    params: id: int id of the user autoincrement and primary key
    params: username: str name of the user
    params: mail: str email of the user
    params: fridge_id: int id of the fridge instance that specific user can be connected to specific fridge
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30))
    mail: Mapped[str] = mapped_column(String(50))

    fridge_id: Mapped[int] = mapped_column(ForeignKey('fridge.id'))
    fridge: Mapped['Fridge'] = relationship(back_populates='fridge_users')

    def __repr__(self) -> str:
        """
            Representation of user
            :returns user's username
        """
        return f'{self.username}'


class Fridge(Base):
    """
    A Fridge class that makes a fridge instance
    params: id: int id of the fridge autoincrement and primary key
    params: name: str name of the fridge
    """
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
        """
            Representation of fridge
            :returns fridge's name
        """
        return f'name={self.name!r}'


class Ingredient(Base):
    """
    An Ingredient class that is made by ingredients needed for making a recipe
    params: id: int id of the ingredient autoincrement and primary key
    params: name: str name of the ingredient
    params: amount: str amount of the ingredient as a string
    params: unit: str unit of the ingredient
    params: recipe_id: int id of the ingredient as it is in the API
    """
    __tablename__ = 'ingredient'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))
    amount: Mapped[str] = mapped_column(String(10))
    unit: Mapped[str] = mapped_column(String(20))
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipe.id'))
    recipe: Mapped['Recipe'] = relationship(back_populates='ingredients')

    def __repr__(self) -> str:
        """
            Representation of ingredient
            :returns ingredient's name
        """
        return f'{self.name}'


class SubCategory(Base):
    """
    A Sub Category class that makes sub categories for the food items
    params: id: int id of the sub category autoincrement and primary key
    params: name: str name of the sub category
    """
    __tablename__ = 'sub_category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    items: Mapped[List['Item']] = relationship(back_populates='sub_category', cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """
            Representation of sub category
            :returns sub category's name
        """
        return f'{self.name}'


class Item(Base):
    """
    An Item class for food items that are into fridge
    params: id: int id of the item autoincrement and primary key
    params: name: str name of the item
    params: amount: str amount of the item as a string
    params: unit: str unit of the item
    params: expiry: str expiry date of the item
    params: sub_category_id: int id of the sub category of the item
    params: fridge_id: int id of the fridge where the item is placed
    """
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
        """
            Representation of food item
            :returns item's name
        """
        return f'{self.name}'


class Recipe(Base):
    """
    A Recipe class for food recipes
    params: id: int id of the recipe autoincrement and primary key
    params: recipe_id: int id of the recipe as it is in the API
    params: title: str name of the recipe
    params: image: str place of the stored image from the recipe as a string
    params: instructions: str instructions for making the recipe
    params: fridge_id: int id of the fridge where the recipe is placed
    """
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
        """
            Representation of recipe
            :returns recipe's name
        """
        return f'{self.title}'



