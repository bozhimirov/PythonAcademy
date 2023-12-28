import math
import string
import time
from datetime import date
import os
from dotenv import load_dotenv
import PIL
from PIL import Image
import segno
from validate_email import validate_email
from segno import helpers
from PIL import ImageTk
from tkinter import *
from tkinter import ttk
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from master_project.db import DataBase
from master_project.view import View
from model import Item, Ingredient, Recipe, Base, Fridge, User, SubCategory


class Controller:
    load_dotenv()
    ENV = os.getenv('api_keys')
    api_keys = ENV

    ingredients_not_to_buy = ['water', 'salt', 'table salt', 'salt and pepper', 'flour', 'half and half',
                              'pepper', 'sugar']

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
        self.wait = False
        self.view = View(self)
        self.generate_choices()
        self.last_item = ''
        self.expired_products = []
        self.check_for_expired_products()
        self.recipes = []
        self.chosen_recipe = object

    @staticmethod
    def remove_digits(name):
        n_name = ''
        for ch in name:
            if not ch.isdigit():
                n_name += ch
        return n_name

    @staticmethod
    def make_qr_code(data):
        img = segno.make(data)
        img.save('images/data.png', border=2, scale=7)
        imgo = PIL.Image.open("images/data.png")
        resized_image = imgo.resize((250, 250))
        qrr = ImageTk.PhotoImage(resized_image)
        return qrr

    @staticmethod
    def remove_li(instructions):
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

    @staticmethod
    def chosen(list_chosen_ingr):
        if len(list_chosen_ingr) == 0:
            pass
        to_str_chosen_ingr = ',+'.join(list_chosen_ingr)
        return to_str_chosen_ingr

    @staticmethod
    def check_name_len(name1, name2):
        len_name1 = name1.split(' ')
        if name2:
            len_name2 = name2.split(' ')
            if len_name1 > len_name2:
                return name2
        return name1

    @staticmethod
    def make_unit(amount, unit):
        new_amount = amount
        new_unit = unit
        if unit in ['l', 'ltr']:
            new_amount = int(round(float(amount) * 1000, 0))
            new_unit = 'ml'
        elif unit in ['kg', 'kgs']:
            new_amount = int(round(float(amount * 1000), 0))
            new_unit = 'g'
        elif unit in ['g']:
            new_amount = int(round(float(amount), 0))
            new_unit = 'g'
        elif unit in ['tbsp', 'tbsps', 'Tbsp', 'Tb', 'Tbs', 'Tbsps', 'sp', 'sps', 'slice', 'slices']:
            new_amount = int(round(float(amount * 20), 0))
            new_unit = 'g'
        elif unit in ['tsp', 'tsps', 'Dash', 'dash', 'Dashes']:
            new_amount = int(round(float(amount * 10), 0))
            new_unit = 'g'
        elif unit in ['cup', 'tea cup', 'glass']:
            new_amount = int(round(float(amount) * 200))
            new_unit = 'ml'
        elif unit in ['gallon', 'gallons']:
            new_amount = int(round(amount * 3785, 0))
            new_unit = 'ml'
        elif unit in ['Lb', 'lb', 'pound', 'pounds']:
            new_amount = int(round(amount * 454, 0))
            new_unit = 'g'
        elif unit in ['sticks', 'stick', 'pts']:
            new_amount = int(round(amount * 250, 0))
            new_unit = 'g'
        elif unit in ['ounces', 'ounce', 'Ounces', 'Ounce']:
            new_amount = int(round(amount * 28, 0))
            new_unit = 'g'
        elif unit in ['', 'serving', 'servings', 'large', 'large bunch', 'cloves', 'can', 'cans', 'bunch', 'small',
                      'medium', 'pinch', 'pkg', 'stalks', 'inch', 'inches', 'fillet', 'clove', 'small bunch', 'Bunch',
                      'loaf', 'large clove', 'leaf', 'Clove', 'head', 'pinches', 'large can', 'sprig', 'handfuls',
                      'strips', 'Cloves', 'strip', 'Handful', 'Handfuls', 'handful', 'medium size', 'pkt', 'sprigs']:
            new_amount = math.ceil(amount)
            new_unit = 'count'
        return str(new_amount), new_unit

    def check_for_expired_products(self):
        items = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
        for item in items:
            if item.expiry < str(date.today()):
                self.expired_products.append(item)

    def get_recipes_by_items(self):
        url = f'https://api.spoonacular.com/recipes/findByIngredients?' \
              f'{self.api_keys}&ingredients={self.chosen_ingredients}&number=10&tags="main course"'
        response = requests.get(url)
        list_ids = []
        if response.status_code < 400:
            results = (response.json())
            for result in results:
                list_ids.append(result['id'])
            list_recipes = self.get_bulk_recipes_by_ids(list_ids)
            return list_recipes

    def get_random_recipes(self):
        random_url = f'https://api.spoonacular.com/recipes/random?number=10&{self.api_keys}&tags="main course"'
        response = requests.get(random_url)
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
                recipe = Recipe(
                    recipe_id=rr_id, title=r_name, image=r_image, instructions=r_instructions)
                for i in r_ingredients:
                    amount, unit = self.make_unit(i['measures']['metric']['amount'],
                                                  i['measures']['metric']['unitShort'])
                    ingr_name = i['name']
                    if i['nameClean']:
                        ingr_name = self.check_name_len(i['name'], i['nameClean'])
                    ingredient = Ingredient(
                        name=ingr_name, amount=amount, unit=unit)
                    for j in self.ingredients_not_to_buy:
                        if ingredient.name not in j or j not in ingredient.name:
                            if ingredient not in recipe.ingredients:
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
        url = f'https://api.spoonacular.com/recipes/informationBulk?{self.api_keys}&ids={recipe_ids}'
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
            recipe = self.create_recipe(rr_id, r_name, r_image, r_instructions, r_ingredients)
            recipes.append(recipe)
        return recipes

    def create_recipe(self, r_id, r_name, r_image, r_instructions, r_ingredients):
        recipe = Recipe(
            recipe_id=r_id, title=r_name, image=r_image, instructions=self.remove_li(r_instructions))
        for i in r_ingredients:
            amount, unit = self.make_unit(i['measures']['metric']['amount'], i['measures']['metric']['unitShort'])
            ingr_name = self.check_name_len(i['name'], i['nameClean'])
            ingredient = Ingredient(
                name=ingr_name, amount=amount, unit=unit)
            for j in self.ingredients_not_to_buy:
                if ingredient.name not in j or j not in ingredient.name:
                    if ingredient not in recipe.ingredients:
                        recipe.ingredients.append(ingredient)
        return recipe

    def check_ingredients_not_to_buy(self, ingredient):
        for i in self.ingredients_not_to_buy:
            if i in ingredient.name or ingredient.name in i:
                return ''
        return ingredient

    def open_settings(self, command):
        self.wait = command
        time.sleep(5)
        self.view.initial = self.view.make_initial_window(self.view.root, command)

    def handle_letter(self, ltr):
        if ltr == 'enter':
            self.view.quantity_entry.focus()
            return
        elif ltr == 'space':
            ltr = ' '
        elif ltr == 'del':
            txt = self.view.name_entry.get()
            self.view.name_entry.delete(0, END)
            self.view.name_entry.insert(0, txt[:-1])
            ltr = ''
        self.view.name_entry.insert(END, ltr)
        self.view.name_entry.focus()

    def make_letter_buttons(self, parent):
        inner_counter = 0
        for i in string.ascii_lowercase:
            Button(parent, text=i, command=lambda ltr=i: self.handle_letter(ltr), width=3, background='#EBF5FB',
                   foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
                .grid(column=(inner_counter % 10), row=inner_counter // 10, sticky='news', padx=2, pady=2)
            inner_counter += 1
        Button(parent, text='DELETE', command=lambda ltr='del': self.handle_letter(ltr), background='#F9EBEA',
               foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
            .grid(column=inner_counter % 10, row=inner_counter // 10, sticky='news', padx=2, pady=2,
                  columnspan=10 - ((inner_counter - 1) % 10))
        inner_counter += 1
        Button(parent, text='SPACE', command=lambda ltr='space': self.handle_letter(ltr), background='#FEF9E7',
               foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
            .grid(column=0, row=(inner_counter // 10) + 1, columnspan=10, sticky='news', padx=2, pady=2)
        inner_counter += 1
        Button(parent, text='ENTER', command=lambda ltr='enter': self.handle_letter(ltr), background='#E9F7EF',
               foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
            .grid(column=0, row=(inner_counter // 10) + 2, columnspan=10, sticky='news', padx=2, pady=2, ipady=12)

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
            old_item = old_item_from_entered_name
            last_checked_name = old_item.name
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
                sum_q = int(float(q)) + int(float(old_quantity))
                return n, e, sum_q, u, to_be_updated, last_checked_name

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
        valid_name = False
        self.is_valid = False
        if fridge_name:
            self.fridge.name = self.db.check_fridge_name(fridge_name)
            valid_name = True
        else:
            self.view.invalid_name_message.grid(column=1, columnspan=3, row=11)
        if valid_name:
            for i in range(0, self.view.clean_row - 3):
                try:
                    fu = names[i][0].get()
                    if not fu:
                        self.view.invalid_username_message.grid(column=1, columnspan=3, row=11)
                    else:
                        self.fm = names[i][1].get()
                        self.is_valid = validate_email(self.fm)
                        if not self.is_valid:
                            self.view.invalid_mail_message.grid(column=1, columnspan=3, row=11)

                    if fu and self.fm and self.is_valid:
                        self.view.invalid_username_message.grid_forget()
                        self.view.invalid_mail_message.grid_forget()
                        reg_users = [x.username for x in self.db.get_all_users(self.session, self.fridge.id)]
                        if fu not in reg_users:
                            user = User(
                                username=fu.capitalize(),
                                mail=self.fm,
                                fridge_id=self.fridge.id
                            )

                            self.session.add(user)
                            self.session.commit()
                except IndexError:
                    pass
            try:
                if self.is_valid:
                    self.session.commit()
                    if not self.db.get_all_sub_cat(self.session):
                        for i in self.db.CATEGORIES:
                            s_c = SubCategory(name=i)
                            self.session.add(s_c)
                            self.session.commit()
                    self.view.welcome['text'] = f'Welcome,\n{self.fridge.name}'
                    self.wait = False
                    self.view.on_start()
            except AttributeError:
                pass

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
                self.view.recipe_description_text.insert(1.0, 'Sorry! No products selected!\n'
                                                              'You can try choosing products\n'
                                                              'or try get random recipe!')
        elif action == 'random':
            self.view.recipes_from_chosen_products = []
            self.view.random_recipes = self.get_random_recipes()
            self.view.set_recipes(self.view.random_recipes)
            self.view.clear_used_missed_instructions()
        elif action == 'add_favourites':
            if self.chosen_recipe is not None:
                if not self.db.check_if_recipe_in_fridge(self.session, self.chosen_recipe):
                    self.chosen_recipe.fridge_id = self.fridge.id
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
                self.view.set_recipes([])
                self.view.recipe_description_text.insert(1.0, 'Sorry! No favourite recipes available!\n'
                                                              'Add favourite recipes first!')
        elif action == 'shopping_list':
            self.data = 'Shopping List:\nno chosen products'
            if self.chosen_recipe:
                for ingred in self.chosen_recipe.ingredients:
                    if ingred:
                        item = self.check_if_ingredient_is_in_fridge(ingred)
                        ingr = self.check_if_ingredient_is_shopping_list(ingred)
                        if not item and ingr:
                            self.view.shopping.append(ingred)
                self.data = 'Shopping List:\n'
                self.fill_shopping_list_content()

            global qr
            qr = self.make_qr_code(self.data)
            self.view.label_qr.config(image=qr)
            self.view.raise_above_all(self.view.shopping_list_frame, '')
        elif action == 'get_shopping_list':
            data = 'Shopping List:\nno chosen products'
            if self.view.shopping:
                data = 'Shopping List:\n'
            img = segno.make(data)
            img.save('images/data.png', border=2, scale=7)
            imgo = PIL.Image.open("images/data.png")
            resized_image = imgo.resize((250, 250))
            global qq
            qq = ImageTk.PhotoImage(resized_image)
            self.view.label_qr.config(image=qq)
            self.view.raise_above_all(self.view.shopping_list_frame, '')

    def fill_shopping_list_content(self):
        counter = 0
        for i in self.view.shopping:
            new_i = i.name.replace("'", '')
            txt = f'• {new_i} - {i.amount} {i.unit}\n'
            self.data += f'• {new_i} - {i.amount} {i.unit}\n'
            if counter <= 7:
                Label(self.view.shopping_list_content, text=txt).grid(column=0, row=counter, sticky='wns')
                Button(self.view.shopping_list_content, text='x', command=lambda x=i: self.remove(x)).grid(
                    column=1, row=counter, sticky='ens', padx=6)
            else:
                Label(self.view.shopping_list_content2, text=txt).grid(column=0, row=counter - 8, sticky='wns')
                Button(self.view.shopping_list_content2, text='x', command=lambda x=i: self.remove(x)).grid(
                    column=1, row=counter - 8, sticky='ens', padx=6)
            counter += 1

    def remove(self, *x):
        try:
            self.view.shopping.remove(x)
        except ValueError:
            self.view.shopping.remove(x[0])
        a = self.view.shopping_list_content.winfo_children()
        for i in a:
            i.destroy()
        b = self.view.shopping_list_content2.winfo_children()
        for i in b:
            i.destroy()
        self.data = 'Shopping List:\nno chosen products'
        if self.view.shopping:
            self.data = 'Shopping List:\n'
        self.fill_shopping_list_content()
        global qr
        qr = self.make_qr_code(self.data)
        self.view.label_qr.config(image=qr)
        self.view.raise_above_all(self.view.shopping_list_frame, '')

    def clear_shopping_list(self):
        a = self.view.shopping_list_content.winfo_children()
        b = self.view.shopping_list_content2.winfo_children()
        for i in a:
            i.destroy()
        for i in b:
            i.destroy()
        self.view.shopping = []
        self.data = 'Shopping List:\nno chosen products'

        qr = self.make_qr_code(self.data)
        self.view.label_qr.config(image=qr)

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
                self.view.quantity_entry.config(from_=data[units[0]][0], to=data[units[0]][1],
                                                increment=data[units[0]][2])
            elif sel_unit == units[1]:
                self.view.quantity_entry.config(from_=data[units[1]][0], to=data[units[1]][1],
                                                increment=data[units[1]][2])
            elif sel_unit == units[2]:
                self.view.quantity_entry.config(from_=data[units[2]][0], to=data[units[2]][1],
                                                increment=data[units[2]][2])
            elif sel_unit == units[3]:
                self.view.quantity_entry.config(from_=data[units[3]][0], to=data[units[3]][1],
                                                increment=data[units[3]][2])
            elif sel_unit == units[4]:
                self.view.quantity_entry.config(from_=data[units[4]][0], to=data[units[4]][1],
                                                increment=data[units[4]][2])
            self.view.quantity_entry['state'] = 'active'
        else:
            if sel_unit in ['ml', 'g']:
                value = int(float(current_value) * 1000)
                self.view.quantity_val.set(value)
                self.view.quantity_entry.config(from_=data[units[1]][0], to=data[units[1]][1],
                                                increment=data[units[1]][2])
            elif sel_unit in ['l', 'kg']:
                value = int(float(current_value) / 1000)
                self.view.quantity_val.set(value)
                self.view.quantity_entry.config(from_=data[units[2]][0], to=data[units[2]][1],
                                                increment=data[units[2]][2])
            elif sel_unit in ['count']:
                value = int(float(current_value))
                self.view.quantity_val.set(value)
                self.view.quantity_entry.config(from_=data[units[0]][0], to=data[units[0]][1],
                                                increment=data[units[0]][2])

    def destroy_top_btn(self):
        self.pop.destroy()
        self.pop_label.destroy()

    def delete_expired(self):
        for item in self.expired_products:
            self.db.delete_item_from_fridge(self.session, item)
        self.view.pop_expired.destroy()

    def send_mail(self, *arg):
        mail = 'empty'
        data = 'Shopping List:\n'
        if self.view.shopping:
            for i in self.view.shopping:
                new_i = i.name.replace("'", '')
                data += f'• {new_i} - {i.amount} {i.unit}\n'
        if arg:
            mail = arg

        qr_mail = segno.helpers.make_email(to=mail, subject='Shopping List', body=data)
        qr_mail.save('images/qr_mail.png', border=2, scale=7)
        imgo = PIL.Image.open("images/qr_mail.png")
        resized_image = imgo.resize((250, 250))
        global qr_to_send
        qr_to_send = ImageTk.PhotoImage(resized_image)
        self.pop = ttk.Button(self.view.left_box, image=qr_to_send, command=self.destroy_top_btn)
        self.pop_label = Label(self.view.left_box, text='Click to return', font=('bold', 14), foreground='tomato')
        self.pop.grid(column=0, row=0, sticky='news')
        self.pop_label.grid(column=0, row=2, sticky='news')

    def name_buttons(self):
        return [
            [self.view.first_user_label, self.view.first_user_entry, self.view.first_user_mail,
             self.view.first_user_mail_entry, self.view.update_first_user, self.view.delete_first_user, ],
            [self.view.sec_user_label, self.view.sec_user_entry, self.view.sec_user_mail,
             self.view.sec_user_mail_entry, self.view.update_sec_user, self.view.delete_sec_user, ],
            [self.view.third_user_label, self.view.third_user_entry, self.view.third_user_mail,
             self.view.third_user_mail_entry, self.view.update_third_user, self.view.delete_third_user, ],
            [self.view.four_user_label, self.view.four_user_entry, self.view.four_user_mail,
             self.view.four_user_mail_entry, self.view.update_four_user, self.view.delete_four_user, ],
            [self.view.fifth_user_label, self.view.fifth_user_entry, self.view.fifth_user_mail,
             self.view.fifth_user_mail_entry, self.view.update_fifth_user, self.view.delete_fifth_user, ],
            [self.view.sixth_user_label, self.view.sixth_user_entry, self.view.sixth_user_mail,
             self.view.sixth_user_mail_entry, self.view.update_sixth_user, self.view.delete_sixth_user, ],
            [self.view.sev_user_label, self.view.sev_user_entry, self.view.sev_user_mail,
             self.view.sev_user_mail_entry, self.view.update_sev_user, self.view.delete_sev_user, ],
        ]

    def add_new_user(self):
        name_btns = self.name_buttons()
        try:
            name_btns[self.view.clean_row - 3][0].grid(column=0, row=self.view.clean_row, pady=5, sticky='e')
            name_btns[self.view.clean_row - 3][1].grid(column=1, row=self.view.clean_row, padx=(0, 30))
            name_btns[self.view.clean_row - 3][2].grid(column=2, row=self.view.clean_row, padx=5)
            name_btns[self.view.clean_row - 3][3].grid(column=3, row=self.view.clean_row)
            name_btns[self.view.clean_row - 3][4].grid(column=4, row=self.view.clean_row, sticky='ew', padx=6)
            name_btns[self.view.clean_row - 3][5].grid(column=5, row=self.view.clean_row, sticky='ew')

            self.view.clean_row += 1
        except IndexError:
            self.view.add_user_btn.config(state='disabled')

    def delete_user(self, position):
        name_btns = self.name_buttons()
        all_users = self.db.get_all_users(self.session, self.fridge.id)

        name_btns[position][1].delete(0, END)
        name_btns[position][3].delete(0, END)
        for u in range(len(all_users)):
            if u == position:
                self.db.del_user_by_user_obj(self.session, all_users[u])
                name_btns[u][0].grid_forget()
                name_btns[u][1].grid_forget()
                name_btns[u][1].delete(0, END)
                name_btns[u][2].grid_forget()
                name_btns[u][3].grid_forget()
                name_btns[u][3].delete(0, END)
                name_btns[u][4].grid_forget()
                name_btns[u][5].grid_forget()

    def update_user(self, position):
        name_btns = self.name_buttons()
        all_users = self.db.get_all_users(self.session, self.fridge.id)
        for u in range(len(all_users)):
            if u == position:
                all_users[u].username = name_btns[u][1].get()
                all_users[u].mail = name_btns[u][3].get()
                self.session.commit()

    def check_if_ingredient_is_in_fridge(self, ingredient):
        for item in self.fridge.content:
            if item.name in ingredient.name or ingredient.name in item.name or \
                    ingredient.name in self.ingredients_not_to_buy:
                if float(item.amount) >= float(ingredient.amount):
                    new_amount = float(item.amount) - float(ingredient.amount)
                    self.db.set_data_for_item_from_name(self.session, item.name, item.name, int(new_amount), item.unit,
                                                        item.expiry, item.sub_category)
                    return item

    def check_if_ingredient_is_shopping_list(self, ingredient):
        if len(self.view.shopping) > 0:
            for item in self.view.shopping:
                if item.name in ingredient.name or ingredient.name in item.name:
                    return None
            return ingredient
        else:
            return ingredient

    def clear_fields(self):
        self.last_item = ''
        self.view.set_values()
        self.generate_choices()
        self.view.enable_buttons()
        self.view.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
        self.view.units_entry.set('')
        self.view.name_entry.focus()
        self.view.quantity_entry['state'] = 'disabled'

    def item_action_buttons(self, action):
        try:
            if action == 'clear':
                self.clear_fields()
            elif action == 'add':
                name_item, quantity, unit, expiry_date, sub_category = self.view.get_values()
                if name_item and unit and quantity:
                    data = self.check_if_item_in_fridge(name_item, expiry_date, quantity, unit, name_item)
                    new_name, n_expiry_date, n_quantity, n_unit, to_be_updated, last_checked_name = data
                    if not to_be_updated:
                        item = Item(name=new_name, amount=n_quantity, unit=n_unit, expiry=str(n_expiry_date),
                                    sub_category_id=self.db.get_sub_id(self.session, sub_category),
                                    fridge_id=self.fridge.id)
                        self.last_item = item
                        self.db.add_item_to_fridge(self.session, item)
                    else:
                        self.db.set_data_for_item_from_name(self.session, last_checked_name, new_name, n_quantity,
                                                            n_unit,
                                                            n_expiry_date, sub_category)
                self.clear_fields()
            elif action == 'delete':
                self.db.delete_item_from_fridge(self.session, self.last_item)
                self.clear_fields()
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
                        self.db.add_item_to_fridge(self.session, item)
                self.clear_fields()
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
                if new_quantity >= 1:
                    self.db.set_data_for_item_from_name(self.session,
                                                        old_name, old_name, int(new_quantity), old_unit, old_expiry,
                                                        old_sub)
                else:
                    self.db.delete_item_from_fridge(self.session, self.last_item)
                self.clear_fields()
        except AttributeError:
            pass

    def action_buttons(self, action):
        actions = {
            'add': self.view.add_frame,
            'cook': self.view.cook_frame,
            'random': self.view.cook_chosen_recipe_frame,
            'favourite': self.view.cook_chosen_recipe_frame,
            'choose': self.view.cook_chosen_recipe_frame,
            'other': self.view.add_item_frame,
            'fruits': self.view.add_item_frame,
            'vegetables': self.view.add_item_frame,
            'meat': self.view.add_item_frame,
            'fish': self.view.add_item_frame,
            'cereals': self.view.add_item_frame,
            'dairy': self.view.add_item_frame,
            'oils': self.view.add_item_frame,
            'legumes': self.view.add_item_frame,
        }
        try:
            self.generate_choices()
            sub_cat = action
            self.view.raise_above_all(actions[action], sub_cat)
        except KeyError:
            pass

    def remove_from_fridge_if_any(self):
        all_from_db = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
        self.db.delete_zero_amount_item_from_fridge(self.session, all_from_db)
        self.view.quit()

    def generate_choices(self, *args):
        if not args:
            var = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
            self.view.set_choices(var)
            self.view.choices = var


if __name__ == '__main__':
    food_manager = Controller()
    food_manager.main()
