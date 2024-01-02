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
from db import DataBase
from view import View
from model import Item, Ingredient, Recipe, Base, Fridge, User, SubCategory


class Controller:
    """
    A Controller class that makes connection between users, views and db
    """

    def __init__(self) -> None:
        """
        constructor that initialize controller, loads dotenv and extract spoonacular api key, have predefined
        ingredients that are not needed to buy, creates the database, creates session, get fridge instance if any else
        makes fridge instance with predefined name, make list with expired products and fill it with expired products
        if any, remove items from fridge if amount is zero or very small, set wait variable, create instance of View,
        generate choices with all the items in the DB, set last_item variable, make blank list of recipes, set
        chosen_recipe variable
        """
        load_dotenv()
        env = os.getenv('api_keys1')
        self.api_keys = env
        self.ingredients_not_to_buy = ['water', 'salt', 'table salt', 'salt and pepper', 'flour', 'half and half',
                                       'pepper', 'sugar', 'salt & pepper', 'cooking oil']

        self.engine = create_engine('sqlite:///mydatabase.db')
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.db = DataBase
        self.fridge = self.session.get(Fridge, 1)
        if self.fridge is None:
            self.db.make_fridge(self.session, 'Change name')
            self.fridge = self.session.get(Fridge, 1)
        self.expired_products = []
        self.check_for_expired_products()
        self.remove_from_fridge_if_any()
        self.wait = False
        self.view = View(self)
        self.generate_choices()
        self.last_item = ''
        self.recipes = []
        self.chosen_recipe = Recipe
        self.recipes_for_cooking = []

    # -- remove digits from items name --
    @staticmethod
    def remove_digits(name: str) -> str:
        """
        remove digits from items' name if any, this is needed to take original ingredient's name for choosing recipe or
        updating amount of the ingredient after cooking
        """
        n_name = ''
        for ch in name:
            if not ch.isdigit():
                n_name += ch
        return n_name

    # -- make qr code from data --
    @staticmethod
    def make_qr_code(data: str) -> PhotoImage:
        """
        make qr code as PhotoImage from specific data and save it to a predefined destination, resizing the image to fit
        the view
        :param data: str string of information that have to be converted into qr code
        :returns PhotoImage of the qr code to be displayed on the view
        """
        img = segno.make(data)
        img.save('images/data.png', border=2, scale=7)
        imgo = PIL.Image.open("images/data.png")
        resized_image = imgo.resize((250, 250))
        qrr = ImageTk.PhotoImage(resized_image)
        return qrr

    # -- removes html tags from given string if any --
    @staticmethod
    def remove_li(instructions: str) -> str:
        """
        removes html tags from instructions, so they can be displayed correctly in the view
        :param instructions: str instructions taken from the API telling how a recipe can be prepared
        :returns string with instructions without html tags
        """
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

    # -- ingredients needed for the query --
    @staticmethod
    def chosen(list_chosen_ingr: list) -> str:
        """
        makes string of ingredients concatenated as needed to make the proper query for the APi
        :param list_chosen_ingr: list chosen ingredients as list
        :returns string of the ingredients as needed to make proper query to API
        """
        if len(list_chosen_ingr) == 0:
            pass
        to_str_chosen_ingr = ',+'.join(list_chosen_ingr)
        return to_str_chosen_ingr

    # -- choose shorter name of the ingredient --
    @staticmethod
    def check_name_len(name1: str, name2: str) -> str:
        """
        choose shorter name form the API of the ingredient
        :param name1: str one of the names taken from the API
        :param name2: str one of the names taken from the API, if any
        :returns string of the ingredients'  shorter name
        """
        len_name1 = name1.split(' ')
        if name2:
            len_name2 = name2.split(' ')
            if len_name1 > len_name2:
                return name2
        return name1

    # -- make amount and unit that user can work easily with --
    @staticmethod
    def make_unit(amount: str, unit: str) -> tuple:
        """
        take amount and unit and convert them to usable amount and unit
        :param amount: str amount of ingredient for specific unit as string as taken from the API
        :param unit: str unit of ingredient taken from the API
        :returns tuple of modified amount and unit
        """
        new_amount = amount
        new_unit = unit
        if unit in ['l', 'ltr']:
            new_amount = int(float(amount) * 1000)
            new_unit = 'ml'
        elif unit in ['kg', 'kgs']:
            new_amount = int(float(amount) * 1000)
            new_unit = 'g'
        elif unit in ['g']:
            new_amount = int(float(amount))
            new_unit = 'g'
        elif unit in ['ml']:
            new_amount = int(float(amount))
            new_unit = 'ml'
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
            new_amount = int(round(float(amount) * 3785, 0))
            new_unit = 'ml'
        elif unit in ['Lb', 'lb', 'pound', 'pounds']:
            new_amount = int(round(float(amount) * 454, 0))
            new_unit = 'g'
        elif unit in ['sticks', 'stick', 'pts']:
            new_amount = int(round(float(amount) * 250, 0))
            new_unit = 'g'
        elif unit in ['ounces', 'ounce', 'Ounces', 'Ounce']:
            new_amount = int(round(float(amount) * 28, 0))
            new_unit = 'g'
        elif unit in ['', 'serving', 'servings', 'extra large', 'large', 'large bunch', 'cloves', 'can', 'cans', 'bunch', 'small',
                      'medium', 'pinch', 'pkg', 'stalks', 'inch', 'inches', 'fillet', 'clove', 'small bunch', 'Bunch',
                      'loaf', 'large clove', 'leaf', 'Clove', 'head', 'pinches', 'large can', 'sprig', 'handfuls',
                      'strips', 'Cloves', 'strip', 'Handful', 'Handfuls', 'handful', 'medium size', 'pkt', 'sprigs']:
            new_amount = math.ceil(float(amount))
            new_unit = 'count'
        return str(new_amount), new_unit

    # -- main method of Controller class--
    def main(self) -> None:
        """
        calls the main method of the View class
        """
        self.view.main()

    # -- checks if there are expired products in the fridge --
    def check_for_expired_products(self) -> None:
        """
        check if there are expired items in the fridge and add them to expired_products variable
        """
        try:
            items = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
            for item in items:
                if item.expiry < str(date.today()):
                    self.expired_products.append(item)
        except AttributeError:
            pass

    # -- open view to set or change fridge's name adn to add, update or remove users --
    def initial_data(self) -> None:
        """
        open view to initial set fridge's name or to change it, also here user can add users to fridge, update their
         info or delete them, and after that takes user to welcome screen
        """
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

    # -- make shopping list string for generating qr code and fill ingredients in the view --
    def fill_shopping_list_content(self) -> None:
        """
        from shopping variable takes all ingredients and concatenate them in proper form for creating qr code, also
         display up to 16 ingredients in user's view in 2 columns
        """
        counter = 0
        for i in self.view.shopping:
            new_i = i.name.replace("'", '')
            txt = f'• {new_i} - {i.amount} {i.unit}\n'
            self.data += f'• {new_i} - {i.amount} {i.unit}\n'
            if counter >= 16:
                pass
            elif counter <= 7:
                Label(self.view.shopping_list_content, text=txt).grid(column=0, row=counter, sticky='wns')
                Button(self.view.shopping_list_content, text='x', command=lambda x=i: self.remove(x)).grid(
                    column=1, row=counter, sticky='ens', padx=6)
            else:
                Label(self.view.shopping_list_content2, text=txt).grid(column=0, row=counter - 8, sticky='wns')
                Button(self.view.shopping_list_content2, text='x', command=lambda x=i: self.remove(x)).grid(
                    column=1, row=counter - 8, sticky='ens', padx=6)
            counter += 1

    # -- clear shopping list view and shopping variable --
    def clear_shopping_list(self) -> None:
        """
        clear shopping variable from ingredients to buy and remove them from the shopping list view, also reset info for
        qr code
        """
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

    # -- removes pop up button --
    def destroy_top_btn(self) -> None:
        """
        destroy pop up button from view
        """
        self.pop.destroy()
        self.pop_label.destroy()

    # -- removes expired products from fridge --
    def delete_expired(self) -> None:
        """
        delete items in expired_products variable from DB and destroy pop up button with expired items from view
        """
        for item in self.expired_products:
            self.db.delete_item_from_fridge(self.session, item)
        self.view.pop_expired.destroy()

    # -- name of users' fields --
    def name_buttons(self) -> list:
        """
        only
        :returns list with names of all users' fields used for proper user manipulation
        """
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

    # -- add new user into DB and view --
    def add_new_user(self) -> None:
        """
        add new user in DB if there are filled fields of name and email and display it in the view in empty location
         field
        """
        name_btns = self.name_buttons()
        try:
            for i in range(0, 7):
                u_u = name_btns[i][1].get()
                u_m = name_btns[i][3].get()
                if not u_m and not u_u:
                    name_btns[i][0].grid(column=0, row=i + 3, pady=5, sticky='e')
                    name_btns[i][1].grid(column=1, row=i + 3, padx=(0, 30))
                    name_btns[i][2].grid(column=2, row=i + 3, padx=5)
                    name_btns[i][3].grid(column=3, row=i + 3)
                    name_btns[i][4].grid(column=4, row=i + 3, sticky='ew', padx=6)
                    name_btns[i][5].grid(column=5, row=i + 3, sticky='ew')
                    break

            self.view.clean_row += 1
        except IndexError:
            pass

    # -- clear all fields from add item in fridge view --
    def clear_fields(self) -> None:
        """
        clear all fields from add item in fridge view and resets connected variables
        """
        self.last_item = ''
        self.view.set_values()
        self.generate_choices()
        self.view.enable_buttons()
        self.view.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
        self.view.units_entry.set('')
        self.view.name_entry.focus()
        self.view.quantity_entry['state'] = 'disabled'

    # -- destroy recipe pop up view --
    def destroy_recipe_btn(self) -> None:
        """
        destroy recipe and ingredients pop up from view
        """
        self.pop2.destroy()
        self.pop3.destroy()
        self.tex_scroll2.destroy()
        self.tex_scroll3.destroy()

    # -- close the app --
    def close_app(self) -> None:
        """
        close the application
        """
        self.view.quit()

    # -- show recipe and ingredients as pop ups --
    def show_recipe(self) -> None:
        """
        display recipe and ingredients in the view as pop ups for easy cooking
        """
        result = self.remove_li(self.chosen_recipe.instructions)
        self.pop2 = Text(self.view.shopping_list_frame, wrap='word', font=('Times', 20, 'bold'))
        self.pop2.delete('1.0', END)
        self.pop2.insert(END, result)
        self.tex_scroll2 = Scrollbar(self.view.shopping_list_frame, orient=VERTICAL, )
        self.tex_scroll2.config(command=self.pop2.yview, )
        self.pop2["yscrollcommand"] = self.tex_scroll2.set
        self.tex_scroll2.grid(column=0, row=0, rowspan=6, sticky="nes", pady=(45, 0))
        self.pop2.grid(column=0, row=0, rowspan=6, sticky='news', padx=(5, 20), pady=(45, 0))
        result2 = [(x.name, x.amount, x.unit) for x in self.chosen_recipe.ingredients]
        self.pop3 = Text(self.view.right_box, wrap='word', font=('Times', 10, 'bold'), width=35, height=17)
        self.pop3.delete('1.0', END)
        for ingr in result2:
            self.pop3.insert(END, f'{ingr[0]} - {ingr[1]} {ingr[2]}\n')
        self.tex_scroll3 = Scrollbar(self.view.right_box, orient=VERTICAL, )
        self.tex_scroll3.config(command=self.pop3.yview, )
        self.pop3["yscrollcommand"] = self.tex_scroll3.set
        self.tex_scroll3.grid(column=0, columnspan=2, row=0, sticky="nes", pady=(0, 2))
        self.pop3.grid(column=0, columnspan=2, row=0, sticky='news', pady=(0, 2))

    # -- remove zero or small amount items from fridge --
    def remove_from_fridge_if_any(self) -> None:
        """
        takes all items from the DB and check if there are items with zero or small amounts and remove them from
        the fridge
        """
        try:
            all_from_db = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
            self.db.delete_zero_amount_item_from_fridge(self.session, all_from_db)
            self.view.choices = all_from_db
            self.view.set_choices(self.view.choices)
        except AttributeError:
            pass

    # -- get recipes from API by chosen ingredients --
    def get_recipes_by_items(self, number: int) -> list:
        """
        get recipes from API by chosen ingredients, then takes their ids and make another call to API to collect
         information for each recipe by their id and add it to a list
        :param number: int number of recipes to be taken
        :returns list of recipes object with information of each recipe
        """
        url = f'https://api.spoonacular.com/recipes/findByIngredients?' \
              f'{self.api_keys}&ingredients={self.chosen_ingredients}&number={number}&tags="main course"'
        response = requests.get(url)
        list_ids = []
        if response.status_code < 400:
            results = (response.json())
            for result in results:
                list_ids.append(result['id'])
            list_recipes = self.get_bulk_recipes_by_ids(list_ids)
            return list_recipes

    # -- get random recipes from the API--
    def get_random_recipes(self, number: int) -> list:
        """
        get random recipes from API, makes a recipe object with all of the recipe's
         information and add it to a list
        :param number: int number of recipes to be taken
        :returns list of recipes object with information of each recipe
        """
        random_url = f'https://api.spoonacular.com/recipes/random?number={number}&{self.api_keys}&tags="main course"'
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

    # -- set choices variable with all the items in the fridge --
    def generate_choices(self, *args) -> None:
        """
        set choices variable with all the items in the fridge so users can choose for items in fridge
        :param args: if args not changes choices variable
        """
        if not args:
            var = self.db.get_all_items_from_fridge(self.session, self.fridge.id)
            self.view.set_choices(var)
            self.view.choices = var

    # -- get recipe from given name --
    def get_recipe_by_name(self, name: str) -> Recipe:
        """
        get recipe by name from recipes from chosen products variable, if not there check if recipe is not in fridge's
         favourite recipes
        :param name: str title of recipe
        :returns searched recipe
        """
        if self.view.recipes_from_chosen_products:
            for fr in self.view.recipes_from_chosen_products:
                if fr.title == name:
                    return fr
        else:
            recipes = self.db.get_all_recipes(self.session, self.fridge.id)
            for r in recipes:
                if r.title == name:
                    name = r
            for fr in self.db.check_if_recipe_in_fridge(self.session, name):
                if fr.title == name:
                    return fr

    # -- get recipes' information by list of ids --
    def get_bulk_recipes_by_ids(self, ids: list) -> list:
        """
        from list of ids for each id make an API call and create recipe object with returned information
        :param ids: list ids of searched recipes in list
        :returns list with recipe objects for each of the searched id with full information
        """
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

    # -- create recipe object --
    def create_recipe(self, r_id: int, r_name: str, r_image: str, r_instructions: str, r_ingredients: list) -> Recipe:
        """
        create recipe object from given arguments and creates ingredients objects connected to that recipe
        :param r_id: int id of the recipe as given by the API
        :param r_name: str title of the recipe
        :param r_image: web link to recipe's image as string
        :param r_instructions: instructions for making recipe with removed tags
        :param r_ingredients: ingredient objects connected to the given recipe
        :return: Recipe object with all the information needed
        """
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

    # -- check if ingredient is among list of ingredients not to buy --
    def check_ingredients_not_to_buy(self, ingredient: Ingredient) -> Ingredient:
        """
        check if specific ingredient has to be bought
        :param ingredient: Ingredient object that has to be checked if it has to be bought
        :return: ingredient if it has to be bought or empty string if not to be bought
        """
        for i in self.ingredients_not_to_buy:
            if i in ingredient.name or ingredient.name in i:
                return ''
        return ingredient

    # -- open settings view --
    def open_settings(self, command: str) -> None:
        """
        set wait variable and open settings view
        :param command: str to be places into wait variable
        """
        self.wait = command
        time.sleep(5)
        self.view.initial = self.view.make_initial_window(self.view.root, command)

    # -- take pressed letter and placed it in a field or make action --
    def handle_letter(self, ltr: str) -> None:
        """
        take pressed letter or word and place it in filed for writing or call command if needed
        :param ltr: str letter or word to be used for writing or call command
        """
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

    # -- make keyboard in the view --
    def make_letter_buttons(self, parent: Frame) -> None:
        """
        make keyboard buttons in specific frame and every button returns letter of calls function
        :param parent: Frame where the keyboard to be displayed in
        """
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

    # -- search item from db --
    def search_item(self, name_item: str) -> list:
        """
        search specific item by name and returns it if presented
        :param name_item: str name of the food item that is searched
        :return: list with one item or empty list in order if the item is presented in the db
        """
        data = self.db.get_data_for_item_from_name(self.session, name_item)
        self.last_item = data
        return data

    # -- search item in DB by properties --
    def check_if_item_in_fridge(self, n: str, e: str, q: str, u: str, l_n: str) -> tuple:
        """
        check if item in fridge by all properties, if everything the same sum amounts, if no such item returned bool
         value is False, if such item but diff expiry or units, make new item with same name extended with number, else
          make new item
        :param n: str name of item to be checked
        :param e: str expiry date of item to be checked
        :param q: str amount of item to be checked
        :param u: str unit of item to be checked
        :param l_n: str last name chosen to be compared with
        :return: tuple with all the properties and a bool variable to_be_updated
        """
        last_checked_name = l_n
        old_item_from_entered_name = self.db.get_data_for_item_from_name(self.session, n)
        if not old_item_from_entered_name:
            to_be_updated = False
            return n, e, q, u, to_be_updated, last_checked_name
        else:
            old_item = old_item_from_entered_name[0]
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

    # -- actions performed by recipe buttons according to which button is presssed --
    def recipe_action_buttons(self, action: str) -> None:
        """
        group of buttons that make different things according to action keyword, according to action are displayed
         recipes from chosen products, random recipes or favourites recipes, user can add recipe to favourites, add
         ingredients to shopping list and get the shopping list
        :param action: str according to this action button perform different action
        """
        if action == 'generate':
            self.chosen_ingredients = self.chosen(self.view.chosen_products)
            self.view.recipes_from_chosen_products = self.get_recipes_by_items(10)
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
            self.view.random_recipes = self.get_random_recipes(10)
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
            self.remove_from_fridge_if_any()
            self.view.make_send_to_users_btns()
            self.data = 'Shopping List:\nno chosen products'
            if self.chosen_recipe:
                self.recipes_for_cooking.append(self.chosen_recipe)
                for ingred in self.chosen_recipe.ingredients:
                    if ingred:
                        item = self.check_if_ingredient_is_in_fridge(ingred)
                        ingr = self.check_if_ingredient_is_shopping_list(item)
                        if item and ingr:
                            self.view.shopping.append(item)
                self.data = 'Shopping List:\n'
                self.fill_shopping_list_content()
            self.remove_from_fridge_if_any()
            global qr
            qr = self.make_qr_code(self.data)
            self.view.label_qr.config(image=qr)
            self.view.raise_above_all(self.view.shopping_list_frame, '')
        elif action == 'get_shopping_list':

            self.view.make_send_to_users_btns()
            self.data = 'Shopping List:\nno chosen products'
            if self.view.shopping:
                self.data = 'Shopping List:\n'
                self.fill_shopping_list_content()
            qr = self.make_qr_code(self.data)
            self.view.label_qr.config(image=qr)
            self.view.raise_above_all(self.view.shopping_list_frame, '')

    # -- remove ingredient from shopping list view--
    def remove(self, *x: str) -> None:
        """
        remove ingredient from shopping list view and shopping variable and create updated qr code
        :param x: str ingredient to be removed
        """
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

    # -- changes values in unit spinbox --
    def change_spinbox(self, e) -> None:
        """
        changes values in unit spinbox according to if item is new, or got from fridge and has to be updated,
        if got from fridge, ml and l and g and kg are pairs possible for change, if the same item,
         else have to be made new item with different units
        :param e: Event to trigger changes
        """
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
                value = float(current_value) / 1000
                self.view.quantity_val.set(value)
                self.view.quantity_entry.config(from_=data[units[2]][0], to=data[units[2]][1],
                                                increment=data[units[2]][2])
            elif sel_unit in ['count']:
                value = int(float(current_value))
                self.view.quantity_val.set(value)
                self.view.quantity_entry.config(from_=data[units[0]][0], to=data[units[0]][1],
                                                increment=data[units[0]][2])

    # -- send email to user with shopping list --
    def send_mail(self, *arg) -> None:
        """
        generate qr code with shopping list and email if any to be sent to specific user
        get user email from DB or if list have to be sent to other user than email have to be manually written
        :param arg: str email of the user that have to receive shopping list
        """
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

    # -- delete user from view and DB --
    def delete_user(self, position: int) -> None:
        """
        delete user from specific position in the view and delete user from the DB
        :param position: int position of the user in view
        """
        name_btns = self.name_buttons()
        all_users = self.db.get_all_users(self.session, self.fridge.id)

        name_btns[position][0].grid_forget()
        name_btns[position][1].grid_forget()
        name_btns[position][1].delete(0, END)
        name_btns[position][2].grid_forget()
        name_btns[position][3].grid_forget()
        name_btns[position][3].delete(0, END)
        name_btns[position][4].grid_forget()
        name_btns[position][5].grid_forget()
        for u in range(len(all_users)):
            if u == position:
                self.db.del_user_by_user_obj(self.session, all_users[u])
        self.view.clean_row -= 1

    # -- update user in db and view --
    def update_user(self, position: int) -> None:
        """
        update user info in specific position in the view and update user's info in DB
        :param position: in t position of the user in the view
        """
        name_btns = self.name_buttons()
        all_users = self.db.get_all_users(self.session, self.fridge.id)
        for u in range(len(all_users)):
            if u == position:
                all_users[u].username = name_btns[u][1].get()
                all_users[u].mail = name_btns[u][3].get()
                self.session.commit()

    # -- check if ingredient is in fridge and can be used --
    def check_if_ingredient_is_in_fridge(self, ingredient: Ingredient) -> None:
        """
        check if ingredient is in fridge, if in fridge and amount is enough for the recipe, the food item in fridge is
        updated with removed amount needed for the recipe, else ingredient is not removed from shopping list
        :param ingredient: Ingredient needed to prepare the recipe
        """
        # modified_amount = False
        return_product = True
        ingredient_to_manipulate = Ingredient(name=ingredient.name, amount=ingredient.amount, unit=ingredient.unit,
                                              recipe_id=ingredient.recipe_id)
        for item in self.fridge.content:
            if ingredient_to_manipulate.amount == 0:
                return_product = False
                break
            if ingredient.name in self.ingredients_not_to_buy:
                return_product = False
                break
            if item.name in ingredient.name or ingredient.name in item.name:
                if float(item.amount) >= float(ingredient_to_manipulate.amount):
                    new_amount = float(item.amount) - float(ingredient_to_manipulate.amount)
                    self.db.set_data_for_item_from_name(self.session, item.name, item.name, int(new_amount), item.unit,
                                                        item.expiry, item.sub_category)

                    new_amount_ingr = 0
                    ingredient_to_manipulate.amount = new_amount_ingr
                    # modified_amount = True
                    return_product = False
                else:
                    new_amount_ingr = float(ingredient_to_manipulate.amount) - float(item.amount)
                    ingredient_to_manipulate.amount = new_amount_ingr
                    new_amount_item = 0
                    self.db.set_data_for_item_from_name(self.session, item.name, item.name, int(new_amount_item), item.unit,
                                                        item.expiry, item.sub_category)
                    # return item
        if return_product:
            return ingredient_to_manipulate


    # -- check if ingredient is in shopping variable --
    def check_if_ingredient_is_shopping_list(self, ingredient: Ingredient) -> Ingredient:
        """
        check if ingredient is in shopping list by checking substrings of any name to eliminate duplications
        :param ingredient: Ingredient to be checked if is in the shopping variable
        :return: ingredient if not in shopping variable, else return None
        """
        if len(self.view.shopping) > 0:
            for item in self.view.shopping:
                if ingredient:
                    if item.name in ingredient.name or ingredient.name in item.name:
                        if item.unit == ingredient.unit:
                            new_amount = int(float(item.amount) + float(ingredient.amount))
                            item.amount = new_amount
                        return None
            return ingredient
        else:
            return ingredient

    # -- check if item is expired --
    def check_if_item_in_expired(self, name: str) -> bool:
        """
        check if searched item is in the expired_products variable and return status
        :param name: str name of the food item to be checked if it is expired
        :return: bool value, True if not in expired_products list else False
        """
        if name in self.expired_products:
            return False
        return True

    # -- group of buttons that act different according to keyword --
    def item_action_buttons(self, action: str) -> None:
        """
        group of buttons in items view that act differently according to keyword, button can clear fields, can add item
        to DB, modify item, or delete item from view and DB, here is the action for removing specific amount of item
        taken for cooking
        :param action: str keyword that tells how a button from a group to act
        """
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
                self.db.delete_item_from_fridge(self.session, self.last_item[0])
                self.clear_fields()
            elif action == 'update':
                name_item, quantity, unit, expiry_date, sub_category = self.view.get_values()
                old_name = self.last_item[0].name
                old_expiry = self.last_item[0].expiry
                if str(old_expiry) == str(expiry_date) and old_name == name_item:
                    self.db.set_data_for_item_from_name(self.session, old_name, name_item, quantity, unit, expiry_date,
                                                        sub_category)
                else:
                    name_item, quantity, unit, expiry_date, to_be_updated, l_n = self.check_if_item_in_fridge(
                        name_item, quantity, unit, expiry_date, self.last_item[0].name)
                    if not to_be_updated:
                        item = Item(name=name_item, amount=quantity, unit=unit, expiry=str(expiry_date),
                                    sub_category_id=self.db.get_sub_id(self.session, sub_category),
                                    fridge_id=self.fridge.id)
                        self.db.add_item_to_fridge(self.session, item)
                self.clear_fields()
            elif action == 'remove':
                _, quantity, unit, _, _ = self.view.get_values()
                old_name = self.last_item[0].name
                old_quantity = self.last_item[0].amount
                old_unit = self.last_item[0].unit
                old_expiry = self.last_item[0].expiry
                old_sub = self.last_item[0].sub_category
                new_quantity = 1
                if unit == old_unit:
                    new_quantity = float(old_quantity) - float(quantity)
                if new_quantity >= 1:
                    self.db.set_data_for_item_from_name(self.session,
                                                        old_name, old_name, int(new_quantity), old_unit, old_expiry,
                                                        old_sub)
                else:
                    self.db.delete_item_from_fridge(self.session, self.last_item[0])
                self.clear_fields()
        except AttributeError:
            pass

    # -- buttons that change view frames --
    def action_buttons(self, action: str) -> None:
        """
        buttons that can change view frames according to action keyword
        :param action: str keyword needed for buttons to perform different action
        """
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


if __name__ == '__main__':
    food_manager = Controller()
    food_manager.main()
