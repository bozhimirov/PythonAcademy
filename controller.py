from datetime import date, datetime, timedelta
from PIL import ImageTk, Image

from tkinter import *
from tkinter import ttk
import tkinter.font as font

from dateutil.utils import today
import json

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from master_project.view import View
from models_new import DataBase, Item, RecipeSuggestion, Ingredient, Recipe, Base, Fridge


class Controller:

    def __init__(self):
        self.engine = create_engine('sqlite:///mydatabase.db')
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.db = DataBase
        self.fridge = self.session.get(Fridge, 1)
        self.view = View(self)
        self.generate_choices()
        self.last_item = ''
        self.chosen_ingredients = self.chosen()

        # for testing------TOBE removed
        # self.recipes = self.get_recipes_by_items()
        # self.get_recipe_by_id(self.recipes[1])
        self.chosen_recipe = object

    def chosen(self):
        list_chosen_ingr = self.get_ingr()
        if len(list_chosen_ingr) == 0:
            # return random_recipe
            pass
        to_str_chosen_ingr = (',+').join(list_chosen_ingr)

        return to_str_chosen_ingr

    def get_ingr(self):
        chosen_ingredients = ['milk', 'potato', 'eggs', 'chicken', 'onion']
        return chosen_ingredients

    def get_recipes_by_items(self):
        url = f'https://api.spoonacular.com/recipes/findByIngredients?' \
              f'apiKey=4bb99921a1fa470bb800293b23863d29' \
              f'&ingredients={self.chosen_ingredients}&number=100'
        recipes = []
        response = requests.get(url)

        if response.status_code < 400:
            results = (response.json())
            self.write_recipe_to_file(results)

            for result in results:
                # print(result)
                n_recipe = RecipeSuggestion(
                    result['id'],
                    result['title'],
                    result['image'])

                used = result['usedIngredients']
                for i in used:
                    ingr = Ingredient(
                        name=i['name'], amount=i['amount'], unit=i['unit'])
                    n_recipe.used.append(ingr)

                missed = result['missedIngredients']
                for i in missed:
                    ingr = Ingredient(
                        name=i['name'], amount=i['amount'], unit=i['unit'])
                    n_recipe.missed.append(ingr)
                recipes.append(n_recipe)
            return recipes

    def get_recipe_by_id(self, recipe):
        recipe_id = recipe.id
        url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?' \
              'apiKey=4bb99921a1fa470bb800293b23863d29' \
              '&includeNutrition=true'
        response = requests.get(url)
        results = (response.json())
        r_id = results['id']
        r_name = results['title']
        r_ingredients = results["extendedIngredients"]
        r_image = results['image']
        r_instructions = results['instructions']
        # r_analyzedInstructions = results['analyzedInstructions']
        # steps = r_analyzedInstructions[0]["steps"]
        recipe = Recipe(
            recipe_id=r_id, title=r_name, image=r_image, instructions=r_instructions)
        for i in r_ingredients:
            amount, unit = self.make_unit(i['measures']['metric']['amount'], i['measures']['metric']['unitShort'])
            ingredient = Ingredient(
                name=i['nameClean'], amount=amount, unit=unit)
            recipe.ingredients.append(ingredient)
        # for i in steps:
        #     recipe.analyzedInstructions[i['number']] = i['step']

        self.chosen_recipe = recipe
        # self.add_to_db(recipe)
        # print(self.chosen_recipe.title)
        # print(self.chosen_recipe.ingredients)
        # print(self.chosen_recipe.instructions)

    @staticmethod
    def make_unit(amount, unit):
        if unit not in ['g', 'ml', 'count']:
            new_amount = ''
            new_unit = ''
            if unit == 'kg':
                new_amount = int(amount) * 1000
                new_unit = 'g'
                return new_amount, new_unit
            elif unit == 'tbsp':
                new_amount = int(amount) * 0.01
                new_unit = 'g'
            elif unit == 'cup':
                new_amount = int(amount) * 0.2
                new_unit = 'ml'
            return str(new_amount), new_unit

    @staticmethod
    def write_recipe_to_file(results):
        with open('temp_result.json', 'w') as f:
            new_result = json.dumps(results)
            f.write(new_result)

    def main(self):
        self.view.main()

    def search_item(self, name_item):
        data = self.db.get_data_for_item_from_name(self.session, name_item)
        self.last_item = data
        return data

    def check_if_item_in_fridge(self, n, e, q, u, l_n):
        last_checked_name = l_n
        old_item_from_entered_name = self.db.get_data_for_item_from_name(self.session, n)
        if not old_item_from_entered_name:
            to_be_updated = False
            return n, e, q, u, to_be_updated, last_checked_name
        else:
            # a = entered_name
            # print(a)
            old_item = old_item_from_entered_name
            last_checked_name = old_item.name
            # l_name = last_checked_name
            old_expiry = old_item.expiry
            old_quantity = old_item.amount
            old_units = old_item.unit
            if old_expiry != e or old_units != u:
                new_num_to_add = 1
                last_char = last_checked_name[-1]
                l_new_name = old_item.name + str(new_num_to_add)
                if last_char.isdigit():
                    new_num_to_add = int(last_checked_name[-1]) + 1
                    l_new_name = last_checked_name[:-1] + str(new_num_to_add)
                n_name, n_e, n_q, n_u, to_be_updated, last_name = self.check_if_item_in_fridge(l_new_name, e, q, u,
                                                                                               last_checked_name)
                return n_name, n_e, n_q, n_u, to_be_updated, last_name
            else:
                to_be_updated = True
                sum = int(q) + int(old_quantity)
                return n, e, sum, u, to_be_updated, last_checked_name

    def item_action_buttons(self, action):
        try:
            if action == 'clear':
                self.last_item = ''
                self.view.set_values()
                self.view.enable_buttons()
            elif action == 'add':
                name_item, quantity, unit, expiry_date, main_category, sub_category = self.view.get_values()
                data = self.check_if_item_in_fridge(name_item, expiry_date, quantity, unit, name_item)

                new_name, n_expiry_date, n_quantity, n_unit, to_be_updated, last_checked_name = data
                if not to_be_updated:

                    item = Item(name=new_name, amount=n_quantity, unit=n_unit, expiry=str(n_expiry_date),
                                sub_category_id=self.db.get_sub_id(self.session, sub_category), fridge_id=self.fridge.id)
                    print(item)
                    self.last_item = item
                    self.db.add_item_to_fridge(self.session, item)
                else:
                    self.db.set_data_for_item_from_name(self.session, last_checked_name, new_name, n_quantity, n_unit,
                                                        n_expiry_date, sub_category)

                self.view.set_values()
                self.generate_choices()
                self.view.enable_buttons()
                self.last_item = ''

            elif action == 'delete':
                self.db.delete_item_from_fridge(self.session, self.last_item)
                self.view.set_values()
                self.generate_choices()
                self.view.enable_buttons()
                self.last_item = ''
            elif action == 'update':
                name_item, quantity, unit, expiry_date, main_category, sub_category = self.view.get_values()
                old_name = self.last_item.name
                old_expiry = self.last_item.expiry
                if str(old_expiry) == str(expiry_date) and old_name == name_item:
                    self.db.set_data_for_item_from_name(self.session, old_name, name_item, quantity, unit, expiry_date,
                                                        sub_category)
                else:
                    name_item, quantity, unit, expiry_date, to_be_updated, l_n = self.check_if_item_in_fridge(
                        name_item, quantity, unit, expiry_date, self.last_item.name)
                    if not to_be_updated:
                        item = Item(name=name_item, amount=quantity, unit=unit, expiry=str(expiry_date),
                                    sub_category_id=self.db.get_sub_id(self.session, sub_category),
                                    fridge_id=self.fridge.id)
                        # self.db.delete_item_from_fridge(self.session, self.last_item)
                        self.db.add_item_to_fridge(self.session, item)
                self.view.set_values()
                self.generate_choices()
                self.view.enable_buttons()
                self.last_item = ''
            elif action == 'remove':
                _, quantity, unit, _, _, _ = self.view.get_values()
                old_name = self.last_item.name
                old_quantity = self.last_item.amount
                old_unit = self.last_item.unit
                old_expiry = self.last_item.expiry
                old_sub = self.last_item.sub_category
                new_quantity = 1
                if unit == old_unit:
                    new_quantity = int(old_quantity) - int(quantity)
                    print(new_quantity)
                if new_quantity >= 1:
                    self.db.set_data_for_item_from_name(self.session,
                                                        old_name, old_name, new_quantity, old_unit, old_expiry, old_sub)
                else:
                    self.db.delete_item_from_fridge(self.session, self.last_item)
                self.view.set_values()
                self.view.enable_buttons()
                self.generate_choices()
                self.last_item = ''
        except AttributeError:
            pass

    def action_buttons(self, action):
        actions = {
            'add': self.view.add_frame,
            'cook': self.view.cook_frame,
            'random': self.view.cook_random_recipe_frame,
            'choose': self.view.cook_chosen_recipe_frame,
            # 'home': self.view.ask_frame,
            'fruits_vegetables': self.view.fruits_vegetables_frame,
            'meat_fish': self.view.meat_fish_frame,
            'cereals_cereal_products': self.view.cereals_cereal_products_frame,
            'milk_milk_products': self.view.milk_milk_products_frame,
            'oils_fats': self.view.oils_fats_frame,
            'legumes_nuts_seeds': self.view.legumes_nuts_seeds_frame,
            'sweets_spices': self.view.sweets_spices_frame,
            'condiments_beverages': self.view.condiments_beverages_frame,
            'others': self.view.add_item_frame,
            'fruits': self.view.add_item_frame,
            'vegetables': self.view.add_item_frame,
            'meat': self.view.add_item_frame,
            'fish': self.view.add_item_frame,
            'cereals': self.view.add_item_frame,
            'cereal product': self.view.add_item_frame,
            'milk': self.view.add_item_frame,
            'milk product': self.view.add_item_frame,
            'oils': self.view.add_item_frame,
            'fats': self.view.add_item_frame,
            'legumes': self.view.add_item_frame,
            'nuts': self.view.add_item_frame,
            'seeds': self.view.add_item_frame,
            'sweets': self.view.add_item_frame,
            'spices': self.view.add_item_frame,
            'condiments': self.view.add_item_frame,
            'beverages': self.view.add_item_frame,
        }

        try:
            sub_cat = action
            self.view.raise_above_all(actions[action], sub_cat)
        except KeyError:
            pass

    def generate_choices(self, *args):
        if not args:
            var = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
            self.view.set_choices(var)
            self.view.choices = var
        else:
            var = self.db.get_items_by_category(self.session, args[0])
            self.view.set_choices(var)
            self.view.choices = var


if __name__ == '__main__':
    food_manager = Controller()
    food_manager.main()
