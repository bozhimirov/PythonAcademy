import random
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import inspect

# create an in-memory SQLite database
engine = create_engine('sqlite:///mydatabase.db')
# engine_in_memory = create_engine('sqlite:///:memory:', echo=True)

metadata = MetaData()
users_table = Table('users', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('name', String),
                    Column('fullname', String),
                    Column('password', String)
                    )
# create a mapper to map the User class to the users table
mapper(User, users_table)

# create the users table
metadata.create_all(engine)

# create a session to manage the connection to the database
Session = sessionmaker(bind=engine)
session = Session()

# add a new user to the database
user = User(name='john', fullname='John Doe', password='password')
session.add(user)
session.commit()

# query the users table
users = session.query(User).all()
print(users)

# -----------------------------------------------------------------------------------------------
# Create an engine and connect to the database
# engine = create_engine('sqlite:///mydatabase.db')

# Reflect the existing tables in the database
metadata = MetaData()
metadata.reflect(bind=engine)

# Create a base class for declarative mapping
Base = declarative_base()


# Define the structure of the table using a mapping class
class MyTable(Base):
    __tablename__ = 'my_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Integer)


# Create the table in the database
Base.metadata.create_all(engine)

# Insert some data into the table
engine.execute(MyTable.__table__.insert(), [
    {'name': 'foo', 'value': 1},
    {'name': 'bar', 'value': 2},
    {'name': 'baz', 'value': 3},
])

# Create a session to use for querying
Session = sessionmaker(bind=engine)
session = Session()

# Query the database and get an instance of the mapped class
instance = session.query(MyTable).first()

# Use the inspect function to introspect the instance
inspector = inspect(instance)

# Print the column names
print("Columns:")
for column in inspector.attrs:
    print(f"{column.key}")


class Fridge:
    main_categories = {
        'cereals/ cereal products': ['cereals', 'cereal products'],
        'fruits/ vegetables': ['fruits', 'vegetables'],
        'meat/ fish': ['meat', 'fish'],
        'legumes/ nuts/ seeds': ['legumes', 'nuts', 'seeds'],
        'milk/ milk products': ['milk', 'milk products'],
        'oils/ fats': ['oils', 'fats'],
        'sweets/ spices': ['sweets', 'spices'],
        'condiments/ beverages': ['condiments', 'beverages'],
        'others': ['others']
    }


    def __init__(self, name):
        self.name = f'{name}\'s Fridge'
        self.categories = {}
        if name[-1] == 's':
            self.name = f'{name}\' Fridge'
        for k, v in self.main_categories.items():
            self.categories[k] = {}
            for i in v:
                self.categories[k][i] = []
                # self.categories[k].append(i)

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


class Ingredient:
    def __init__(self, name, amount, unit):
        self.name = name
        self.amount = amount
        self.unit = unit

    def __str__(self):
        return self.name


class Item(Ingredient):
    def __init__(self, name, amount, unit, expiry, main_category, sub_category):
        super().__init__(name, amount, unit)
        self.expiry = expiry
        self.main_category = main_category
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

# ----------------------------------------------------------------------------------------------------
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
