# import json
#
# import requests
#
#
# url = 'https://api.spoonacular.com/recipes/findByIngredients?apiKey=4bb99921a1fa470bb800293b23863d29&ingredients=milk,+potato,+eggs,+chicken, +onion&number=10'
# # url = 'https://api.spoonacular.com/recipes/716429/information?apiKey=4bb99921a1fa470bb800293b23863d29&includeNutrition=true'
# # url2 = f'https://api.spoonacular.com/recipes/{n_id}/information'
# # url = 'https://api.spoonacular.com/recipes/complexSearch?apiKey=4bb99921a1fa470bb800293b23863d29'
# # url = 'https://api.spoonacular.com/recipes/complexSearch?type=main course&number=100'
# # url = "https://api.spoonacular.com/recipes/findByIngredients?ingredients=tomato,+potato,+onion,+garlic"
#
#
# # querystring = {"query": "pork", "equipment": "pan", "includeIngredients": "tomato,cheese", "excludeIngredients": "eggs",
# #                "type": "main course", "instructionsRequired": "true", "fillIngredients": "false",
# #                "addRecipeInformation": "false", "titleMatch": "Crock Pot", "maxReadyTime": "20", "ignorePantry": "true",
# #                "sort": "calories", "sortDirection": "asc", "minCarbs": "10", "maxCarbs": "100", "minProtein": "10",
# #                "maxProtein": "100", "minCalories": "50", "maxCalories": "800", "minFat": "10", "maxFat": "100",
# #                "minAlcohol": "0", "maxAlcohol": "100", "minCaffeine": "0", "maxCaffeine": "100", "minCopper": "0",
# #                "maxCopper": "100", "minCalcium": "0", "maxCalcium": "100", "minCholine": "0", "maxCholine": "100",
# #                "minCholesterol": "0", "maxCholesterol": "100", "minFluoride": "0", "maxFluoride": "100",
# #                "minSaturatedFat": "0", "maxSaturatedFat": "100", "minVitaminA": "0", "maxVitaminA": "100",
# #                "minVitaminC": "0", "maxVitaminC": "100", "minVitaminD": "0", "maxVitaminD": "100", "minVitaminE": "0",
# #                "maxVitaminE": "100", "minVitaminK": "0", "maxVitaminK": "100", "minVitaminB1": "0",
# #                "maxVitaminB1": "100", "minVitaminB2": "0", "maxVitaminB2": "100", "minVitaminB5": "0",
# #                "maxVitaminB5": "100", "minVitaminB3": "0", "maxVitaminB3": "100", "minVitaminB6": "0",
# #                "maxVitaminB6": "100", "minVitaminB12": "0", "maxVitaminB12": "100", "minFiber": "0", "maxFiber": "100",
# #                "minFolate": "0", "maxFolate": "100", "minFolicAcid": "0", "maxFolicAcid": "100", "minIodine": "0",
# #                "maxIodine": "100", "minIron": "0", "maxIron": "100", "minMagnesium": "0", "maxMagnesium": "100",
# #                "minManganese": "0", "maxManganese": "100", "minPhosphorus": "0", "maxPhosphorus": "100",
# #                "minPotassium": "0", "maxPotassium": "100", "minSelenium": "0", "maxSelenium": "100", "minSodium": "0",
# #                "maxSodium": "100", "minSugar": "0", "maxSugar": "100", "minZinc": "0", "maxZinc": "100", "offset": "0",
# #                "number": "10", "limitLicense": "false", "ranking": "2"}
#
# headers = {
#     "X-RapidAPI-Key": "4bb99921a1fa470bb800293b23863d29",
#     "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
# }
#
# response = requests.get(url)
# # response = requests.get(url, headers=headers, params=querystring)
#
# results = (response.json())
# # print(results[0])
# for result in results:
#     # print(result)
#     print(result['id'])
#     print(result['title'])
#     print(result['image'])
#     print('used count')
#     print(result['usedIngredientCount'])
#     print('missed count')
#     print(result['missedIngredientCount'])
#     print('used')
#     used = result['usedIngredients']
#     for i in used:
#         print(i['name'], end=' ')
#         print(i['amount'], end=' ')
#         print(i['unit'])
#     print('missed')
#     missed = result['missedIngredients']
#     for i in missed:
#         print(i['name'], end=' ')
#         print(i['amount'], end=' ')
#         print(i['unit'])
#
# with open('temp_result.json', 'w') as f:
#     new_result = json.dumps(results)
#     f.write(new_result)
#
# # with open('temp_result.json', 'r') as r:
# #     lines = r.readlines()
# #     for line in lines:
# #         n_line = (line[1:-2])
# #         print(n_line)
# #         n_id = line['id']
# #         url2 = f'https://api.spoonacular.com/recipes/{n_id}/information'
# #
# #         # n_title = line['title']
# #         response2 = requests.get(url2, headers=headers)
# #         results2 = (response2.json())
# #         print(results2)
# #         # print(results2)
#
# from datetime import date
#
# a = date.today()
# print(a)
# b = str(a)
# c = b.split('-')
# print(c)
# print(b)
# c = date(int(c[0]), int(c[1]), int(c[2]))
# print(c)


#
#
# from tkinter import *
#
# root = Tk()
# img = PhotoImage(file='images/data.png')
# label = Label(root, image=img)
# label.grid(column=0, row=0)
# root.mainloop()


class Ocean:

    def __init__(self, sea_creature_name, sea_creature_age):
        self.name = sea_creature_name
        self.age = sea_creature_age

    def __str__(self):
        return f'The creature type is {self.name} and the age is {self.age}'

    def __repr__(self):
        return f'Ocean(\'{self.name}\', {self.age})'


c = Ocean('Jellyfish', 5)

print(str(c))
print(repr(c))
print(c)