import random
from typing import List, Optional
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# # create an in-memory SQLite database
# engine = create_engine('sqlite:///mydatabase.db')
# # engine_in_memory = create_engine('sqlite:///:memory:', echo=True)


class DataBase:

    CATEGORIES = {
        'cereals/ cereal products': ['cereals', 'cereal products'],
        'fruits/ vegetables': ['fruits', 'vegetables'],
        'meat/ fish': ['meat', 'fish'],
        'legumes/ nuts/ seeds': ['legumes', 'nuts', 'seeds'],
        'milk/ eggs/ milk products': ['milk', 'eggs', 'milk products'],
        'oils/ fats': ['oils', 'fats'],
        'sweets/ spices': ['sweets', 'spices'],
        'condiments/ beverages': ['condiments', 'beverages'],
        'others': ['others']
    }

    def __init__(self):
        pass

    @staticmethod
    def check_fridge_name(name):
        if name[-1] == 's':
            return f'{name}\' Fridge'
        else:
            return f'{name}\'s Fridge'

    @staticmethod
    def make_fridge(session, fridge_name):
        # with Session(engine) as session:
        fridge_obj = session.check_for_fridge(session)
        if not fridge_obj:
            fridge = Fridge(
                name=session.check_fridge_name(fridge_name)
            )
            session.add(fridge)
            session.commit()

    @staticmethod
    def check_for_fridge(session):
        fridge = select(Fridge).where(Fridge.name != "Change Name")
        item = []
        try:
            item = session.scalars(fridge).one()
            return item
        except NoResultFound:
            return item

    @staticmethod
    def get_sub_id(session, sub_name):
        subs = select(SubCategory).where(SubCategory.name == sub_name)
        sub = session.scalars(subs).one()
        return sub.id

    @staticmethod
    def add_item_to_fridge(session, new_item):
        session.add(new_item)
        session.commit()

    @staticmethod
    def add_recipe_to_fridge(session, new_recipe):
        session.add(new_recipe)
        session.commit()

    @staticmethod
    def delete_item_from_fridge(session, c_item):
        cc_item = session.get(Item, c_item.id)
        # print(cc_item)
        session.delete(cc_item)
        session.commit()

    @staticmethod
    def get_data_for_item_from_name(session, name_item):
        items = select(Item).where(Item.name == name_item)
        item = []
        try:
            item = session.scalars(items).one()
            return item
        except NoResultFound:
            return item

    @staticmethod
    def check_if_recipe_in_fridge(session, new_recipe):
        try:
            recipes = select(Recipe).where(Recipe.name == new_recipe.name)
            recipe = session.scalars(recipes).one()
            if recipe:
                n_rec = session.get(Recipe, new_recipe.id)
                return n_rec
            else:
                return []

        except AttributeError:
            return []



    @staticmethod
    def set_data_for_item_from_name(session, name_item, new_name, new_amount, new_unit, new_expiry, new_sub):
        items = select(Item).where(Item.name == name_item)
        item = session.scalars(items).one()
        item.name = new_name
        item.amount = int(new_amount)
        item.unit = new_unit
        item.expiry = new_expiry
        item.sub = new_sub

    @staticmethod
    def get_items_by_category(session, category):
        cats = select(MainCategory).where(MainCategory.name == category)
        cats = session.scalars(cats).one()
        cats_id = cats.id
        print(cats_id)
        subs = select(SubCategory).where(SubCategory.main_category_id == cats_id)
        ssubs = session.scalars(subs)
        print(ssubs)
        cat_items = []
        for sub in ssubs:
            items = select(Item).where(Item.sub_category == sub)
            for item in session.scalars(items):
                cat_items.append(item)
        return cat_items

    @staticmethod
    def get_all_items_from_fridge(session, fridge_id):
        all_items = []
        items = select(Item).where(Item.fridge_id == fridge_id)
        for item in session.scalars(items):
            all_items.append(item)
        return all_items

    @staticmethod
    def get_all_recipes(session, fridge_id):
        all_recipes = []
        recipes = select(Recipe).where(Recipe.fridge_id == fridge_id)
        for recipe in session.scalars(recipes):
            all_recipes.append(recipe)
        return all_recipes

    @staticmethod
    def get_all_users(session, fridge_id):
        all_users = []
        users = select(User).where(User.fridge_id == fridge_id)
        for user in session.scalars(users):
            all_users.append(user)
        return all_users

    @staticmethod
    def get_all_sub_cat(session):
        all_sub_cat = session.query(SubCategory).all()
        return all_sub_cat

    @staticmethod
    def get_all_main_cat(session):
        all_main_cat = session.query(MainCategory).all()
        return all_main_cat


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
        return f'{self.name!r}'

    # def __init__(self, name, amount, unit):
    #     self.name = name
    #     self.amount = amount
    #     self.unit = unit
    #
    # def __str__(self):
    #     return self.name


class MainCategory(Base):
    __tablename__ = 'main_category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    sub_categories: Mapped[List['SubCategory']] = relationship(back_populates='main_category',
                                                               cascade='all, delete-orphan')


class SubCategory(Base):
    __tablename__ = 'sub_category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    main_category_id: Mapped[int] = mapped_column(ForeignKey('main_category.id'))
    main_category: Mapped["MainCategory"] = relationship(back_populates='sub_categories')
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


class RecipeSuggestion:
    def __init__(self, rid, title, image):
        self.id = rid
        self.title = title
        self.image = image
        self.used = ''
        self.missed = ''

    def __str__(self):
        return self.title


class Recipe(Base):
    __tablename__ = 'recipe'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(30))
    image: Mapped[str] = mapped_column(String(60))
    instructions: Mapped[str] = mapped_column(String(600))
    ingredients: Mapped[List['Ingredient']] = relationship(back_populates='recipe')

    fridge_id: Mapped[int] = mapped_column(ForeignKey('fridge.id'))
    fridge: Mapped['Fridge'] = relationship(back_populates='favourite_recipes')

    def __repr__(self) -> str:
        return f'{self.title}'

#
# class RecipeSuggestion:
#     def __init__(self, rid, title, image):
#         self.id = rid
#         self.title = title
#         self.image = image
#         self.used = []
#         self.missed = []
#
#     def __str__(self):
#         return self.title
#
#
# class Recipe(RecipeSuggestion):
#     def __init__(self, rid, title, image, instructions):
#         super().__init__(rid, title, image)
#         self.ingredients = []
#         self.instructions = instructions
#         self.analyzedInstructions = {}
#
#     def __str__(self):
#         return self.title
#
# # ----------------------------------------------------------------------------------------------------
# testing TODO - to be deleted
# ----------------------------------------------------------------------------------------------------
#
# def random_category_item():
#     all_keys = []
#     for k in Fridge.categories.keys():
#         all_keys.append(k)
#     main_category = random.choice(all_keys)
#     all_sub_values = []
#     for el in Fridge.categories[main_category]:
#         all_sub_values.append(el)
#     sub_category = random.choice(all_sub_values)
#     return main_category, sub_category
#
#
# f1 = Fridge('stanley')
# m_c, s_c = random_category_item()
# i1 = BaseItem('item1', 1, 'g', '12/12/12', m_c, s_c)
# m_c, s_c = random_category_item()
# i2 = BaseItem('item2', 2, 'count', '13/12/12', m_c, s_c)
# m_c, s_c = random_category_item()
# i3 = BaseItem('item3', 1, 'g', '12/12/12', m_c, s_c)
# m_c, s_c = random_category_item()
# i4 = BaseItem('item4', 2, 'count', '13/12/12', m_c, s_c)
# f1.add_item(i1)
# f1.add_item(i2)
# f1.add_item(i3)
# f1.add_item(i4)
# print(f1.categories)
# print(f1.get_all_items())
# print(f1.get_items_by_category(m_c))


engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)
#
# with Session(engine) as session:
#     b = Fridge(
#         name=check_fridge_name('Bozhimirovi')
#     )
#     session.add(b)
#     session.commit()
#     for k, v in main_categories.items():
#         m_c = MainCategory(
#             name=k
#         )
#         session.add(m_c)
#         session.commit()
#         for i in v:
#             s_c = SubCategory(
#                 name=i,
#                 main_category_id=m_c.id
#             )
#             session.add(s_c)
#             session.commit()
#
#     item1 = Item(
#         name='milk',
#         amount='1000',
#         unit='ml',
#         sub_category_id=10,
#         fridge_id=1
#     )
#     session.add(item1)
#     session.commit()
#
# session = Session(engine)
# items = select(Item).where(Item.name == 'milk')
# for item in session.scalars(items):
#     print(f'{item.id} {item.name} {item.amount} {item.unit} {item.sub_category} {item.sub_category.main_category.name}')
#
# content = select(Fridge).where(Fridge.name == 'Bozhimirovi')
# for i in session.scalars(content):
#     print(i)
#
# session = Session(engine)
# db = DataBase
# item1 = Item(
#         name='milk',
#         amount='1000',
#         unit='ml',
#         expiry='15/12/2023',
#         sub_category_id=10,
#         fridge_id=1
#     )
# item2 = Item(
#         name='eggs',
#         amount='1',
#         unit='count',
#         expiry='12/12/2023',
#         sub_category_id=11,
#         fridge_id=1
#     )
# print(item1)
# db.add_item_to_fridge(session, item1)
# db.add_item_to_fridge(session, item2)
# all = db.get_all_items_from_fridge(session, 1)
# print(all)
# # db.delete_item_from_fridge(session, item1)
# # alls = db.get_all_items_from_fridge(session, 1)
# # print(alls)
# it = db.get_items_by_category(session, 'milk/ eggs/ milk products')
# print(it)
