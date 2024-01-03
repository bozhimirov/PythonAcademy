import datetime
import io
import string
from datetime import date
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from urllib.request import urlopen, Request
from model import Item


class View(Tk):
    """
    A View class that makes the interface of the application
    """
    # -- frame stack needed for going back --
    frame_stack = []
    # -- predefined fonts --
    FONT2 = ('Helvetica', 12, 'bold')
    FONT3 = "Times 12 bold"
    FONT4 = "Times 14 bold"
    FONT5 = "Times 16 bold"

    def __init__(self, controller):
        """
        constructor that initialize view, make instance of controller, set min and max size of the root frame, set title
        of the application, set geometry, make root frame and position it on screen, make and set quantity_val variable,
        make and set date_val variable, make and set unit_var variable, perform anonymous _create_main_window function,
        set initial sub category, perform on_start function
        :param controller: Controller instance that connect user with view and db
        """
        super().__init__()
        self.controller = controller
        self.minsize(width=800, height=500)
        self.maxsize(width=800, height=500)
        self.title('Smart Fridge System')
        self.geometry('800x500')
        self.root = ttk.Frame(self, name='root')
        self.root.grid(column=0, row=0, sticky='NSEW')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.quantity_val = StringVar()
        self.quantity_val.set('')
        self.date_val = StringVar()
        self.date_val.set('1')
        self.unit_var = StringVar()
        self.unit_var.set('')
        self._create_main_window()
        self.sub_cat = ''
        self.on_start()

    # -- main method of View class--
    def main(self) -> None:
        """
        calls the mainloop function of the View class
        """
        self.mainloop()

    # --create main view window--
    def _create_main_window(self) -> None:
        """
        private method that is used when initializing view class, cannot be used outside class, created main view
         window with every needed frames
        """
        # ---------------wellcome------------------
        self.welcome = ttk.Label(self.root, background='grey', anchor="center", justify='center',
                                 text=f'Welcome,\n{self.controller.fridge.name}', font="Times 40 bold")
        self.welcome.grid(column=0, row=0, sticky='NSEW')
        sv = ttk.Style()
        sv.configure('my.TButton', background='gray', borderwidth=0)
        pil_image = Image.open('images/settings1.png')
        global image_settings
        image_settings = ImageTk.PhotoImage(pil_image.resize((20, 20)))
        settings_btn = Button(self.welcome, width=15, image=image_settings, background='gray', borderwidth=0,
                              command=lambda action=True: self.controller.open_settings(action))
        settings_btn.grid(column=0, row=0, sticky='en')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.welcome.columnconfigure(0, weight=1)
        self.welcome.rowconfigure(0, weight=1)
        # ---------------ask------------------
        self.ask_frame = self.make_aks_window(self.root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.ask_frame.columnconfigure(0, weight=1)
        self.ask_frame.rowconfigure(0, weight=1)
        # # ---------------add_frame--------------------------------
        self.add_frame = self.make_add_window(self.root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.add_frame.columnconfigure(0, weight=1)
        self.add_frame.rowconfigure(0, weight=1)
        # ---------------------add_item----------------------------------
        self.add_item_frame = self.make_add_item_window(self.root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.add_item_frame.columnconfigure(0, weight=1)
        self.add_item_frame.rowconfigure(0, weight=1)
        # ---------------------cook-------------------------------------
        self.cook_frame = self.make_cook_window(self.root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.cook_frame.columnconfigure(0, weight=1)
        self.cook_frame.rowconfigure(0, weight=1)
        # ---------------------shopping list-----------------------------------
        self.shopping_list_frame = self.make_qr_shopping_list_window(self.root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.shopping_list_frame.columnconfigure(0, weight=1)
        self.shopping_list_frame.rowconfigure(0, weight=1)
        # ---------------------choose_recipe-----------------------------------
        self.cook_chosen_recipe_frame = self.make_cook_chosen_window(self.root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.cook_chosen_recipe_frame.columnconfigure(0, weight=1)
        self.cook_chosen_recipe_frame.rowconfigure(0, weight=1)
        # -------------------------initial-------------------------------
        self.initial = self.make_initial_window(self.root)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    # -- delete chosen products--
    def clear_chosen(self) -> None:
        """
        delete all chosen products from view, set chosen_products variable to empty list
        """
        self.chosen_products = []
        self.items_products_list_box.delete(0, END)

    # -- clear fields on recipe view --
    def clear_used_missed_instructions(self) -> None:
        """
        clear chosen products list view and variable, clear ingredients view, clear recipe description view
        """
        self.recipe_ingredients_text.delete(1.0, 'end')
        self.clear_chosen()
        self.recipe_description_text.delete(1.0, 'end')

    # -- check if recipe has image--
    def check_if_chosen_recipe_image(self) -> None:
        """
        check if chosen recipe has image and if it has it is displayed in recipe view
        """
        url = self.controller.chosen_recipe.image
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        image_bytes = urlopen(req).read()
        data_stream = io.BytesIO(image_bytes)
        pil_image = Image.open(data_stream)
        global tk_image
        tk_image = ImageTk.PhotoImage(pil_image.resize((204, 144)))
        self.lbl = ttk.Label(self.recipe_image_box, image=tk_image, )
        self.lbl.grid(column=0, row=0, sticky='news')

    # -- make send to buttons for all the users and one for other user--
    def make_send_to_users_btns(self) -> None:
        """
        make and display send shopping list buttons for all the users in DB with their username and one for another
         user not in DB
        """
        users = self.controller.db.get_all_users(self.controller.session, self.controller.fridge.id)
        counter = 0
        for user in users:
            btn = ttk.Button(self.send_btn_box, text=f'Send to\n{user.username}', style='my.TButton',
                             command=lambda mail=user.mail: self.controller.send_mail(mail))
            btn.grid(column=counter % 4, row=counter // 4, padx=2, pady=2, sticky='news')
            counter += 1
        self.mail_btn_r = ttk.Button(self.send_btn_box, text='Send to', style='my.TButton',
                                     command=lambda x='': self.controller.send_mail(x))
        self.mail_btn_r.grid(column=counter % 4, row=counter // 4, padx=2, pady=2, sticky='news')

    # -- display expired items for deleting--
    def display_expired_for_deleting(self) -> None:
        """
        check if items in expired_products list and display pop up button for prompt to delete them
        """
        ex_pr = [x.name for x in self.controller.expired_products]
        expired = '\n'.join(ex_pr)
        self.pop_expired = ttk.Button(self.ask, command=self.controller.delete_expired, style='my.TButton',
                                      text=f'EXPIRED ITEMS:\n\n\n\n{expired}\n\n\n\n\nClick to DELETE from list'
                                           f'\n\nremove from fridge')
        self.pop_expired.grid(column=0, columnspan=2, row=0, sticky='news', ipady=220)

    # -- perform different actions on start of the application--
    def on_start(self) -> None:
        """
        if user didn't set fridge's name displays settings view, else displays welcome screen for 5 sec then ask frame
        """
        if self.controller.fridge.name != 'Change name':
            self.raise_above_all(self.welcome, '')
            self.frame_stack.pop()
            # with delay 2s
            self.after(4000, lambda: self.raise_above_all(self.ask_frame, ''))
            # without delay for testing
            # self.after(0000, lambda: self.raise_above_all(self.ask_frame, ''))
        else:
            self.raise_above_all(self.initial, '')

    # -- displays last shown frame--
    def fall_back_under(self) -> None:
        """
        displays last shown frame if any and update frame stack
        """
        try:
            self.controller.destroy_recipe_btn()
        except AttributeError:
            pass
        self.controller.remove_from_fridge_if_any()
        if len(self.frame_stack) > 1:
            self.frame_stack.pop()
            self.raise_above_all(self.frame_stack[-1], '')

    # -- enable add item buttons group--
    def enable_buttons(self) -> None:
        """
        enable add, update, clear, delete buttons from add item group buttons
        """
        self.add_btn['state'] = 'normal'
        self.update_btn['state'] = 'normal'
        self.clear_btn['state'] = 'normal'
        self.del_btn['state'] = 'normal'

    # -- get all item values--
    def get_values(self) -> tuple:
        """
        get item values - name, amount, unit, expiry date, sub category
        :return: tuple with all values to make Item
        """
        name_item = self.name_entry.get()
        quantity = self.quantity_val.get()
        unit = self.unit_var.get()
        expiry_date = self.new_date()
        sub_category = self.sub_cat
        if unit and quantity:
            n_quantity, n_unit = self.controller.make_unit(quantity, unit)
            return name_item, n_quantity, n_unit, expiry_date, sub_category
        else:
            return name_item, quantity, unit, expiry_date, sub_category

    # -- get ingredients from chosen recipe and return them as string--
    def list_ingredients(self) -> str:
        """
        get all ingredients in chosen_recipe variable and returns all ingredients that have to be bought as string
        :return: str of all ingredients in chosen_recipe variable
        """
        list_ingredients = []
        for i in self.controller.chosen_recipe.ingredients:
            for z in self.controller.ingredients_not_to_buy:
                if i.name not in z or z not in i.name:
                    if i.name not in list_ingredients:
                        list_ingredients.append(i.name)
        res = ', '.join(list_ingredients)
        return res

    # -- make new expiry date for item--
    def new_date(self, *args) -> str:
        """
        make new date form current date and timedelta if not args or if args makes time delta from items expiry date
        :param args of date as string, optional
        :return: if args presented returns timedelta, else returns date as string
        """
        if not args:
            try:
                new_date = date.today() + datetime.timedelta(int(str(self.date_val.get()).split(' ')[0]))
                var = self.date_view
                var.config(text=str(date.today() + datetime.timedelta(float(str(self.date_val.get()).split(' ')[0]))))
                return str(new_date)
            except ValueError:
                pass

        else:
            c = args[0].split('-')
            c = date(int(c[0]), int(c[1]), int(c[2]))
            td = c - date.today()
            return str(td)

    # -- set chosen items into products list box view--
    def set_chosen(self, value: list) -> None:
        """
        display all chosen products in products list box view to cook for
        :param value: list of chosen products to be displayed
        """
        self.items_products_list_box.delete(0, END)
        for c in value:
            self.items_products_list_box.insert(END, c)

    # -- set choices for items into items list box view--
    def set_choices(self, value: list) -> None:
        """
        set chosen products from list into items list box view
        :param value: list of chosen products to be displayed into items list box view
        """
        self.items_list_box.delete(0, END)
        for c in value:
            self.items_list_box.insert(END, c)

    # -- set chosen recipes into recipe list box view--
    def set_recipes(self, value: list) -> None:
        """
        set chosen recipes from a list into recipe list box view
        :param value: list of chosen recipes to be displayed
        """
        self.recipe_list_box.delete(0, END)
        for c in value:
            self.recipe_list_box.insert(END, c)

    # -- select item from view--
    def selected_item_str(self, a: Event) -> None:
        """
        select item form fridge and return it into item fields to be removed or modified, if expired, add, update,
         clear buttons are disabled and only delete is active to prompts user to delete item and remove it from fridge,
         spinbox for units is modified according to item's unit
        :param a: Event that triggers selection of item
        """
        if a.widget.curselection() not in [(), '']:
            sel_item = self.items_list_box.get(a.widget.curselection())
            dates = []
            data = []
            try:
                data = self.controller.search_item(sel_item)
                d_data = str(data[0].expiry)
                dates = d_data.split('-')
            except AttributeError:
                pass
            try:
                if date(int(dates[0]), int(dates[1]), int(dates[2])) <= date.today():
                    self.update_btn['state'] = 'disabled'
                    self.clear_btn['state'] = 'disabled'
                    self.add_btn['state'] = 'disabled'
                else:
                    self.enable_buttons()
            except ValueError:
                pass
            if data[0].unit in ['g', 'kg']:
                self.units_entry['values'] = ('g', 'kg')
            elif data[0].unit in ['l', 'ml']:
                self.units_entry['values'] = ('ml', 'l')
            else:
                self.units_entry['values'] = 'count'
            self.set_values(data[0])

    # -- select items from fridge to cook with--
    def chosen_item_str(self, b: Event) -> None:
        """
        select item from fridge and add it to chosen products, remove from name any digits if any to prevent repetition
        of items selected
        :param b: Event that triggers selection of item
        """
        if b.widget.curselection() not in [(), '']:
            sel_item = self.items_list_box.get(b.widget.curselection())
            if sel_item not in [(), '']:
                data = self.controller.search_item(sel_item)
                no_digit_name = self.controller.remove_digits(data[0].name)
                if no_digit_name not in self.chosen_products:
                    self.chosen_products.append(no_digit_name)
                self.set_chosen(self.chosen_products)

    # -- select products form list with chosen products to cook for--
    def chosen_product_str(self, c: Event) -> None:
        """
        select product from list with chosen products to cook for and remove it from chosen_products list and update
        chosen products view
        :param c: Event that triggers selection of product
        """
        if c.widget.curselection() not in [(), '']:
            sel_item = self.items_products_list_box.get(c.widget.curselection())
            self.chosen_products.remove(sel_item)
            self.set_chosen(self.chosen_products)

    # -- find selected recipe from list--
    def recipe_find(self, d: Event) -> None:
        """
        select recipe name from list and then search that recipe in recipes from chosen products, random recipes or
        favourites according to list of recipes displayed, in view displays image, ingredients, instructions and name
        of the chosen recipe, if any
        :param d: Event that triggers selection of recipe
        """
        self.clear_used_missed_instructions()
        if d.widget.curselection() not in [(), '']:
            recipe_name = self.recipe_list_box.get(d.widget.curselection())
            try:
                recipe = []
                if self.recipes_from_chosen_products:
                    for i in self.recipes_from_chosen_products:
                        if recipe_name == i.title:
                            recipe = i
                            break

                    self.controller.chosen_recipe = recipe
                    list_ingredients = []
                    try:
                        for i in self.controller.chosen_recipe.ingredients:
                            ingr = self.controller.check_ingredients_not_to_buy(i)

                            if ingr and i.name not in list_ingredients:
                                list_ingredients.append(i.name)

                        res = ', '.join(list_ingredients)
                        self.recipe_ingredients_text.insert(1.0, res)
                        self.recipe_description_text.delete(1.0, 'end')
                        if self.controller.chosen_recipe.image:
                            self.check_if_chosen_recipe_image()

                        if self.controller.chosen_recipe.instructions:
                            result = self.controller.remove_li(self.controller.chosen_recipe.instructions)
                            new_result = self.controller.prepare_text_for_display(result, 80)
                            self.recipe_description_text.insert(1.0, new_result)
                        else:
                            self.recipe_description_text.insert(1.0, 'Sorry! No information available')
                    except AttributeError:
                        pass
                elif self.random_recipes:
                    for i in self.random_recipes:
                        if recipe_name == i.title:
                            recipe = i
                            break
                    self.controller.chosen_recipe = recipe
                    res = self.list_ingredients()
                    self.recipe_ingredients_text.insert(1.0, res)

                    if self.controller.chosen_recipe.image:
                        self.check_if_chosen_recipe_image()
                    self.recipe_description_text.delete(1.0, 'end')
                    if self.controller.chosen_recipe.instructions:
                        result = self.controller.remove_li(self.controller.chosen_recipe.instructions)
                        self.recipe_description_text.insert(1.0, result)
                    else:
                        self.recipe_description_text.insert(1.0, 'Sorry! No information available')

                else:
                    for i in self.controller.db.get_all_recipes(self.controller.session, self.controller.fridge.id):
                        if recipe_name == i.title:
                            recipe = i
                            break
                    self.controller.chosen_recipe = recipe
                    res = self.list_ingredients()
                    self.recipe_ingredients_text.insert(1.0, res)
                    self.recipe_description_text.delete(1.0, 'end')

                    if self.controller.chosen_recipe.image:
                        self.check_if_chosen_recipe_image()
                    if self.controller.chosen_recipe.instructions:
                        result = self.controller.remove_li(self.controller.chosen_recipe.instructions)
                        self.recipe_description_text.insert(1.0, result)
                    else:
                        self.recipe_description_text.insert(1.0, 'Sorry! No information available')
            except ValueError:
                self.chosen_products = []

    # -- make cook chosen frame window--
    def make_cook_chosen_window(self, parent: Frame) -> Frame:
        """
        make cook chosen view where user can select recipes and make shopping list and cook adn displays all items
         needed
        :param parent: Frame of the parent Frame
        :return: currently made Frame
        """
        cook_chosen_frame = Frame(parent, name="cook chosen")
        cook_chosen_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(cook_chosen_frame, 3)
        self.listbox_name = ttk.Label(cook_chosen_frame, text='R E C I P E S', font=self.FONT5,
                                      justify='center')
        details_box = Frame(cook_chosen_frame)
        details_box.grid(column=0, columnspan=3, row=2, sticky='news', padx=6)
        self.choices_products = []
        self.choicevar = StringVar(self, value=self.choices_products, name='choicev')
        self.items_list_box = Listbox(details_box, height=5, width=35, font=self.FONT3, listvariable=self.choicevar,
                                      selectmode='browse')
        self.items_list_box.grid(column=0, row=0, sticky='news', padx=(0, 6), pady=(0, 6))
        self.items_list_box.bind('<<ListboxSelect>>', self.chosen_item_str)
        s = ttk.Scrollbar(details_box, orient=VERTICAL, command=self.items_list_box.yview)
        s.grid(column=0, row=0, sticky='ens', pady=(0, 6), padx=(0, 6))
        self.items_list_box['yscrollcommand'] = s.set
        self.chosen_products = []
        self.choiceprodvar = StringVar(self, value=self.chosen_products, name='choicepv')
        self.details_inner = Frame(details_box)
        self.details_inner.grid(column=1, row=0, sticky='news', pady=(0, 6), padx=(0, 6))
        self.items_products_list_box = Listbox(self.details_inner, height=4, font=self.FONT3, selectmode='browse',
                                               listvariable=self.choiceprodvar, )
        self.items_products_list_box.grid(column=0, row=0, sticky='news')
        self.items_products_list_box.bind('<<ListboxSelect>>', self.chosen_product_str)
        s1 = ttk.Scrollbar(self.details_inner, orient=VERTICAL, command=self.items_products_list_box.yview)
        s1.grid(column=0, row=0, sticky='ens')
        self.items_products_list_box['yscrollcommand'] = s1.set
        buttons_box = Frame(details_box)
        buttons_box.grid(column=2, row=0, sticky='ne', padx=(0, 6))
        self.clear_list_btn = Button(self.details_inner, text='CLEAR', background='#EBF5FB',
                                     font=self.FONT2, command=self.clear_chosen)
        self.clear_list_btn.grid(column=0, row=2, sticky='news', ipady=1, pady=(3, 0))
        self.generate_btn = Button(buttons_box, text='GET RECIPES', background='#fcdada',
                                   font=self.FONT2,
                                   command=lambda action='generate': self.controller.recipe_action_buttons(action))
        self.generate_btn.grid(column=0, row=0, sticky='news', ipady=2, pady=(0, 6))
        self.random_btn = Button(buttons_box, text='RANDOM RECIPES', background='#d7e9cd',
                                 font=self.FONT2,
                                 command=lambda action='random': self.controller.recipe_action_buttons(action))
        self.random_btn.grid(column=0, row=1, sticky='news', ipady=2, pady=(0, 6))
        self.favourites_btn = Button(buttons_box, text='FAVOURITE RECIPES', background='#f6e7b6',
                                     font=self.FONT2,
                                     command=lambda action='favourites': self.controller.recipe_action_buttons(action))
        self.favourites_btn.grid(column=0, row=2, sticky='news', ipady=2, )
        self.get_shopping_list_btn = Button(buttons_box, text='GET\nSHOPPING\nLIST', background='#82E0AA',
                                            font=self.FONT2, command=lambda
                                            action='get_shopping_list': self.controller.recipe_action_buttons(action))
        self.get_shopping_list_btn.grid(column=1, row=0, rowspan=3, sticky='nws', padx=(5, 6), ipadx=19, ipady=14)
        recipes_box = Frame(cook_chosen_frame)
        recipes_box.grid(column=0, columnspan=3, row=3, sticky='news', padx=(0, 6))
        self.add_to_favourites_btn = Button(recipes_box, text='ADD TO\nFAVOURITES', background='#EBDEF0',
                                            font=self.FONT2, command=lambda
                                            action='add_favourites': self.controller.recipe_action_buttons(action))
        self.add_to_favourites_btn.grid(column=1, row=1, sticky='news', padx=(8, 0), ipadx=6, pady=(0, 6), )
        self.recipes_from_chosen_products = []
        self.random_recipes = []
        self.shopping_list_l = []
        choicerecipes = StringVar(self, value=self.recipes_from_chosen_products, name='choicer')
        self.recipe_list_box = Listbox(recipes_box, height=4, width=77, font=self.FONT3, listvariable=choicerecipes,
                                       selectmode='browse')
        self.recipe_list_box.grid(column=0, row=1, sticky='news', padx=6, pady=(0, 6), ipadx=3)
        self.recipe_list_box.bind('<<ListboxSelect>>', self.recipe_find)
        sr = ttk.Scrollbar(recipes_box, orient=VERTICAL, command=self.recipe_list_box.yview)
        sr.grid(column=0, row=1, sticky='ens', pady=(0, 6))
        self.recipe_list_box['yscrollcommand'] = sr.set
        self.recipe_ingredients_box = Frame(recipes_box)
        self.recipe_ingredients_box.grid(column=0, columnspan=4, row=3, sticky='news', padx=6, pady=(0, 6))
        self.recipe_ingredients_label = ttk.Label(self.recipe_ingredients_box, font=self.FONT3, text='INGREDIENTS:',
                                                  width=14)
        self.recipe_ingredients_label.grid(column=0, row=0, sticky='nw')
        self.recipe_ingredients_text = Text(self.recipe_ingredients_box, font=self.FONT3, width=61, height=2,
                                            wrap='word')
        self.recipe_ingredients_text.grid(column=1, row=0, sticky='news', padx=(2, 2), ipadx=7)
        sri = ttk.Scrollbar(self.recipe_ingredients_box, orient=VERTICAL, command=self.recipe_ingredients_text.yview)
        sri.grid(column=2, row=0, sticky='ens')
        self.recipe_ingredients_text['yscrollcommand'] = sri.set
        self.add_to_shopping_btn = Button(self.recipe_ingredients_box, text='ADD TO\nSHOPPING LIST',
                                          background='PeachPuff', font=self.FONT2,
                                          command=lambda action='shopping_list': self.controller.recipe_action_buttons(
                                              action))
        self.add_to_shopping_btn.grid(column=3, row=0, sticky='news', padx=(5, 0))
        recipe_details_box = Frame(recipes_box)
        recipe_details_box.grid(column=0, columnspan=4, row=4, sticky='news', padx=6, pady=(0, 6))
        self.recipe_image_box = Frame(recipe_details_box)
        self.recipe_image_box.grid(column=2, row=2, sticky='news')
        global img
        img = ImageTk.PhotoImage(Image.open('images/jb-no-photo__24078.jpg'))
        self.lbl = Label(self.recipe_image_box, image=img, width=204, height=144)
        self.lbl.grid(column=0, row=0, sticky='news', padx=(4, 0))
        self.recipe_description_text = Text(recipe_details_box, font=self.FONT3, width=65, height=9, wrap='word')
        self.recipe_description_text.grid(column=0, row=2, sticky='news', ipadx=22)
        srr = ttk.Scrollbar(recipe_details_box, orient=VERTICAL, command=self.recipe_description_text.yview)
        srr.grid(column=1, row=2, sticky='ens')
        self.recipe_description_text['yscrollcommand'] = srr.set
        return cook_chosen_frame

    # -- make qr code frame window--
    def make_qr_shopping_list_window(self, parent: Frame) -> Frame:
        """
         make qr shopping list view where user can get shopping list and send it and cook and displays all items needed
        :param parent: Frame of the parent Frame
        :return: currently made Frame
        """
        shopping_list_frame = Frame(parent, name="shopping list")
        shopping_list_frame.grid(column=0, row=0, sticky='news')
        shopping_list_frame.columnconfigure(0, weight=1)
        shopping_list_frame.rowconfigure(0, weight=1)
        try:
            nm = self.sub_cat
        except AttributeError:
            nm = ''
        self.make_menu_buttons(shopping_list_frame, 2, nm)
        self.left_box = Frame(shopping_list_frame)
        self.left_box.grid(column=0, columnspan=2, row=1, sticky='news', padx=(6, 0), pady=(0, 4))
        self.left_box.columnconfigure(0, weight=1)
        self.left_box.rowconfigure(0, minsize=350, weight=1)
        self.inner_left_box = Frame(self.left_box)
        self.inner_left_box.grid(column=0, row=0, sticky='news')
        self.right_box = Frame(shopping_list_frame)
        self.right_box.grid(column=2, row=1, sticky='news', padx=(0, 6), pady=(0, 6))
        self.right_box.columnconfigure(0, weight=1)
        self.right_box.rowconfigure(0, weight=1)
        global imge
        imge = PhotoImage(file='')
        self.label_qr = Label(self.right_box, image=imge)
        self.label_qr.grid(column=0, columnspan=2, row=0, sticky='s')
        self.clear_shopping_list_btn = Button(self.right_box, text='Close App', font="Helvetica 12 bold",
                                              background='#EC7063',
                                              command=self.controller.close_app)
        self.clear_shopping_list_btn.grid(column=0, row=1, ipadx=8, padx=(1, 2), pady=2, ipady=9, sticky='news')
        self.continue_shopping_btn = Button(self.right_box, text='Continue\nShopping', font="Helvetica 12 bold",
                                            background='#AED6F1',
                                            command=self.fall_back_under)
        self.continue_shopping_btn.grid(column=1, row=1, ipadx=12)
        self.remove_from_fridge_cook_btn = Button(self.right_box, text='COOK', font="Helvetica 12 bold",
                                                  background='#A9DFBF',
                                                  command=self.controller.show_recipe)
        self.remove_from_fridge_cook_btn.grid(column=0, columnspan=2, row=2, sticky='news', ipady=50)
        self.shopping_list_title = ttk.Label(self.left_box, text='SHOPPING LIST', font=self.FONT4,
                                             justify='center', )
        self.shopping_list_title.grid(column=0, columnspan=2, row=0, sticky='n', pady=(0, 8))
        self.shopping_list_lable = ttk.Label(self.inner_left_box, font=self.FONT4,
                                             justify='center')
        self.shopping_list_lable.grid(column=0, row=0, sticky='n', pady=(0, 8))
        self.shopping = []
        self.shopping_list_content = ttk.Label(self.inner_left_box, font=('bold', 14))
        self.shopping_list_content.grid(column=0, row=1, sticky='news', padx=(28, 18))
        self.shopping_list_content2 = ttk.Label(self.inner_left_box, font=('bold', 14))
        self.shopping_list_content2.grid(column=2, row=1, sticky='news', padx=18)
        self.send_btn_box = ttk.Label(self.left_box, justify='center')
        self.send_btn_box.grid(column=0, columnspan=2, row=2, sticky='n', padx=(0, 2))
        return shopping_list_frame

    # -- name of users' fields --
    def name_buttons(self) -> list:
        """
        only
        :returns list with names of all users' fields used for proper user manipulation
        """
        return [
            [self.first_user_label, self.first_user_entry, self.first_user_mail,
             self.first_user_mail_entry, self.update_first_user, self.delete_first_user, ],
            [self.sec_user_label, self.sec_user_entry, self.sec_user_mail,
             self.sec_user_mail_entry, self.update_sec_user, self.delete_sec_user, ],
            [self.third_user_label, self.third_user_entry, self.third_user_mail,
             self.third_user_mail_entry, self.update_third_user, self.delete_third_user, ],
            [self.four_user_label, self.four_user_entry, self.four_user_mail,
             self.four_user_mail_entry, self.update_four_user, self.delete_four_user, ],
            [self.fifth_user_label, self.fifth_user_entry, self.fifth_user_mail,
             self.fifth_user_mail_entry, self.update_fifth_user, self.delete_fifth_user, ],
            [self.sixth_user_label, self.sixth_user_entry, self.sixth_user_mail,
             self.sixth_user_mail_entry, self.update_sixth_user, self.delete_sixth_user, ],
            [self.sev_user_label, self.sev_user_entry, self.sev_user_mail,
             self.sev_user_mail_entry, self.update_sev_user, self.delete_sev_user, ],
        ]

    # -- make keyboard in the view --
    def make_letter_buttons(self, parent: Frame) -> None:
        """
        make keyboard buttons in specific frame and every button returns letter of calls function
        :param parent: Frame where the keyboard to be displayed in
        """
        inner_counter = 0
        for i in string.ascii_lowercase:
            Button(parent, text=i, command=lambda ltr=i: self.controller.handle_letter(ltr), width=3,
                   background='#EBF5FB', foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
                .grid(column=(inner_counter % 10), row=inner_counter // 10, sticky='news', padx=2, pady=2)
            inner_counter += 1
        Button(parent, text='DELETE', command=lambda ltr='del': self.controller.handle_letter(ltr),
               background='#F9EBEA', foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
            .grid(column=inner_counter % 10, row=inner_counter // 10, sticky='news', padx=2, pady=2,
                  columnspan=10 - ((inner_counter - 1) % 10))
        inner_counter += 1
        Button(parent, text='SPACE', command=lambda ltr='space': self.controller.handle_letter(ltr),
               background='#FEF9E7', foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
            .grid(column=0, row=(inner_counter // 10) + 1, columnspan=10, sticky='news', padx=2, pady=2)
        inner_counter += 1
        Button(parent, text='ENTER', command=lambda ltr='enter': self.controller.handle_letter(ltr),
               background='#E9F7EF', foreground='#212F3D', font=('Helvetica', 12, 'bold')) \
            .grid(column=0, row=(inner_counter // 10) + 2, columnspan=10, sticky='news', padx=2, pady=2, ipady=12)

    # -- make cook frame window --
    def make_cook_window(self, parent: Frame) -> Frame:
        """
         make sub cook frame where user to choose where to get recipes from, make recipe from items in fridge, get
         random recipe, or choose among favourite resipes, if any and displays all needed items
        :param parent: Frame of the parent Frame
        :return: currently made Frame
        """
        cook_frame = Frame(parent, name='cook_frame')
        cook_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(cook_frame, 1)
        image1 = Image.open('images/add-to-favorites-icon.png')
        image1 = image1.resize((50, 50))
        global img1
        img1 = ImageTk.PhotoImage(image1)
        image2 = Image.open('images/pngegg.png')
        image2 = image2.resize((130, 110))
        global img2
        img2 = ImageTk.PhotoImage(image2)
        image3 = Image.open('images/choose-icon.png')
        image3 = image3.resize((90, 70))
        global img3
        img3 = ImageTk.PhotoImage(image3)
        random_btn = Button(cook_frame, text='           F A V O U R I T E S', image=img1, compound=LEFT,
                            font=('Arial', 19, 'bold'), justify='center', height=135,
                            command=lambda action='favourite': self.controller.action_buttons(action),
                            background='#f6e7b6', foreground='#163c5e', )
        random_btn.grid(column=0, columnspan=3, row=1, sticky='new', ipady=5)
        random_btn = Button(cook_frame, text='R A N D O M            ', image=img2, compound=RIGHT,
                            font=('Arial', 19, 'bold'), justify='center', height=135,
                            command=lambda action='random': self.controller.action_buttons(action),
                            background='#d7e9cd', foreground='#163c5e', )
        random_btn.grid(column=0, columnspan=3, row=2, sticky='new', ipady=5)
        choose_btn = Button(cook_frame, text='              C H O O S E', image=img3, compound=LEFT, height=134,
                            background='#fcdada', foreground='#163c5e',
                            command=lambda action='choose': self.controller.action_buttons(action),
                            font=('Arial', 19, 'bold'), justify='center')
        choose_btn.grid(column=0, columnspan=3, row=3, sticky='new', ipady=5)
        return cook_frame

    # -- make add item to fridge view window--
    def make_add_item_window(self, parent: Frame) -> Frame:
        """
         make add item frame with where user can add, update, delete items and displays all items in fridge
        :param parent: Frame of the parent Frame
        :return: currently made Frame
        """
        add_item_frame = Frame(parent, name="add items")
        add_item_frame.grid(column=0, row=0, sticky='news')
        try:
            nm = self.sub_cat
        except AttributeError:
            nm = ''
        self.make_menu_buttons(add_item_frame, 3, nm)
        self.choices = []
        self.under_menu_frame = Frame(add_item_frame)
        self.under_menu_frame.grid(column=0, columnspan=3, row=1, sticky='news', padx=6)
        self.under_menu_frame.columnconfigure(0, weight=1)
        self.under_menu_frame.rowconfigure(0, weight=1)
        self.choicevar = StringVar(self, value=self.choices, name='choicev', )
        self.listbox_name = ttk.Label(self.under_menu_frame, text='PRODUCTS IN FRIDGE', font=self.FONT5,
                                      justify='center')
        self.listbox_name.grid(column=0, columnspan=4, row=1, sticky='n', pady=(0, 38))
        self.items_list_box = Listbox(self.under_menu_frame, height=15, listvariable=self.choicevar, selectmode='browse',
                                      width=37, font=self.FONT5)
        self.items_list_box.grid(column=0, row=2, sticky='e', padx=(4, 0), pady=(0, 12))
        self.items_list_box.bind('<<ListboxSelect>>', self.selected_item_str)
        s = ttk.Scrollbar(self.under_menu_frame, orient=VERTICAL, command=self.items_list_box.yview)
        s.grid(column=0, row=2, rowspan=1, sticky='ens', pady=(0, 12))
        self.items_list_box['yscrollcommand'] = s.set
        details_box = Frame(self.under_menu_frame)
        details_box.grid(column=1, row=2, sticky='new')
        self.name_entry = ttk.Entry(details_box, width=28, font=self.FONT3)
        self.name_entry.grid(column=1, row=0, sticky='w', pady=3)
        self.name_entry.focus()
        date_entry = ttk.Spinbox(details_box, from_=1, to=365, textvariable=self.date_val, command=self.new_date,
                                 width=5, font=self.FONT3)
        date_entry.grid(column=1, row=1, sticky='e', padx=(0, 7))
        self.date_view = ttk.Label(details_box, text='', width=26, background='white', borderwidth=1, relief="groove",
                                   font=self.FONT3)
        self.date_view.grid(column=1, row=1, sticky='w', ipady=1)
        name_label = ttk.Label(details_box, text='Name:', font=self.FONT3, width=12)
        name_label.grid(column=0, row=0, sticky='w')
        date_label = ttk.Label(details_box, text=f'Expiry date:', font=self.FONT3)
        date_label.grid(column=0, row=1, sticky='w')
        q_box = Frame(details_box)
        q_box.grid(column=1, row=2, sticky='news')
        quantity_label = ttk.Label(details_box, text='Quantity:', font=self.FONT3)
        quantity_label.grid(column=0, row=2, sticky='w')
        self.quantity_entry = ttk.Spinbox(q_box, from_=1, to=10000, increment=1, textvariable=self.quantity_val,
                                          width=17, font=self.FONT3, state='disabled')
        self.quantity_entry.grid(column=0, row=0, sticky='w', padx=(0, 1))
        self.units_entry = ttk.Combobox(q_box, textvariable=self.unit_var, width=6, font=self.FONT3, state='readonly')
        self.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
        self.units_entry.grid(column=1, row=0, sticky='e', padx=(2, 0))
        self.units_entry.bind("<<ComboboxSelected>>", self.controller.change_spinbox)
        self.clear_btn = Button(details_box, text='CLEAR', font="Helvetica 12 bold", background='PeachPuff',
                                command=lambda action='clear': self.controller.item_action_buttons(action))
        self.clear_btn.grid(column=2, row=0, rowspan=3, sticky='nws', ipadx=4, padx=(6, 6))
        buttons_box = Frame(details_box)
        buttons_box.grid(column=0, columnspan=4, row=4, sticky='n')
        self.add_btn = Button(buttons_box, text='ADD', font="Helvetica 12 bold", width=12, background='lightgreen',
                              command=lambda action='add': self.controller.item_action_buttons(action))
        self.add_btn.grid(column=0, row=0, sticky='we', padx=(0, 6), pady=(6, 6), ipadx=2, ipady=6)
        self.update_btn = Button(buttons_box, text='UPDATE', width=12, font="Helvetica 12 bold", background='lightblue',
                                 command=lambda action='update': self.controller.item_action_buttons(action))
        self.update_btn.grid(column=1, row=0, sticky='we', padx=(0, 6), ipadx=2, ipady=6)
        self.del_btn = Button(buttons_box, text='DELETE', width=12, font="Helvetica 12 bold", background='tomato',
                              command=lambda action='delete': self.controller.item_action_buttons(action))
        self.del_btn.grid(column=2, row=0, sticky='we', padx=(0, 6), ipadx=2, ipady=6)
        self.keyboard_box = Frame(details_box)
        self.keyboard_box.grid(column=0, columnspan=4, row=5, sticky='n')
        self.alpha_box = Frame(self.keyboard_box)
        self.make_letter_buttons(self.alpha_box)
        self.alpha_box.grid(column=0, row=0, sticky='s', pady=(32, 0))
        return add_item_frame

    # -- make add item by sub category--
    def make_add_window(self, parent: Frame) -> Frame:
        """
         make buttons for all the sub categories so user can place new item in correct sub category
        :param parent: Frame of the parent Frame
        :return: currently made Frame
        """
        add_frame = ttk.Frame(parent, name='others')
        add_frame.grid(column=0, row=0, sticky='news')
        global fruit
        fruit = PhotoImage(file='images/png products/fruits1.png')
        global vegetable
        vegetable = PhotoImage(file='images/png products/vegetables1.png')
        global cereals
        cereals = PhotoImage(file='images/png products/cereals1.png')
        global meats
        meats = PhotoImage(file='images/png products/meat1.png')
        global fishs
        fishs = PhotoImage(file='images/png products/fish1.png')
        global dairy
        dairy = PhotoImage(file='images/png products/dairy1.png')
        global oils
        oils = PhotoImage(file='images/png products/oils1.png')
        global legumes
        legumes = PhotoImage(file='images/png products/legumes1.png')
        global other
        other = PhotoImage(file='images/png products/other1.png')
        self.make_menu_buttons(add_frame, 3)
        # row1
        fruits = Button(add_frame, text='Fruits', font=('bold', 18), justify='center', image=fruit, background='white',
                        command=lambda action='fruits': self.controller.action_buttons(action))
        fruits.grid(column=0, row=1, sticky='news')
        vegetables = Button(add_frame, text='Vegetables', font=('bold', 18), justify='center', image=vegetable,
                            background='white',
                            command=lambda action='vegetables': self.controller.action_buttons(action))
        vegetables.grid(column=1, row=1, sticky='news')
        cereals_cereal_products = Button(add_frame, text='Cereals', font=('bold', 18), justify='center', image=cereals,
                                         background='white',
                                         command=lambda action='cereals': self.controller.action_buttons(action))
        cereals_cereal_products.grid(column=2, row=1, sticky='news')
        # row2
        meat = Button(add_frame, text='Meat', font=('bold', 18), justify='center', image=meats, background='white',
                      command=lambda action='meat': self.controller.action_buttons(action))
        meat.grid(column=0, row=2, sticky='news')
        fish = Button(add_frame, text='Fish', font=('bold', 18), justify='center', image=fishs, background='white',
                      command=lambda action='fish': self.controller.action_buttons(action))
        fish.grid(column=1, row=2, sticky='news')
        milk_milk_products_dairy = Button(add_frame, text='Dairy', font=('bold', 18), justify='center', image=dairy,
                                          background='white',
                                          command=lambda action='dairy': self.controller.action_buttons(action))
        milk_milk_products_dairy.grid(column=2, row=2, sticky='news')
        # row3
        oils_fats = Button(add_frame, text='Oils', font=('bold', 18), justify='center', image=oils, background='white',
                           command=lambda action='oils': self.controller.action_buttons(action))
        oils_fats.grid(column=0, row=3, sticky='news')
        legumes_nuts_seeds = Button(add_frame, text='Legumes', font=('bold', 18), justify='center', image=legumes,
                                    background='white',
                                    command=lambda action='legumes': self.controller.action_buttons(action))
        legumes_nuts_seeds.grid(column=1, row=3, sticky='news', ipadx=6)
        others = Button(add_frame, text='Others', font=('bold', 18), justify='center', image=other, background='white',
                        command=lambda action='other': self.controller.action_buttons(action))
        others.grid(column=2, row=3, sticky='news', ipadx=6)
        return add_frame

    # -- make ask view window--
    def make_aks_window(self, parent: Frame) -> Frame:
        """
        make ask view frame when user is asked to choose if to add item or to cook and display these 2 buttons
        :param parent: Frame of the parent Frame
        :return: currently made Frame
        """
        global bag
        bag = PhotoImage(file='images/bag1.png')
        global chef
        chef = PhotoImage(file='images/hat1.png')
        self.ask = ttk.Frame(parent, name='ask', )
        self.ask.grid(column=0, row=0, sticky='news')
        self.ask.columnconfigure(0, weight=1)
        self.ask.rowconfigure(0, weight=1)
        btn_add_item = Button(self.ask, text='ADD PRODUCT\n', image=bag, compound=BOTTOM, font="Times 20  bold",
                              foreground='black',
                              justify='center', command=lambda action='add': self.controller.action_buttons(action))
        btn_add_item.grid(column=0, row=0, sticky='news', )
        btn_add_item.columnconfigure(0, weight=1)
        btn_add_item.rowconfigure(0, weight=1)
        btn_cook = Button(self.ask, text='COOK RECIPE\n', image=chef, compound=BOTTOM, foreground='black',
                          command=lambda action='cook': self.controller.action_buttons(action),
                          font="Times 20  bold", justify='center', background='lightgray')
        btn_cook.grid(column=1, row=0, sticky='news', ipadx=50)
        btn_cook.columnconfigure(0, weight=1)
        btn_cook.rowconfigure(0, weight=1)
        if self.controller.expired_products:
            self.display_expired_for_deleting()
        return self.ask

    # -- make initial view frame to set fridge name and users--
    def make_initial_window(self, parent: Frame, *args) -> Frame:
        """
        make initial settings frame where user can set or change fridge's name and add, update or remove users and all
         needed items to display
        :param parent: Frame of the parent Frame
        :return: currently made Frame
        """
        s = ttk.Style()
        s.configure('my.TButton', font=self.FONT2, justify="center", background='orange')
        if self.controller.fridge.name == 'Change name' or args:
            self.initial_frame = ttk.Frame(self.root)
            self.initial_frame.columnconfigure(0, weight=1)
            self.initial_frame.rowconfigure(0, weight=1)
            self.initial_frame.grid(column=0, row=0, sticky='news')
            self.initial_label = ttk.Label(self.initial_frame, text='Set Fridge', font='Times 30 bold italic',
                                           justify='center')
            self.initial_label.grid(column=0, columnspan=6, row=0, sticky='n', pady=20)
            self.initial_box = ttk.Frame(self.initial_frame, padding=(5, 5))
            self.initial_box.grid(column=0, columnspan=6, row=1, sticky='n')
            self.init_name_label = ttk.Label(self.initial_box, text="Fridge's name: ", font=('Helvetica', 14))
            self.init_name_label.grid(column=0, row=1, sticky='n', pady=12)
            self.init_name_entry = ttk.Entry(self.initial_box, font=('Helvetica', 14))
            self.init_name_entry.grid(column=1, columnspan=3, row=1, sticky='ew')
            self.first_user_label, self.first_user_entry, self.first_user_mail, self.first_user_mail_entry, \
            self.update_first_user, self.delete_first_user = self.make_user_field_lines(0)
            self.first_user_label.grid(column=0, row=3, pady=5, sticky='en')
            self.first_user_entry.grid(column=1, row=3, padx=(0, 30))
            self.first_user_mail.grid(column=2, row=3, padx=5)
            self.first_user_mail_entry.grid(column=3, row=3)
            self.update_first_user.grid(column=4, row=3, sticky='ew', padx=6)
            self.delete_first_user.grid(column=5, row=3, sticky='ew')
            self.clean_row = 4
            self.sec_user_label, self.sec_user_entry, self.sec_user_mail, self.sec_user_mail_entry, \
            self.update_sec_user, self.delete_sec_user = self.make_user_field_lines(1)
            self.third_user_label, self.third_user_entry, self.third_user_mail, self.third_user_mail_entry, \
            self.update_third_user, self.delete_third_user = self.make_user_field_lines(2)
            self.four_user_label, self.four_user_entry, self.four_user_mail, self.four_user_mail_entry, \
            self.update_four_user, self.delete_four_user = self.make_user_field_lines(3)
            self.fifth_user_label, self.fifth_user_entry, self.fifth_user_mail, self.fifth_user_mail_entry, \
            self.update_fifth_user, self.delete_fifth_user = self.make_user_field_lines(4)
            self.sixth_user_label, self.sixth_user_entry, self.sixth_user_mail, self.sixth_user_mail_entry, \
            self.update_sixth_user, self.delete_sixth_user = self.make_user_field_lines(5)
            self.sev_user_label, self.sev_user_entry, self.sev_user_mail, self.sev_user_mail_entry, \
            self.update_sev_user, self.delete_sev_user = self.make_user_field_lines(6)
            self.add_user_btn = Button(self.initial_box, text='ADD USER', command=self.controller.add_new_user,
                                       foreground='white',
                                       font=self.FONT2, background='orange')
            self.add_user_btn.grid(column=4, columnspan=2, row=11, sticky='es', pady=10)
            self.submit_fridge_data_btn = Button(self.initial_box, text='SUBMIT', foreground='white',
                                                 background='green',
                                                 command=self.controller.initial_data, font=self.FONT2)
            self.submit_fridge_data_btn.grid(column=1, columnspan=3, row=10, pady=10, sticky='ews')
            self.invalid_name_message = ttk.Label(self.initial_box, text='Invalid name', justify='center',
                                                  foreground='red', font=('Times', 14, 'bold'))
            self.invalid_username_message = ttk.Label(self.initial_box, text='No username', justify='center',
                                                      foreground='red', font=('Times', 14, 'bold'))
            self.invalid_mail_message = ttk.Label(self.initial_box, text='Invalid email', justify='center',
                                                  foreground='red', font=('Times', 14, 'bold'))
            if args:
                name = self.controller.fridge.name[:-9]
                self.init_name_entry.insert(0, name)
                all_users = self.controller.db.get_all_users(self.controller.session, self.controller.fridge.id)
                user_fields = [(self.first_user_entry, self.first_user_mail_entry),
                               (self.sec_user_entry, self.sec_user_mail_entry),
                               (self.third_user_entry, self.third_user_mail_entry),
                               (self.four_user_entry, self.four_user_mail_entry),
                               (self.fifth_user_entry, self.fifth_user_mail_entry),
                               (self.sixth_user_entry, self.sixth_user_mail_entry),
                               (self.sev_user_entry, self.sev_user_mail_entry),
                               ]
                inr_countr = 0
                for u in all_users:
                    if inr_countr > 0:
                        self.controller.add_new_user()
                    user_fields[inr_countr][0].insert(0, u.username)
                    user_fields[inr_countr][1].insert(0, u.mail)
                    inr_countr += 1
            else:
                return self.initial_frame
        else:
            return self.on_start()

    # -- make user fields and buttons--
    def make_user_field_lines(self, index: int) -> tuple:
        """
        make all needed fields to be displayed for user to be created and buttons to be updated or deleted
        :param index: int place of the user in the view
        :return: tuple with all of users fields that have to be displayed
        """
        return ttk.Label(self.initial_box, text='User: ', font=('Helvetica', 12)), \
               ttk.Entry(self.initial_box, font=('Helvetica', 12)), \
               ttk.Label(self.initial_box, text="e-mail: ", font=('Helvetica', 12)), \
               ttk.Entry(self.initial_box, font=('Helvetica', 12)), \
               Button(self.initial_box, text='UPDATE', foreground='white', background='blue',
                      font=('Helvetica', 8, 'bold'), command=lambda x=index: self.controller.update_user(x)), \
               Button(self.initial_box, text='DELETE', foreground='white', background='red',
                      font=('Helvetica', 8, 'bold'), command=lambda x=index: self.controller.delete_user(x))

    # -- make menu buttons--
    def make_menu_buttons(self, parent: Frame, colspan: int, *name_sub) -> None:
        """
        make menu buttons for most of the frames and place them, buttons are: add, cook, back
        :param parent: parent Frame where current frame to be places
        :param colspan: int number of columns to span
        :param name_sub: optional, name of frame
        """
        home_sub_menu = Frame(parent)
        home_sub_menu.grid(column=0, row=0, sticky='wn')
        home_sub_menu.columnconfigure(0, weight=1)
        home_sub_menu.rowconfigure(0, weight=1)
        home_menu = Button(home_sub_menu, text='COOK', font="Times 16 italic bold", background='PowderBlue',
                           command=lambda action='cook': self.controller.action_buttons(action))
        home_menu.grid(column=0, row=0, sticky='news')
        add_menu = Button(home_sub_menu, text='ADD', font="Times 16 italic bold", background='lightgreen',
                          command=lambda action='add': self.controller.action_buttons(action))
        add_menu.grid(column=1, row=0, sticky='news')
        self.middle_menu_label = ttk.Label(parent)
        back_menu = Button(parent, text='BACK', foreground='#fffeed',
                           command=self.fall_back_under, background='#163c5e', font="Times 16 italic bold")
        back_menu.grid(column=2, row=0, sticky='ne')

    # -- raise specific frame above others--
    def raise_above_all(self, win1: Frame, action: str) -> None:
        """
        display selected frame or if setting button pressed display settings window,
        clear specific fields according to keyword and if selected frame is the initial frame clears frame stack
        :param win1: view frame to be lifted
        :param action: keyword that can modify lifting behaviour
        """
        if win1 == self.ask_frame and self.controller.wait:
            try:
                self.make_initial_window(self.root, True)
                self.initial.lift()
            except AttributeError:
                pass
        else:
            win1.lift()
            if self.frame_stack and win1 != self.frame_stack[0]:
                if win1 != self.frame_stack[-1]:
                    self.frame_stack.append(win1)
            else:
                self.frame_stack.clear()
                self.frame_stack.append(win1)
            self.sub_cat = action
            if self.sub_cat == 'random':
                self.clear_used_missed_instructions()
                self.random_recipes = self.controller.get_random_recipes(10)
                self.set_recipes(self.random_recipes)
            elif self.sub_cat == 'favourite':
                self.clear_used_missed_instructions()
                self.controller.chosen_recipe = None
                self.set_recipes(self.controller.db.get_all_recipes(self.controller.session, self.controller.fridge.id))
                self.random_recipes = []
            elif self.sub_cat == 'choose':
                self.clear_used_missed_instructions()
                self.controller.chosen_recipe = None
                self.set_recipes([])
                self.random_recipes = []
            self.middle_menu_label.config(text=self.sub_cat)
            self.set_values()

    # -- set values for add item frame--
    def set_values(self, *args: Item) -> None:
        """
        set initial values in item fields if args not presented, else set values from args in item fields
        :param args: list if args set values of item with values of the selected item placed in args
        """
        if not args:
            self.quantity_val.set('')
            self.date_val.set('1')
            self.date_view['text'] = self.new_date()
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, '')
            self.units_entry['values'] = ('count', 'ml', 'l', 'g', 'kg')
            self.unit_var.set('')
            self.units_entry.set('')
            self.name_entry.focus()
            self.quantity_entry['state'] = 'disabled'
        else:
            data = args[0]
            self.unit_var.set(data.unit)
            self.controller.change_spinbox(data)
            self.quantity_val.set(data.amount)
            self.date_view['text'] = data.expiry
            self.date_val.set(self.new_date(data.expiry))
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, data.name)
