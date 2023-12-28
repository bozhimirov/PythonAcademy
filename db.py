from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from master_project.model import Fridge, SubCategory, Item, Recipe, User


class DataBase:

    CATEGORIES = ['fruits', 'vegetables', 'cereals', 'meat', 'fish', 'dairy', 'oils', 'legumes', 'other']

    def __init__(self):
        pass

    @staticmethod
    def check_fridge_name(name):
        if name[-1] == 's':
            return f'{name.capitalize()}\' Fridge'
        else:
            return f'{name.capitalize()}\'s Fridge'

    @staticmethod
    def make_fridge(session, fridge_name):
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
        session.delete(cc_item)
        session.commit()

    @staticmethod
    def delete_zero_amount_item_from_fridge(session, all_items):
        for a in all_items:
            if a.amount == '0':
                cc_item = session.get(Item, a.id)
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
            recipes = select(Recipe).where(Recipe.title == new_recipe.title)
            recipe = session.scalars(recipes).one()
            if recipe:
                n_rec = session.get(Recipe, new_recipe.id)
                return n_rec
            else:
                return []
        except NoResultFound:
            return []
        except AttributeError:
            return []

    @staticmethod
    def set_data_for_item_from_name(session, name_item, new_name, new_amount, new_unit, new_expiry, new_sub):
        items = select(Item).where(Item.name == name_item)
        item = session.scalars(items).one()
        item.name = new_name
        item.amount = new_amount
        item.unit = new_unit
        item.expiry = new_expiry
        item.sub = new_sub
        session.commit()

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
    def del_user_by_user_obj(session, user):
        c_user = session.get(User, user.id)
        session.delete(c_user)
        session.commit()

    @staticmethod
    def get_all_sub_cat(session):
        all_sub_cat = session.query(SubCategory).all()
        return all_sub_cat
