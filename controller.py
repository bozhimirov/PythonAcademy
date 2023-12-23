import time
from datetime import date, datetime, timedelta

import PIL
from PIL import ImageTk, Image

import segno
from segno import helpers
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
from models_new import DataBase, Item, RecipeSuggestion, Ingredient, Recipe, Base, Fridge, User, SubCategory


class Controller:
    api_keys = ['apiKey=69f4da8ccbdd4431954fdc77a282b0cf', 'apiKey=c0a99b232eb44675a3f26b0945867318',
                     'apiKey=532e06fb4a034e55aa0a28d915c8ab4b', 'apiKey=4bb99921a1fa470bb800293b23863d29']

    def __init__(self):
        self.engine = create_engine('sqlite:///mydatabase.db')
        # self.temp_engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(self.engine)
        # Base.metadata.create_all(self.temp_engine)
        self.session = Session(self.engine)
        # self.temp_session = Session(self.temp_engine)
        self.db = DataBase
        self.fridge = self.session.get(Fridge, 1)
        self.expired_products = []
        self.check_for_expired_products()
        self.view = View(self)
        self.generate_choices()
        self.last_item = ''
        self.expired_products = []
        self.check_for_expired_products()
        # self.chosen_ingredients = self.chosen(self.view.chosen_products)
        self.recipes = []
        # for testing------TOBE removed
        # self.recipes = self.get_recipes_by_items()
        # self.get_recipe_by_id(self.recipes[1])
        self.chosen_recipe = object


    def check_for_expired_products(self):
        items = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
        for item in items:
            if item.expiry < str(date.today()):
                self.expired_products.append(item)
        print(self.expired_products)

    def chosen(self, list_chosen_ingr):
        # list_chosen_ingr = self.get_ingr()
        if len(list_chosen_ingr) == 0:
            # return random_recipe
            pass
        to_str_chosen_ingr = (',+').join(list_chosen_ingr)

        return to_str_chosen_ingr

    # def get_ingr(self):
    #     chosen_ingredients = ['milk', 'potato', 'eggs', 'chicken', 'onion']
    #     return chosen_ingredients

    def get_recipes_by_items(self):
        url = f'https://api.spoonacular.com/recipes/findByIngredients?' \
              f'{self.api_keys[1]}&ingredients={self.chosen_ingredients}&number=5&tags="main course"'

        response = requests.get(url)
        list_ids = []
        print(response)
        if response.status_code < 400:
            results = (response.json())
            # self.write_recipe_to_file(results)
            for result in results:
                list_ids.append(result['id'])
            list_recipes = self.get_bulk_recipes_by_ids(list_ids)
            return list_recipes
        else:
            print(response)

    def get_random_recipes(self):
        self.api_keys = ['apiKey=69f4da8ccbdd4431954fdc77a282b0cf', 'apiKey=c0a99b232eb44675a3f26b0945867318', 'apiKey=532e06fb4a034e55aa0a28d915c8ab4b', 'apiKey=4bb99921a1fa470bb800293b23863d29']

        random_url = f'https://api.spoonacular.com/recipes/random?number=5&{self.api_keys[1]}&tags="main course"'
        response = requests.get(random_url)
        # print(response)

        recipes = []
        if response.status_code < 400:
            results = (response.json())
            rec = results['recipes']
            for r in rec:
                rr_id = r['id']
                r_name = r['title']
                r_ingredients = r["extendedIngredients"]
                r_image = ''
                try:
                    r_image = r['image']
                except KeyError:
                    pass
                r_instructions = r['instructions']
                # r_analyzedInstructions = results['analyzedInstructions']
                # steps = r_analyzedInstructions[0]["steps"]
                recipe = Recipe(
                    recipe_id=rr_id, title=r_name, image=r_image, instructions=r_instructions)
                for i in r_ingredients:
                    amount, unit = self.make_unit(i['measures']['metric']['amount'], i['measures']['metric']['unitShort'])
                    ingredient = Ingredient(
                        name=i['name'], amount=amount, unit=unit)
                    recipe.ingredients.append(ingredient)
                recipes.append(recipe)
            return recipes

    def get_recipe_by_name(self, name):
        if self.view.recipes_from_chosen_products:
            for fr in self.view.recipes_from_chosen_products:
                if fr.title == name:
                    return fr
        else:
            for fr in self.db.check_if_recipe_in_fridge(self.session, name):
                if fr.title == name:
                    return fr



    def get_bulk_recipes_by_ids(self, ids):
        ids = [str(x) for x in ids]
        recipe_ids = ','.join(ids)
        url = f'https://api.spoonacular.com/recipes/informationBulk?{self.api_keys[1]}&ids={recipe_ids}'
        response = requests.get(url)
        results = response.json()
        recipes = []
        for r in results:
            rr_id = r['id']
            r_name = r['title']
            r_ingredients = r["extendedIngredients"]
            r_image = ''
            try:
                r_image = r['image']
            except KeyError:
                pass
            r_instructions = r['instructions']
            # r_analyzedInstructions = results['analyzedInstructions']
            # steps = r_analyzedInstructions[0]["steps"]
            recipe = Recipe(
                recipe_id=rr_id, title=r_name, image=r_image, instructions=r_instructions)
            for i in r_ingredients:
                amount, unit = self.make_unit(i['measures']['metric']['amount'], i['measures']['metric']['unitShort'])
                ingredient = Ingredient(
                    name=i['name'], amount=amount, unit=unit)
                recipe.ingredients.append(ingredient)
            recipes.append(recipe)
        return recipes

    def get_recipe_by_id(self, recipe):
        recipe_id = ''
        if type(recipe) == str:
            recipe = self.get_recipe_by_name(recipe)
        try:
            # if recipe.recipe_id:
            recipe_id = recipe.recipe_id
        except AttributeError:
            recipe_id = recipe.id
        url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?{self.api_keys[1]}'
        response = requests.get(url)
        results = response.json()
        r_id = results['id']
        r_name = results['title']
        r_ingredients = results["extendedIngredients"]
        r_image = ''
        try:
            r_image = results['image']
        except KeyError:
            r_image = ''
        r_instructions = results['instructions']
        # r_analyzedInstructions = results['analyzedInstructions']
        # steps = r_analyzedInstructions[0]["steps"]
        recipe = Recipe(
            recipe_id=r_id, title=r_name, image=r_image, instructions=self.remole_li(r_instructions))
        for i in r_ingredients:
            amount, unit = self.make_unit(i['measures']['metric']['amount'], i['measures']['metric']['unitShort'])
            ingr_name = self.check_name_len(i['name'], i['nameClean'])
            ingredient = Ingredient(
                name=i['name'], amount=amount, unit=unit)
            recipe.ingredients.append(ingredient)
        # for i in steps:
        #     recipe.analyzedInstructions[i['number']] = i['step']
        # return recipe
        self.chosen_recipe = recipe
        # self.add_to_db(recipe)
        # print(self.chosen_recipe.title)
        # print(self.chosen_recipe.ingredients)
        # print(self.chosen_recipe.instructions)

    @staticmethod
    def check_name_len(name1, name2):
        len_name1 = name1.split(' ')
        len_name2 = name2.split(' ')
        if len_name1 > len_name2:
            return name2
        return name1

    @staticmethod
    def make_unit(amount, unit):
        new_amount = amount
        new_unit = unit
        if unit in ['l', 'ltr']:
            new_amount = int(float(amount) * 1000)
            new_unit = 'ml'
        elif unit in ['kg', 'kgs']:
            new_amount = int(float(amount) * 1000)
            new_unit = 'g'
        elif unit in ['tbsp', 'tbsps', 'Tbsp', 'Tbsps', 'sp', 'sps']:
            new_amount = int(amount) * 0.02
            new_unit = 'g'
        elif unit in ['tsp', 'tsps']:
            new_amount = int(amount) * 0.01
            new_unit = 'g'
        elif unit in ['cup', 'tea cup', 'glass']:
            new_amount = int(amount) * 0.2
            new_unit = 'ml'
        elif unit in ['', 'serving', 'servings', 'large', 'large bunch', 'cloves', 'can', 'cans', 'bunch', 'small', 'medium', 'pinch']:
            new_unit = 'count'
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
                sum = int(float(q)) + int(float(old_quantity))
                return n, e, sum, u, to_be_updated, last_checked_name

    def initial_data(self):
        names = [
            (self.view.first_user_entry, self.view.first_user_mail_entry),
            (self.view.sec_user_entry, self.view.sec_user_mail_entry),
            (self.view.third_user_entry, self.view.third_user_mail_entry),
            (self.view.four_user_entry, self.view.four_user_mail_entry),
            (self.view.fifth_user_entry, self.view.fifth_user_mail_entry),
            (self.view.sixth_user_entry, self.view.sixth_user_mail_entry),
            (self.view.sev_user_entry, self.view.sev_user_mail_entry),
                 ]
        fridge_name = self.view.init_name_entry.get()
        self.fridge.name = self.db.check_fridge_name(fridge_name)
        for i in range(0, self.view.clean_row - 3):
            try:

                fu = names[i][0].get()
                fm = names[i][1].get()
                if fu and fm:
                    user = User(
                        username=fu.capitalize(),
                        mail=fm,
                        fridge_id=self.fridge.id
                    )

                    self.session.add(user)
                    self.session.commit()
            except IndexError:
                pass
        self.session.commit()
        if not self.db.get_all_sub_cat(self.session):
            for i in self.db.CATEGORIES:
                s_c = SubCategory(name=i)
                self.session.add(s_c)
                self.session.commit()
        self.view.welcome['text'] = f'Welcome,\n{self.fridge.name}'
        self.view.on_start()

    def recipe_action_buttons(self, action):
        if action == 'generate':
            self.chosen_ingredients = self.chosen(self.view.chosen_products)
            self.view.recipes_from_chosen_products = self.get_recipes_by_items()
            if self.view.recipes_from_chosen_products:
                self.view.set_recipes(self.view.recipes_from_chosen_products)
                self.view.clear_used_missed_instructions()
            else:
                self.view.clear_used_missed_instructions()
                self.view.set_recipes([])
                self.view.recipe_description_text.insert(1.0, 'Sorry! No products selected!\nYou can try choosing products\nor try get random recipe!')
        elif action == 'random':
            self.view.recipes_from_chosen_products = []
            self.view.random_recipes = self.get_random_recipes()
            self.view.set_recipes(self.view.random_recipes)
            self.view.clear_used_missed_instructions()
        elif action == 'add_favourites':
            if self.chosen_recipe is not None:
                if not self.db.check_if_recipe_in_fridge(self.session, self.chosen_recipe):
                    self.chosen_recipe.fridge_id = self.fridge.id

                    if not self.db.check_if_recipe_in_fridge(self.session, self.chosen_recipe):
                        self.db.add_recipe_to_fridge(self.session, self.chosen_recipe)
        elif action == 'favourites':
            self.chosen_recipe = None
            self.view.recipes_from_chosen_products = []
            self.view.random_recipes = []
            if self.db.get_all_recipes(self.session, self.fridge.id):
                self.view.set_recipes(self.db.get_all_recipes(self.session, self.fridge.id))
                self.view.clear_used_missed_instructions()
            else:
                self.view.clear_used_missed_instructions()
                self.view.recipe_description_text.insert(1.0, 'Sorry! No favourite recipes available!\nAdd favourite recipes first!')
        elif action == 'shopping_list':
            if self.chosen_recipe:
                for ingred in self.chosen_recipe.ingredients:
                    if ingred:
                        item = self.check_if_ingredient_is_in_fridge(ingred)
                        ingr = self.check_if_ingredient_is_shopping_list(ingred)
                        if not item and ingr:
                            self.view.shopping.append(ingred)
                self.data = 'Shopping List\n'
                counter = 0
                for i in self.view.shopping:
                    new_i = i.name.replace("'", '')
                    txt = f'• {new_i} - {i.amount} {i.unit}\n'
                    self.data += f'• {new_i} - {i.amount} {i.unit}\n'
                    # i = Label(self.view.shopping_list_content)
                    # i.grid(column=0, row=counter)
                    Label(self.view.shopping_list_content, text=txt).grid(column=0, row=counter, sticky='wns')
                    Button(self.view.shopping_list_content, text='x', command=lambda x=i: self.remove(x)).grid(column=1, row=counter, sticky='ens')

                    # Label(self.view.shopping_list_content, text=txt).grid(column=0, row=counter)
                    # Button(self.view.shopping_list_content, text='x', command=lambda x=i: self.remove(x)).grid(column=1, row=counter)
                    counter += 1
            img = segno.make(self.data)
            img.save('images/data.png', border=2, scale=3)

            # for content in self.fridge.content:
            #     # print(self.chosen_recipe.ingredients)
            #     # a = self.chosen_recipe
            #     for ingr in self.chosen_recipe.ingredients:
            #         print(ingr)
            #         if ingr.name not in content.name:
            #             self.view.shopping_list.append(ingr)

            if self.view.shopping:
                global qr
                qr = PhotoImage(file='images/data.png')
                self.view.label_qr.config(image=qr)
                self.view.label_qr.grid(column=0, row=0)
            # self.view.qr['image'] = qr
            # self.view.qr.grid(column=0, row=0)
            self.view.raise_above_all(self.view.shopping_list_frame, '')
            print(self.view.shopping)

        elif action == 'get_shopping_list':
            # data = ''
            # for i in self.view.shopping_list:
            #     data += f'&#  {i} &#x2718"\n"'
            #     self.view.shopping_list_content['text'] = data
            # img = segno.make(data)
            # img.save('./data.gif', border=5, scale=5)
            # time.sleep(2)
            # qr_code = Image.open("data.gif")
            # self.view.qr['image'] = qr_code
            # im = PIL.Image.open('data.gif')
            # ph = ImageTk.PhotoImage(im)
            # self.view.qr['image'] = ph
            # self.view.choiceshopvar.set(self.view.shopping)
            if self.view.shopping:
                qr = PhotoImage(file='images/data.png')
                self.view.label_qr.config(image=qr)
                self.view.label_qr.grid(column=0, row=0)
            # self.view.qr['image'] = qr
            # self.view.qr.grid(column=0, row=0)
            self.view.raise_above_all(self.view.shopping_list_frame, '')

    def remove(self, *x):
        try:
            self.view.shopping.remove(x)
        except ValueError:
            self.view.shopping.remove(x[0])
        a = self.view.shopping_list_content.winfo_children()
        for i in a:
            i.destroy()
        self.data = 'Shopping List\n'
        counter = 0
        for i in self.view.shopping:
            new_i = i.name.replace("'", '')
            txt = f'• {new_i} - {i.amount} {i.unit}\n'
            self.data += f'• {new_i} - {i.amount} {i.unit}\n'
            Label(self.view.shopping_list_content, text=txt).grid(column=0, row=counter, sticky='wns')
            Button(self.view.shopping_list_content, text='x', command=lambda x=i: self.remove(x)).grid(column=1, row=counter,
                                                                                                       sticky='ens')
            counter += 1
        img = segno.make(self.data)
        img.save('images/data.png', border=2, scale=3)
        if self.view.shopping:
            global qr
            qr = PhotoImage(file='images/data.png')
            self.view.label_qr.config(image=qr)
            self.view.label_qr.grid(column=0, row=0)
        self.view.raise_above_all(self.view.shopping_list_frame, '')

    def clear_shopping_list(self):
        a = self.view.shopping_list_content.winfo_children()
        for i in a:
            i.destroy()
        self.view.shopping = []
        self.data = 'Shopping List\n'
        counter = 0
        for i in self.view.shopping:
            new_i = i.name.replace("'", '')
            txt = f'• {new_i} - {i.amount} {i.unit}\n'
            self.data += f'• {new_i} - {i.amount} {i.unit}\n'
            Label(self.view.shopping_list_content, text=txt).grid(column=0, row=counter, sticky='nsw')
            Button(self.view.shopping_list_content, text='x', command=lambda x=i: self.remove(x)).grid(column=1,
                                                                                                       row=counter, sticky='ens')
            counter += 1
        img = segno.make(self.data)
        img.save('images/data.png', border=2, scale=3)
        global qr
        qr = PhotoImage(file='images/data.png')
        self.view.label_qr.config(image=qr)
        self.view.label_qr.grid(column=0, row=0)

    def change_spinbox(self, e):
        units = ('count', 'ml', 'l', 'g', 'kg')
        data = {
            units[0]: (1, 100, 1),
            units[1]: (50, 10000, 50),
            units[2]: (0.1, 10, 0.1),
            units[3]: (50, 10000, 50),
            units[4]: (0.1, 10, 0.1)
        }
        sel_unit = self.view.units_entry.get()
        current_value = self.view.quantity_entry.get()
        if not current_value:
            if sel_unit == units[0]:
                self.view.quantity_entry.config(from_=data[units[0]][0], to=data[units[0]][1], increment=data[units[0]][2])
                # self.view.quantity_val.set(data[units[0]][0])
                # self.view.update()
            elif sel_unit == units[1]:
                self.view.quantity_entry.config(from_=data[units[1]][0], to=data[units[1]][1], increment=data[units[1]][2])
                # self.view.quantity_val.set(data[units[1]][0])
                # self.view.update()
            elif sel_unit == units[2]:
                self.view.quantity_entry.config(from_=data[units[2]][0], to=data[units[2]][1], increment=data[units[2]][2])
                # self.view.quantity_val.set(data[units[2]][0])
                # self.view.update()
            elif sel_unit == units[3]:
                self.view.quantity_entry.config(from_=data[units[3]][0], to=data[units[3]][1], increment=data[units[3]][2])
                # self.view.quantity_val.set(data[units[3]][0])
                # self.view.update()
            elif sel_unit == units[4]:
                self.view.quantity_entry.config(from_=data[units[4]][0], to=data[units[4]][1], increment=data[units[4]][2])
                # self.view.quantity_val.set(data[units[4]][0])
                # self.view.update()
        else:
            if sel_unit in ['ml', 'g']:
                value = int(float(current_value) * 1000)
                self.view.quantity_val.set(value)
                self.view.quantity_entry.config(from_=data[units[1]][0], to=data[units[1]][1], increment=data[units[1]][2])
                # self.view.update()
            elif sel_unit in ['l', 'kg']:
                value = float(current_value) / 1000
                self.view.quantity_val.set(value)
                self.view.quantity_entry.config(from_=data[units[2]][0], to=data[units[2]][1], increment=data[units[2]][2])
                # self.view.update()

    def destroy_top_btn(self):
        self.pop.destroy()
        self.pop_label.destroy()

    def delete_expired(self):
        for item in self.expired_products:
            self.db.delete_item_from_fridge(self.session, item)
        self.view.pop_expired.destroy()
        self.view.pop_expired_label.destroy()



    def send_mail(self, *arg):
        # mail = ''
        if arg:
            mail = arg
        else:
            mail = self.view.mail_entry_r.get()
        global qr_to_send
        qr_mail = segno.helpers.make_email(to=mail, subject='Shopping List', body=self.data)
        qr_mail.save('images/qr_mail.png', border=2, scale=3)
        qr_to_send = PhotoImage(file='images/qr_mail.png')
        # self.view.label_qr.config(image=qr)
        # self.view.label_qr.grid(column=0, row=0)
        # time.sleep(0.5)
        # self.pop = Label(self.view.shopping_list_frame, image=qr_to_send)
        self.pop = Button(self.view.shopping_list_frame, image=qr_to_send, command=self.destroy_top_btn)
        self.pop_label = Label(self.view.shopping_list_frame, text='Click to return', font=('bold', 10))
        self.pop.grid(column=0, row=1, sticky='news')
        self.pop_label.grid(column=0, row=2, sticky='news')

    def add_new_user(self):
        self.name_btns = [
            [self.view.sec_user_label, self.view.sec_user_entry, self.view.sec_user_mail, self.view.sec_user_mail_entry],
            [self.view.third_user_label, self.view.third_user_entry, self.view.third_user_mail, self.view.third_user_mail_entry],
            [self.view.four_user_label, self.view.four_user_entry, self.view.four_user_mail, self.view.four_user_mail_entry],
            [self.view.fifth_user_label, self.view.fifth_user_entry, self.view.fifth_user_mail, self.view.fifth_user_mail_entry],
            [self.view.sixth_user_label, self.view.sixth_user_entry, self.view.sixth_user_mail, self.view.sixth_user_mail_entry],
            [self.view.sev_user_label, self.view.sev_user_entry, self.view.sev_user_mail, self.view.sev_user_mail_entry],

        ]
        try:
            self.name_btns[self.view.clean_row - 4][0].grid(column=0, row=self.view.clean_row, pady=5, sticky='e')
            self.name_btns[self.view.clean_row - 4][1].grid(column=1, row=self.view.clean_row, padx=(0, 30))
            self.name_btns[self.view.clean_row - 4][2].grid(column=2, row=self.view.clean_row, padx=5)
            self.name_btns[self.view.clean_row - 4][3].grid(column=3, row=self.view.clean_row)

            self.view.clean_row += 1
        except IndexError:
            self.view.add_user_btn.config(state='disabled')





    def check_if_ingredient_is_in_fridge(self, ingredient):
        self.ingredients_not_to_buy = ['water', 'salt', 'table salt', 'salt and pepper', 'flour']
        for item in self.fridge.content:
            if item.name in ingredient.name or ingredient.name in item.name or ingredient.name in self.ingredients_not_to_buy:

                if float(item.amount) >= float(ingredient.amount):
                    new_amount = float(item.amount) - float(ingredient.amount)
                    self.db.set_data_for_item_from_name(self.session, item.name, item.name, int(new_amount), item.unit, item.expiry, item.sub_category)
                    return item

    def check_if_ingredient_is_shopping_list(self, ingredient):
        if len(self.view.shopping) > 0:
            for item in self.view.shopping:
                if item.name in ingredient.name or ingredient.name in item.name:
                    return None
            return ingredient
        else:
            return ingredient


    def item_action_buttons(self, action):
        try:
            if action == 'clear':
                self.last_item = ''
                self.view.set_values()
                self.view.enable_buttons()
                self.view.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
                self.view.name_entry.focus()

            elif action == 'add':
                name_item, quantity, unit, expiry_date, sub_category = self.view.get_values()
                if name_item:
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
                    self.view.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
                    self.view.name_entry.focus()


            elif action == 'delete':
                self.db.delete_item_from_fridge(self.session, self.last_item)
                self.view.set_values()
                self.generate_choices()
                self.view.enable_buttons()
                self.last_item = ''
                self.view.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
                self.view.name_entry.focus()

            elif action == 'update':
                name_item, quantity, unit, expiry_date, sub_category = self.view.get_values()
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
                self.view.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
                self.view.name_entry.focus()

            elif action == 'remove':
                _, quantity, unit, _, _ = self.view.get_values()
                old_name = self.last_item.name
                old_quantity = self.last_item.amount
                old_unit = self.last_item.unit
                old_expiry = self.last_item.expiry
                old_sub = self.last_item.sub_category
                new_quantity = 1
                if unit == old_unit:
                    new_quantity = float(old_quantity) - float(quantity)
                    # print(new_quantity)
                if new_quantity >= 1:
                    self.db.set_data_for_item_from_name(self.session,
                                                        old_name, old_name, int(new_quantity), old_unit, old_expiry, old_sub)
                else:
                    self.db.delete_item_from_fridge(self.session, self.last_item)
                self.view.set_values()
                self.view.enable_buttons()
                self.generate_choices()
                self.last_item = ''
                self.view.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
                self.view.name_entry.focus()

        except AttributeError:
            pass

    def action_buttons(self, action):
        actions = {
            'add': self.view.add_frame,
            'cook': self.view.cook_frame,
            'random': self.view.cook_chosen_recipe_frame,
            'favourite': self.view.cook_chosen_recipe_frame,
            'choose': self.view.cook_chosen_recipe_frame,
            # 'home': self.view.ask_frame,
            # 'fruits_vegetables': self.view.fruits_vegetables_frame,
            # 'meat_fish': self.view.meat_fish_frame,
            # 'cereals_cereal_products': self.view.cereals_cereal_products_frame,
            # 'milk_milk_products': self.view.milk_milk_products_frame,
            # 'oils_fats': self.view.oils_fats_frame,
            # 'legumes_nuts_seeds': self.view.legumes_nuts_seeds_frame,
            # 'sweets_spices': self.view.sweets_spices_frame,
            # 'condiments_beverages': self.view.condiments_beverages_frame,
            'other': self.view.add_item_frame,
            'fruits': self.view.add_item_frame,
            'vegetables': self.view.add_item_frame,
            'meat': self.view.add_item_frame,
            'fish': self.view.add_item_frame,
            'cereals': self.view.add_item_frame,
            # 'cereal product': self.view.add_item_frame,
            'dairy': self.view.add_item_frame,
            # 'milk product': self.view.add_item_frame,
            'oils': self.view.add_item_frame,
            # 'fats': self.view.add_item_frame,
            'legumes': self.view.add_item_frame,
            # 'nuts': self.view.add_item_frame,
            # 'seeds': self.view.add_item_frame,
            # 'sweets': self.view.add_item_frame,
            # 'spices': self.view.add_item_frame,
            # 'condiments': self.view.add_item_frame,
            # 'beverages': self.view.add_item_frame,
        }

        try:
            self.generate_choices()
            sub_cat = action
            self.view.raise_above_all(actions[action], sub_cat)
        except KeyError:
            pass

    def remove_from_fridge_if_any(self):
        for sh in self.view.shopping:
            fridge_analog = self.db.get_data_for_item_from_name(self.session, sh)

            new_quantity = 1
            if sh.unit == fridge_analog.unit:
                new_quantity = float(fridge_analog.unit) - float(sh.unit)
                # print(new_quantity)
            if new_quantity >= 1:
                self.db.set_data_for_item_from_name(self.session, fridge_analog.name, fridge_analog.name, int(new_quantity),
                                                    fridge_analog.unit, fridge_analog.expiry)
            else:
                self.db.delete_item_from_fridge(self.session, fridge_analog)



    def remole_li(self, instructions):
        if instructions:
            i = instructions.replace('<ol>', '')
            i1 = i.replace('<li>', '')
            i2 = i1.replace('<p>', '')
            i3 = i2.replace('</p>', '\n')
            i4 = i3.replace('</li>', '\n')
            i5 = i4.replace('</ol>', '\n')
            return i5
        else:
            return instructions

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
