import random
# from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, ForeignKey
# from sqlalchemy.orm import mapper, sessionmaker, declarative_base, relationship
from sqlalchemy import inspect

# # create an in-memory SQLite database
# engine = create_engine('sqlite:///mydatabase.db')
# # engine_in_memory = create_engine('sqlite:///:memory:', echo=True)
#
# metadata = MetaData()
# class FridgeContentTable(Base):
#     __tablename__ = 'Fridge_content'
#     id = Column(Integer, primary_key=True)
#     content_id = Column(Integer)
#     item_id = Column(Integer)
#
# # Define the structure of the table using a mapping class
# # class FridgeTable(Base):
# #     __tablename__ = 'Fridge'
# #     id = Column(Integer, primary_key=True)
# #     name = Column(String)
# #     content = Column(Integer, ForeignKey('FridgeContentTable.id'))
#
# items_table = Table('items_table', metadata,
#                     Column()
#                     )
#
# fridge_content_table = Table('fridge_content', metadata,
#                     Column('id', Integer, primary_key=True),
#                     Column('content_id', Integer),
#                     Column('item_id', Integer, foreign_key=items_table.id),
#                     )
#
# fridge_table = Table('fridge', metadata,
#                     Column('id', Integer, primary_key=True),
#                     Column('name', String),
#                     Column('content', Integer, foreign_key=fridge_content_table.id),
#
#
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

# -----------------------------------------------------------------------------------------------
# Create an engine and connect to the database
# engine = create_engine('sqlite:///mydatabase.db')
# #
# # # Reflect the existing tables in the database
# metadata = MetaData()
# metadata.reflect(bind=engine)
# #
# # # Create a base class for declarative mapping
# Base = declarative_base()
# #
# #
# # # Define the structure of the table using a mapping class
# class MainCategoryTable(Base):
#     __tablename__ = 'Main_category'
#     main_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     main_name = Column(String)
#
#     def __str__(self):
#         return self.main_name
#
#
# # Define the structure of the table using a mapping class
# class SubCategoryTable(MainCategoryTable):
#     __tablename__ = 'Sub_category'
#     sub_id = Column(Integer, primary_key=True)
#     main_category = Column(Integer, ForeignKey(MainCategoryTable.main_id))
#     sub_name = Column(String)
#
#
# # Define the structure of the table using a mapping class
# class FridgeTable(Base):
#     __tablename__ = 'Fridge'
#     fridge_id = Column(Integer, primary_key=True)
#     fridge_name = Column(String)
#     # content = Column(Integer, ForeignKey(FridgeContentTable.id))
#     # item_id = Column(Integer, ForeignKey(ItemsTable.item_id))
#
#
# # Define the structure of the table using a mapping class
# class ItemsTable(Base):
#     __tablename__ = 'Items'
#     item_id = Column(Integer, primary_key=True)
#     item_name = Column(String)
#     item_amount = Column(String)
#     item_unit = Column(String)
#     sub_category_id = Column(Integer, ForeignKey('SubCategoryTable.sub_id'))
#     fridge_name_id = Column(Integer, ForeignKey('FridgeTable.fridge_id'))
#     sub_category = relationship('SubCategoryTable')
#     fridge_name = relationship('FridgeTable')



# Define the structure of the table using a mapping class
# class FridgeContentTable(ItemsTable):
#     __tablename__ = 'Fridge_content'
#     id = Column(Integer, primary_key=True)
#     # fridge_id = Column(Integer, ForeignKey(FridgeTable.id))
#     item_id = Column(Integer, ForeignKey(ItemsTable.id))



# Create the table in the database
Base.metadata.create_all(engine)
#

# # Insert some data into the table


#
# # Create a session to use for querying
# Session = sessionmaker(bind=engine)
# session = Session()
#
# # Query the database and get an instance of the mapped class
# instance = session.query(ItemsTable).all()
#
# # Use the inspect function to introspect the instance
# inspector = inspect(instance)
#
# # Print the column names
# print("Columns:")
# for i in instance:
#     print(f"{i.item_id} {i.item_name} {i.item_amount} {i.item_unit} {i.sub_name} {str(i.main_category)}")



class Fridge:
    #

    def __init__(self, name):
        self.name = f'{name}\'s Fridge'
        # self.categories = {}
        if name[-1] == 's':
            self.name = f'{name}\' Fridge'
        self.content = int
        # for k, v in self.main_categories.items():
        #     self.categories[k] = {}
        #     for i in v:
        #         self.categories[k][i] = []
        #         # self.categories[k].append(i)


    def add_item(self, item):
        main_category = item.main_category
        sub_category = item.sub_category
        self.categories[main_category][sub_category].append(item)

    def __str__(self):
        return self.name

    def delete_item(self, item):
        for _, v in self.categories.items():
            for _, val in v.items():
                for va in val:
                    if va.name == item.name:
                        val.remove(va)

    def get_data_for_item_from_name(self, name_item):
        item_object = []
        for _, v in self.categories.items():
            for _, val in v.items():
                for va in val:
                    if va.name == name_item:
                        item_object.append(va)
        return item_object

    def set_data_for_item_from_name(self, name_item,
                                    new_name, new_quantity, new_unit, new_expiry, new_main, new_sub):
        for _, v in self.categories.items():
            for _, val in v.items():
                for va in val:
                    if va.name == name_item:
                        va.name = new_name
                        va.quantity = new_quantity
                        va.unit = new_unit
                        va.expiry = new_expiry
                        va.main_category = new_main
                        va.sub_category = new_sub

    def get_items_by_category(self, category):
        n_l = []
        for k, v in self.categories.items():
            if k == category:
                for _, val in v.items():
                    for va in val:
                        if va:
                            n_l.append(va)
        return n_l

    def get_all_items(self):
        n_l = []
        for _, v in self.categories.items():
            for _, val in v.items():
                for va in val:
                    if va:
                        n_l.append(va)
        return n_l


class FridgeContent:
    def __init__(self, fridge, item):
        self.fridge = fridge
        self.item = item


class Ingredient:
    def __init__(self, name, amount, unit):
        self.name = name
        self.amount = amount
        self.unit = unit

    def __str__(self):
        return self.name


class MainCategory:
    def __init__(self, name):
        self.name = name


class SubCategory:
    def __init__(self, main_category, name):
        self.main_category = main_category
        self.name = name


class Item(Ingredient):
    def __init__(self, name, amount, unit, expiry, main_category, sub_category):
        super().__init__(name, amount, unit)
        self.expiry = expiry
        # self.main_category = main_category
        self.sub_category = sub_category

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name}'
    # def __repr__(self):
    #     return f'{self.name, self.quantity, self.unit, self.expiry, self.main_category, self.sub_category}'


class RecipeSuggestion:
    def __init__(self, rid, title, image):
        self.id = rid
        self.title = title
        self.image = image
        self.used = []
        self.missed = []

    def __str__(self):
        return self.title


class Recipe(RecipeSuggestion):
    def __init__(self, rid, title, image, instructions):
        super().__init__(rid, title, image)
        self.ingredients = []
        self.instructions = instructions
        self.analyzedInstructions = {}

    def __str__(self):
        return self.title
