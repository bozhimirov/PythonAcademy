from datetime import date, timedelta
from PIL import ImageTk, Image

from tkinter import *
from tkinter import ttk


# import tkinter.font as font
#
# from dateutil.utils import today
#
# from models_new import Fridge, Item


class View(Tk):
    frame_stack = []

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # self.minsize(width=600, height=400)
        # self.maxsize(width=600, height=400)
        self.title('Food Management')

        self.geometry('600x400')
        self.root = ttk.Frame(self, name='root')
        self.root.grid(column=0, row=0, sticky='NSEW')
        # self.root.grid_propagate(0)
        # self.frame = Frame(self.root, width=600, height=400)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.quantity_val = StringVar()
        self.quantity_val.set('1')
        self.date_val = StringVar()
        self.date_val.set('1')
        self.unit_var = StringVar()
        self.unit_var.set('count')
        self._create_main_window()
        self.sub_cat = ''
        self._on_start()

    def main(self):
        self.mainloop()

    # photos = [PhotoImage(file="images/home.png"), PhotoImage(file="images/back.png")]
    def new_date(self):
        new_date = date.today() + timedelta(float(str(self.date_val.get())))
        var = self.date_view
        var.config(text=str(date.today() + timedelta(float(str(self.date_val.get())))))
        return new_date

        # return date.today() + timedelta(float(str(self.date_val.get())))

    def _create_main_window(self):
        # ---------------wellcome------------------
        self.welcome = ttk.Label(self.root, background='grey', anchor="center",
                                 text=f'Welcome,\n{self.controller.fridge.name}', font=('bold', 16), justify='center')
        self.welcome.grid(column=0, row=0, sticky='NSEW')
        self.welcome.columnconfigure(0, weight=1)
        self.welcome.rowconfigure(0, weight=1)
        # ---------------ask------------------
        self.ask_frame = self.make_aks_window(self.root)
        # # ---------------add_frame--------------------------------
        self.add_frame = self.make_add_window(self.root)
        # 00---------------------fruits_vegetables----------------------------------
        self.fruits_vegetables_frame = self.make_fruits_vegetables_window(self.root)
        # 10---------------------meat_fish----------------------------------
        self.meat_fish_frame = self.make_meat_fish_window(self.root)
        # 20---------------------cereals_cereal_products----------------------------------
        self.cereals_cereal_products_frame = self.make_cereals_cereal_products_window(self.root)

        # 01---------------------milk_milk_products----------------------------------
        self.milk_milk_products_frame = self.make_milk_milk_products_window(self.root)
        # 11---------------------oils_fats----------------------------------
        self.oils_fats_frame = self.make_oils_fats_window(self.root)

        # 21---------------------legumes_nuts_seeds----------------------------------
        self.legumes_nuts_seeds_frame = self.make_legumes_nuts_seeds_window(self.root)

        # 02---------------------sweets_spices----------------------------------
        self.sweets_spices_frame = self.make_sweets_spices_window(self.root)
        # 12---------------------condiments_beverages----------------------------------
        self.condiments_beverages_frame = self.make_condiments_beverages_window(self.root)

        # 22---------------------others----------------------------------
        self.condiments_beverages_frame = self.make_condiments_beverages_window(self.root)

        # ---------------------add_sub----------------------------------

        # ---------------------add_item----------------------------------
        self.add_item_frame = self.make_add_item_window(self.root)
        # ---------------------cook-------------------------------------
        self.cook_frame = self.make_cook_window(self.root)
        # ---------------------random-----------------------------------
        self.cook_random_recipe_frame = self.make_cook_random_window(self.root)
        # ---------------------choose_recipe-----------------------------------
        self.cook_chosen_recipe_frame = self.make_cook_chosen_window(self.root)

    def set_choices(self, value):
        self.items_list_box.delete(0, END)

        for c in value:
            self.items_list_box.insert(END, c)

    def selected_item_str(self, a):
        if a.widget.curselection() not in [(), '']:
            sel_item = self.items_list_box.get(a.widget.curselection())
            dates = []
            try:
                data = self.controller.search_item(sel_item)
                d_data = str(data.expiry)
                dates = d_data.split('-')
                # str_date = ', '.join(date)
                # print(str_date)
                # print(datetime.date(str_date))
                # print(datetime.date(date))
                # print(datetime.date(date.expiry))
            except AttributeError:
                pass
            if date(int(dates[0]), int(dates[1]), int(dates[2])) < date.today():
                self.update_btn['state'] = 'disabled'
                self.clear_btn['state'] = 'disabled'
                self.remove_btn['state'] = 'disabled'
                self.add_btn['state'] = 'disabled'
            self.set_values(data)
            old_date = data.expiry
            cur_date = date.today()

        self.update()

    def make_cook_random_window(self, parent):
        add_item_frame = Frame(parent, name="add items")
        add_item_frame.grid(column=0, row=0, sticky='news')
        try:
            nm = self.sub_cat
        except AttributeError:
            nm = ''
        self.make_menu_buttons(add_item_frame, 3, nm)
        self.choices = []
        choicevar = StringVar(self, value=self.choices, name='choicev')
        self.items_list_box = Listbox(add_item_frame, height=5, listvariable=choicevar, selectmode='browse')
        self.items_list_box.grid(column=0, row=1, sticky='news')
        self.items_list_box.bind('<<ListboxSelect>>', self.selected_item_str)
        s = ttk.Scrollbar(add_item_frame, orient=VERTICAL, command=self.items_list_box.yview)
        s.grid(column=0, row=1, rowspan=5, sticky='ens')
        self.items_list_box['yscrollcommand'] = s.set
        details_box = Frame(add_item_frame)
        details_box.grid(column=1, row=1, sticky='news')
        self.name_entry = ttk.Entry(details_box, width=26)
        self.name_entry.grid(column=1, row=0, sticky='e', pady=3)
        date_entry = ttk.Spinbox(details_box, from_=1, to=365, textvariable=self.date_val, command=self.new_date,
                                 width=5)

        date_entry.grid(column=1, row=1, sticky='e')
        self.date_view = ttk.Label(details_box, text='', width=24, background='white', borderwidth=1, relief="groove")
        self.date_view.grid(column=1, row=1, sticky='w', ipady=1)
        name_label = ttk.Label(details_box, text='Name:', width=20)
        name_label.grid(column=0, row=0, sticky='w')
        date_label = ttk.Label(details_box, text=f'Expiry date:')
        date_label.grid(column=0, row=1, sticky='w')
        q_box = Frame(details_box, width=20)
        q_box.grid(column=1, row=2, sticky='news')
        quantity_label = ttk.Label(details_box, text='Quantity:', width=20)
        quantity_label.grid(column=0, row=2, sticky='w')
        quantity_entry = ttk.Spinbox(q_box, from_=1, to=10000, textvariable=self.quantity_val, width=14)
        quantity_entry.grid(column=0, row=0, sticky='e', pady=3)

        units_entry = ttk.Combobox(q_box, textvariable=self.unit_var, width=6)
        units_entry['values'] = ('g', 'ml', 'count')
        units_entry.grid(column=1, row=0, sticky='e')
        buttons_box = Frame(add_item_frame)
        buttons_box.grid(column=3, row=1, sticky='news')
        self.add_btn = ttk.Button(buttons_box, text='add',
                                  command=lambda action='add': self.controller.item_action_buttons(action))
        self.add_btn.grid(column=0, row=1, sticky='news')
        self.remove_btn = ttk.Button(buttons_box, text='remove',
                                     command=lambda action='remove': self.controller.item_action_buttons(action))
        self.remove_btn.grid(column=0, row=3, sticky='news')
        self.del_btn = ttk.Button(buttons_box, text='delete',
                                  command=lambda action='delete': self.controller.item_action_buttons(action))
        self.del_btn.grid(column=0, row=4, sticky='news')
        self.clear_btn = ttk.Button(details_box, text='clear',
                                    command=lambda action='clear': self.controller.item_action_buttons(action))
        self.clear_btn.grid(column=0, columnspan=2, row=4, sticky='news')
        self.update_btn = ttk.Button(buttons_box, text='update',
                                     command=lambda action='update': self.controller.item_action_buttons(action))
        self.update_btn.grid(column=0, row=2, sticky='news')
        return add_item_frame

    def make_cook_chosen_window(self, parent):
        cook_chosen_frame = Frame(parent, name="cook chosen")
        cook_chosen_frame.grid(column=0, row=0, sticky='news')

        self.make_menu_buttons(cook_chosen_frame, 3)
        self.choices_products = []
        choicevar = StringVar(self, value=self.choices_products, name='choicev')
        self.items_list_box = Listbox(cook_chosen_frame, height=5, listvariable=choicevar, selectmode='browse')
        self.items_list_box.grid(column=0, row=1, sticky='news')
        self.items_list_box.bind('<<ListboxSelect>>', self.selected_item_str)
        s = ttk.Scrollbar(cook_chosen_frame, orient=VERTICAL, command=self.items_list_box.yview)
        s.grid(column=0, row=1, rowspan=5, sticky='ens')
        self.items_list_box['yscrollcommand'] = s.set
        details_box = Frame(cook_chosen_frame)
        details_box.grid(column=1, row=1, sticky='news')

        name_label = Listbox(details_box, width=20, height=5)?texttolistbox??
        name_label.grid(column=0, row=0, sticky='news')

        buttons_box = Frame(cook_chosen_frame)
        buttons_box.grid(column=3, row=1, sticky='news')
        self.remove_item_btn = ttk.Button(buttons_box, text='remove item',
                                     command=lambda action='remove_item': self.controller.item_action_buttons(action))
        self.remove_item_btn.grid(column=0, row=3, sticky='news')
        self.clear_list_btn = ttk.Button(details_box, text='clear list',
                                    command=lambda action='clear_list': self.controller.item_action_buttons(action))
        self.clear_list_btn.grid(column=0, columnspan=2, row=4, sticky='news')
        self.generate_btn = ttk.Button(buttons_box, text='generate',
                                     command=lambda action='generate': self.controller.item_action_buttons(action))
        self.generate_btn.grid(column=0, row=2, sticky='news')
        return cook_chosen_frame

    def make_cook_window(self, parent):
        cook_frame = Frame(parent, name='cook_frame')
        cook_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(cook_frame, 1)
        random_btn = Button(cook_frame, text='Random Recipe', font=('bold', 18), justify='center',
                            command=lambda action='random': self.controller.action_buttons(action))
        random_btn.grid(column=0, row=1, sticky='sewn')
        choose_btn = Button(cook_frame, text='Choose Recipe',
                            command=lambda action='choose': self.controller.action_buttons(action),
                            font=('bold', 18), justify='center')
        choose_btn.grid(column=0, row=2, sticky='sewn')
        return cook_frame

    def make_add_item_window(self, parent):
        add_item_frame = Frame(parent, name="add items")
        add_item_frame.grid(column=0, row=0, sticky='news')
        try:
            nm = self.sub_cat
        except AttributeError:
            nm = ''
        self.make_menu_buttons(add_item_frame, 3, nm)
        self.choices = []
        choicevar = StringVar(self, value=self.choices, name='choicev')
        self.items_list_box = Listbox(add_item_frame, height=5, listvariable=choicevar, selectmode='browse')
        self.items_list_box.grid(column=0, row=1, sticky='news')
        self.items_list_box.bind('<<ListboxSelect>>', self.selected_item_str)
        s = ttk.Scrollbar(add_item_frame, orient=VERTICAL, command=self.items_list_box.yview)
        s.grid(column=0, row=1, rowspan=5, sticky='ens')
        self.items_list_box['yscrollcommand'] = s.set
        details_box = Frame(add_item_frame)
        details_box.grid(column=1, row=1, sticky='news')
        self.name_entry = ttk.Entry(details_box, width=26)
        self.name_entry.grid(column=1, row=0, sticky='e', pady=3)
        date_entry = ttk.Spinbox(details_box, from_=1, to=365, textvariable=self.date_val, command=self.new_date,
                                 width=5)

        date_entry.grid(column=1, row=1, sticky='e')
        self.date_view = ttk.Label(details_box, text='', width=24, background='white', borderwidth=1, relief="groove")
        self.date_view.grid(column=1, row=1, sticky='w', ipady=1)
        name_label = ttk.Label(details_box, text='Name:', width=20)
        name_label.grid(column=0, row=0, sticky='w')
        date_label = ttk.Label(details_box, text=f'Expiry date:')
        date_label.grid(column=0, row=1, sticky='w')
        q_box = Frame(details_box, width=20)
        q_box.grid(column=1, row=2, sticky='news')
        quantity_label = ttk.Label(details_box, text='Quantity:', width=20)
        quantity_label.grid(column=0, row=2, sticky='w')
        quantity_entry = ttk.Spinbox(q_box, from_=1, to=10000, textvariable=self.quantity_val, width=14)
        quantity_entry.grid(column=0, row=0, sticky='e', pady=3)

        units_entry = ttk.Combobox(q_box, textvariable=self.unit_var, width=6)
        units_entry['values'] = ('g', 'ml', 'count')
        units_entry.grid(column=1, row=0, sticky='e')
        buttons_box = Frame(add_item_frame)
        buttons_box.grid(column=3, row=1, sticky='news')
        self.add_btn = ttk.Button(buttons_box, text='add',
                                  command=lambda action='add': self.controller.item_action_buttons(action))
        self.add_btn.grid(column=0, row=1, sticky='news')
        self.remove_btn = ttk.Button(buttons_box, text='remove',
                                     command=lambda action='remove': self.controller.item_action_buttons(action))
        self.remove_btn.grid(column=0, row=3, sticky='news')
        self.del_btn = ttk.Button(buttons_box, text='delete',
                                  command=lambda action='delete': self.controller.item_action_buttons(action))
        self.del_btn.grid(column=0, row=4, sticky='news')
        self.clear_btn = ttk.Button(details_box, text='clear',
                                    command=lambda action='clear': self.controller.item_action_buttons(action))
        self.clear_btn.grid(column=0, columnspan=2, row=4, sticky='news')
        self.update_btn = ttk.Button(buttons_box, text='update',
                                     command=lambda action='update': self.controller.item_action_buttons(action))
        self.update_btn.grid(column=0, row=2, sticky='news')
        return add_item_frame

    def make_condiments_beverages_window(self, parent):
        condiments_beverages_frame = Frame(parent, name='condiments/ beverages')
        condiments_beverages_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(condiments_beverages_frame, 1)
        condiments_btn = Button(condiments_beverages_frame, text='Condiments', font=('bold', 18), justify='center',
                                command=lambda action='condiments': self.controller.action_buttons(action))
        condiments_btn.grid(column=0, row=1, sticky='sewn')
        beverages_btn = Button(condiments_beverages_frame, text='Beverages',
                               command=lambda action='beverages': self.controller.action_buttons(action),
                               font=('bold', 18), justify='center')
        beverages_btn.grid(column=0, row=2, sticky='sewn')
        return condiments_beverages_frame

    def make_sweets_spices_window(self, parent):
        sweets_spices_frame = Frame(parent, name='sweets/ spices')
        sweets_spices_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(sweets_spices_frame, 1)
        sweets_btn = Button(sweets_spices_frame, text='Sweets', font=('bold', 18), justify='center',
                            command=lambda action='sweets': self.controller.action_buttons(action))
        sweets_btn.grid(column=0, row=1, sticky='sewn')
        spices_btn = Button(sweets_spices_frame, text='Spices',
                            command=lambda action='spices': self.controller.action_buttons(action),
                            font=('bold', 18), justify='center')
        spices_btn.grid(column=0, row=2, sticky='sewn')
        return sweets_spices_frame

    def make_legumes_nuts_seeds_window(self, parent):
        legumes_nuts_seeds_frame = Frame(parent, name='legumes/ nuts/ seeds')
        legumes_nuts_seeds_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(legumes_nuts_seeds_frame, 1)
        legumes_btn = Button(legumes_nuts_seeds_frame, text='Legumes', font=('bold', 18), justify='center',
                             command=lambda action='legumes': self.controller.action_buttons(action))
        legumes_btn.grid(column=0, row=1, sticky='sewn')
        nuts_btn = Button(legumes_nuts_seeds_frame, text='Nuts',
                          command=lambda action='nuts': self.controller.action_buttons(action),
                          font=('bold', 18), justify='center')
        nuts_btn.grid(column=0, row=2, sticky='sewn')
        seeds_btn = Button(legumes_nuts_seeds_frame, text='Seeds',
                           command=lambda action='seeds': self.controller.action_buttons(action),
                           font=('bold', 18), justify='center')
        seeds_btn.grid(column=0, row=3, sticky='sewn')
        return legumes_nuts_seeds_frame

    def make_oils_fats_window(self, parent):
        oils_fats_frame = Frame(parent, name='oils/ fats')
        oils_fats_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(oils_fats_frame, 1)
        oils_btn = Button(oils_fats_frame, text='Oils', font=('bold', 18), justify='center',
                          command=lambda action='oils': self.controller.action_buttons(action))
        oils_btn.grid(column=0, row=1, sticky='ewn')
        fats_btn = Button(oils_fats_frame, text='Fats',
                          command=lambda action='fats': self.controller.action_buttons(action),
                          font=('bold', 18), justify='center')
        fats_btn.grid(column=0, row=2, sticky='ews')
        return oils_fats_frame

    def make_milk_milk_products_window(self, parent):
        milk_milk_products_frame = Frame(parent, name='milk/ milk products')
        milk_milk_products_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(milk_milk_products_frame, 1)
        milk_btn = Button(milk_milk_products_frame, text='Milk', font=('bold', 18), justify='center',
                          command=lambda action='milk': self.controller.action_buttons(action))
        milk_btn.grid(column=0, row=1, sticky='ewn')
        milk_products_btn = Button(milk_milk_products_frame, text='Milk Products',
                                   command=lambda action='milk product': self.controller.action_buttons(action),
                                   font=('bold', 18), justify='center')
        milk_products_btn.grid(column=0, row=2, sticky='ews')
        return milk_milk_products_frame

    def make_cereals_cereal_products_window(self, parent):
        cereals_cereal_products_frame = Frame(parent, name='cereals/ cereal products')
        cereals_cereal_products_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(cereals_cereal_products_frame, 1)
        cereals_btn = Button(cereals_cereal_products_frame, text='Cereals', font=('bold', 18), justify='center',
                             command=lambda action='cereals': self.controller.action_buttons(action))
        cereals_btn.grid(column=0, row=1, sticky='ewn')
        cereal_products_btn = Button(cereals_cereal_products_frame, text='Cereal Products',
                                     command=lambda action='cereal product': self.controller.action_buttons(action),
                                     font=('bold', 18), justify='center')
        cereal_products_btn.grid(column=0, row=2, sticky='ews')
        return cereals_cereal_products_frame

    def make_meat_fish_window(self, parent):
        meat_fish_frame = Frame(parent, name='meat/ fish')
        meat_fish_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(meat_fish_frame, 1)
        meat_btn = Button(meat_fish_frame, text='Meat', font=('bold', 18), justify='center',
                          command=lambda action='meat': self.controller.action_buttons(action))
        meat_btn.grid(column=0, columnspan=3, row=1, sticky='news')
        fish_btn = Button(meat_fish_frame, text='Fish',
                          command=lambda action='fish': self.controller.action_buttons(action),
                          font=('bold', 18), justify='center')
        fish_btn.grid(column=0, columnspan=3, row=2, sticky='news')
        return meat_fish_frame

    def make_fruits_vegetables_window(self, parent):
        fruits_vegetables_frame = Frame(parent, name='fruits/ vegetables')
        fruits_vegetables_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(fruits_vegetables_frame, 1)
        fruits_btn = Button(fruits_vegetables_frame, text='Fruits', font=('bold', 18), justify='center',
                            command=lambda action='fruits': self.controller.action_buttons(action))
        fruits_btn.grid(column=0, columnspan=3, row=1, sticky='news')
        vegs_btn = Button(fruits_vegetables_frame, text='Vegetables',
                          command=lambda action='vegetables': self.controller.action_buttons(action),
                          font=('bold', 18), justify='center')
        vegs_btn.grid(column=0, columnspan=3, row=2, sticky='news')
        return fruits_vegetables_frame

    def make_add_window(self, parent):
        add_frame = ttk.Frame(parent, name='others')
        add_frame.grid(column=0, row=0, sticky='news')
        self.make_menu_buttons(add_frame, 3)
        # row0
        fruits_vegetables = Button(add_frame, text='Fruits/\nVegetables', font=('bold', 18), justify='center',
                                   command=lambda action='fruits_vegetables': self.controller.action_buttons(action))
        fruits_vegetables.grid(column=0, row=1, sticky='ew')
        meat_fish = Button(add_frame, text='Meat/\nFish', font=('bold', 18), justify='center',
                           command=lambda action='meat_fish': self.controller.action_buttons(action))
        meat_fish.grid(column=1, row=1, sticky='ew')
        cereals_cereal_products = Button(add_frame, text='Cereals/\nCereal products', font=('bold', 18),
                                         justify='center',
                                         command=lambda action='cereals_cereal_products':
                                         self.controller.action_buttons(action))
        cereals_cereal_products.grid(column=2, row=1, sticky='ew')
        # row1
        milk_milk_products = Button(add_frame, text='Milk/\nMilk Products', font=('bold', 18), justify='center',
                                    command=lambda action='milk_milk_products': self.controller.action_buttons(action))
        milk_milk_products.grid(column=0, row=2, sticky='news')
        oils_fats = Button(add_frame, text='Oils/\nFats', font=('bold', 18), justify='center',
                           command=lambda action='oils_fats': self.controller.action_buttons(action))
        oils_fats.grid(column=1, row=2, sticky='news')
        legumes_nuts_seeds = Button(add_frame, text='Legumes/\nNuts/\nSeeds', font=('bold', 18), justify='center',
                                    command=lambda action='legumes_nuts_seeds': self.controller.action_buttons(action))
        legumes_nuts_seeds.grid(column=2, row=2, sticky='news')
        # row2
        sweats_spices = Button(add_frame, text='Sweats/\nSpices', font=('bold', 18), justify='center',
                               command=lambda action='sweats_spices': self.controller.action_buttons(action))
        sweats_spices.grid(column=0, row=3, sticky='news')
        spices_condiments_beverages = Button(add_frame, text='Condiments/\nBeverages', font=('bold', 18),
                                             justify='center',
                                             command=lambda action='condiments_beverages':
                                             self.controller.action_buttons(action))
        spices_condiments_beverages.grid(column=1, row=3, sticky='news')
        others = Button(add_frame, text='Others', font=('bold', 18), justify='center',
                        command=lambda action='others': self.controller.action_buttons(action))
        others.grid(column=2, row=3, sticky='news')
        return add_frame

    def make_aks_window(self, parent):
        ask = ttk.Frame(parent, name='ask', )
        ask.grid(column=0, row=0, sticky='news')
        btn_add_item = Button(ask, text='add product', font=('bold', 18), justify='center',
                              command=lambda action='add': self.controller.action_buttons(action))
        btn_add_item.grid(column=0, row=0, sticky='news')
        btn_cook = Button(ask, text='cook', command=lambda action='cook': self.controller.action_buttons(action),
                          font=('bold', 18), justify='center')
        btn_cook.grid(column=1, row=0, sticky='news')
        return ask

    # def make_cook_window(self, parent):
    #     pass

    def make_menu_buttons(self, parent, colspan, *name_sub):
        home_menu = Button(parent, text='COOK',
                           command=lambda action='cook': self.controller.action_buttons(action))
        home_menu.grid(column=0, row=0, sticky='w')
        # or buttons ???
        self.middle_menu_label = ttk.Label(parent)
        self.middle_menu_label.grid(column=1, columnspan=colspan, row=0, sticky='news')

        # fruit_veg_menu = Button(parent, text='fruits\nvegetables',
        #                         command=lambda action='fruits_vegetables': self.controller.action_buttons(action))
        # fruit_veg_menu.grid(column=1, row=0, sticky='news')
        # meat_fish_menu = Button(parent, text='meat\nfish',
        #                         command=lambda action='meat_fish': self.controller.action_buttons(action))
        # meat_fish_menu.grid(column=2, row=0, sticky='news')
        # cer_cer_prod_menu = Button(parent, text='cereals\ncereal\nproducts',
        #                         command=lambda action='cereals_cereal_products': self.controller.action_buttons(action))
        # cer_cer_prod_menu.grid(column=3, row=0, sticky='news')
        # milk_milk_prod_menu = Button(parent, text='milk\nmilk\nproducts',
        #                         command=lambda action='milk_milk_products': self.controller.action_buttons(action))
        # milk_milk_prod_menu.grid(column=4, row=0, sticky='news')
        # oils_fats_menu = Button(parent, text='oils\nfats',
        #                         command=lambda action='oils_fats': self.controller.action_buttons(action))
        # oils_fats_menu.grid(column=5, row=0, sticky='news')
        # legumes_nuts_seeds_menu = Button(parent, text='legumes\nnuts\nseeds',
        #                         command=lambda action='legumes_nuts_seeds': self.controller.action_buttons(action))
        # legumes_nuts_seeds_menu.grid(column=6, row=0, sticky='news')
        # sweets_spices_menu = Button(parent, text='sweets\nspices',
        #                         command=lambda action='sweets_spices': self.controller.action_buttons(action))
        # sweets_spices_menu.grid(column=1, row=0, sticky='news')
        # condiments_beverages_menu = Button(parent, text='condiments\nbeverages',
        #                         command=lambda action='condiments_beverages': self.controller.action_buttons(action))
        # condiments_beverages_menu.grid(column=1, row=0, sticky='news')
        # others_menu = Button(parent, text='fruits\nvegetables',
        #                         command=lambda action='fruits_vegetables': self.controller.action_buttons(action))
        # others_menu.grid(column=1, row=0, sticky='news')
        back_menu = Button(parent, text='back',
                           command=self.fall_back_under)
        back_menu.grid(column=2, columnspan=colspan, row=0, sticky='e')

    def _on_start(self):
        self.raise_above_all(self.welcome, '')
        self.frame_stack.pop()
        # with delay 2s
        self.after(3000, lambda: self.raise_above_all(self.ask_frame, ''))
        # without delay for testing
        # self.after(0000, lambda: self.raise_above_all(self.ask))

    def raise_above_all(self, win1, action):
        win1.lift()
        if self.frame_stack and win1 != self.frame_stack[0]:
            if win1 != self.frame_stack[-1]:
                self.frame_stack.append(win1)
        else:
            self.frame_stack.clear()
            self.frame_stack.append(win1)
        self.sub_cat = action
        self.middle_menu_label.config(text=self.sub_cat)

    def fall_back_under(self):
        if len(self.frame_stack) > 1:
            self.frame_stack.pop()
            self.raise_above_all(self.frame_stack[-1], '')

    def set_values(self, *args):
        if not args:
            self.quantity_val.set('1')
            self.date_val.set('1')
            self.date_view['text'] = self.new_date()
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, '')
            self.unit_var.set('count')
        else:
            data = args[0]
            self.quantity_val.set(data.amount)
            self.date_view['text'] = data.expiry
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, data.name)
            self.unit_var.set(data.unit)

    def get_values(self):
        name_item = self.name_entry.get()
        quantity = self.quantity_val.get()
        unit = self.unit_var.get()
        expiry_date = self.new_date()
        sub_category = self.sub_cat
        main_category_raw = self.frame_stack[-2]
        main_category_raw_str = str(main_category_raw)
        main_category = main_category_raw_str.split('.')[-1]
        self.set_values()
        return name_item, quantity, unit, expiry_date, main_category, sub_category

    def enable_buttons(self):
        self.add_btn['state'] = 'normal'
        self.update_btn['state'] = 'normal'
        self.remove_btn['state'] = 'normal'
        self.clear_btn['state'] = 'normal'
        self.del_btn['state'] = 'normal'
