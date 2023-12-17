import random
from typing import List, Optional
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# # create an in-memory SQLite database
# engine = create_engine('sqlite:///mydatabase.db')
# # engine_in_memory = create_engine('sqlite:///:memory:', echo=True)
#
# metadata = MetaData()
# users_table = Table('users', metadata,
#                     Column('id', Integer, primary_key=True),
#                     Column('name', String),
#                     Column('fullname', String),
#                     Column('password', String)
#                     )
# # create a mapper to map the User class to the users table
# mapper(User, users_table)
#
# # create the users table
# metadata.create_all(engine)
#
# # create a session to manage the connection to the database
# Session = sessionmaker(bind=engine)
# session = Session()
#
# # add a new user to the database
# user = User(name='john', fullname='John Doe', password='password')
# session.add(user)
# session.commit()
#
# # query the users table
# users = session.query(User).all()
# print(users)
#
# # -----------------------------------------------------------------------------------------------
# # Create an engine and connect to the database
# # engine = create_engine('sqlite:///mydatabase.db')
#
# # Reflect the existing tables in the database
# metadata = MetaData()
# metadata.reflect(bind=engine)
#
# # Create a base class for declarative mapping
# Base = declarative_base()
#
#
# # Define the structure of the table using a mapping class
# class MyTable(Base):
#     __tablename__ = 'my_table'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     value = Column(Integer)
#
#
# # Create the table in the database
# Base.metadata.create_all(engine)
#
# # Insert some data into the table
# engine.execute(MyTable.__table__.insert(), [
#     {'name': 'foo', 'value': 1},
#     {'name': 'bar', 'value': 2},
#     {'name': 'baz', 'value': 3},
# ])
#
# # Create a session to use for querying
# Session = sessionmaker(bind=engine)
# session = Session()
#
# # Query the database and get an instance of the mapped class
# instance = session.query(MyTable).first()
#
# # Use the inspect function to introspect the instance
# inspector = inspect(instance)
#
# # Print the column names
# print("Columns:")
# for column in inspector.attrs:
#     print(f"{column.key}")

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

    def make_fridge(self, fridge_name):
        with Session(engine) as session:
            fridge = Fridge(
                name=self.check_fridge_name(fridge_name)
            )
            session.add(fridge)
            session.commit()

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
    def set_data_for_item_from_name(session, name_item, new_name, new_amount, new_unit, new_expiry, new_sub):
        items = select(Item).where(Item.name == name_item)
        item = session.scalars(items).one()
        item.name = new_name
        item.amount = new_amount
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


class Base(DeclarativeBase):
    pass


class Fridge(Base):
    __tablename__ = 'fridge'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    content: Mapped[List["Item"]] = relationship(
        back_populates='fridge', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'name={self.name!r}'

    #
    # def __init__(self, name):
    #     self.name = f'{name}\'s Fridge'
    #     self.categories = {}
    #     if name[-1] == 's':
    #         self.name = f'{name}\' Fridge'
    #     for k, v in self.main_categories.items():
    #         self.categories[k] = {}
    #         for i in v:
    #             self.categories[k][i] = []
    #             # self.categories[k].append(i)

    # def add_item(self, session, item):
    #     # main_category = item.main_category
    #     # sub_category = item.sub_category
    #     # self.categories[main_category][sub_category].append(item)
    #     content.append(item)
    # # def __str__(self):
    # #     return self.name
    #
    # def delete_item(self, item):
    #     for _, v in self.categories.items():
    #         for _, val in v.items():
    #             for va in val:
    #                 if va.name == item.name:
    #                     val.remove(va)
    #
    # def get_data_for_item_from_name(self, name_item):
    #     item_object = []
    #     for _, v in self.categories.items():
    #         for _, val in v.items():
    #             for va in val:
    #                 if va.name == name_item:
    #                     item_object.append(va)
    #     return item_object
    #
    # def set_data_for_item_from_name(self, name_item,
    #                                 new_name, new_quantity, new_unit, new_expiry, new_main, new_sub):
    #     for _, v in self.categories.items():
    #         for _, val in v.items():
    #             for va in val:
    #                 if va.name == name_item:
    #                     va.name = new_name
    #                     va.quantity = new_quantity
    #                     va.unit = new_unit
    #                     va.expiry = new_expiry
    #                     va.main_category = new_main
    #                     va.sub_category = new_sub
    #
    #
    # def get_items_by_category(self, category):
    #     n_l = []
    #     for k, v in self.categories.items():
    #         if k == category:
    #             for _, val in v.items():
    #                 for va in val:
    #                     if va:
    #                         n_l.append(va)
    #     return n_l
    #
    # def get_all_items(self):
    #     n_l = []
    #     for _, v in self.categories.items():
    #         for _, val in v.items():
    #             for va in val:
    #                 if va:
    #                     n_l.append(va)
    #     return n_l


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
        self.used = []
        self.missed = []

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
