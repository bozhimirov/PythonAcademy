# Smart Fridge System App


This Smart Fridge System is designed to improve cooking and shopping planning for every user that use fridges in their home and wants to optimize food expenses and food waste. The Smart Fridge System can give easy access of all family members to many recipes to choose from and to optimize cooking by using most of the products in the fridge and to make less shopping expenses, by optimizing already bought food usage and eliminate food waste. Easily generated shopping list and easily sending it to other family members can optimize the time of shopping and expenses for cooking

Getting Started

Installation
1.	Download Python 3 
2.	Create folder for the project e.g. C:\Users\youruser\Desktop\SmartFridgeSystem
3.	Navigate to folder from your terminal and create virtual environment with following command:
          $ python -m venv myenv
4.	Activate environment by navigating to myenv/Scripts and execute following command
          $ activate.bat
5.	Navigate back to C:\Users\youruser\Desktop\SmartFridgeSystem and copy all files of the project
6.	Install requirements.txt with following command:
          $ pip install -r requirements.txt
7.	Create .env file with key and value in format: api_keys1 = 'apiKey={yourAPIkey}', get the API key from the SpoonacularAPI
8.	Run project with following command:
          $ python smart_fridge.py
	

1.	Main goals of the project
  1.1.	Add, remove, update, delete products in the fridge
  1.2.	Get recipes – by chosen products, random recipes from the API or from saved recipes in favorites
  1.3.	Choose from displayed recipes and if not interested get new recipes
  1.4.	If recipe is chosen to generate shopping list with products that are not in the fridge
  1.5.	The shopping list is displayed as text and as QR code with the shopping list as text, there is an option to send the shopping list to fridge’s users by email or to not registered person with email(where email have to be written)
  1.6.	There is an option that recipe to be displayed on the screen
2.	User requests
  •	To set name of the Smart Fridge
  •	To set users with usernames and emails connected to the Smart Fridge
  •	Fridge’s name have an option to be changed
  •	Users can be added, updated, removed from the Smart Fridge
  •	Users can add products by categories in the Smart Fridge
  •	Users can change and delete products from the Smart Fridge
  •	If there is an expired product there is a prompt to delete the product from the Smart Fridge and to remove it from the Smart Fridge
  •	If all of the amount of a given product is used for the selected recipe, the product to be automatically removed from the Smart Fridge
  •	Users have 3 options to choose a recipe – from chosen products, from save recipes in favorites, from randomly generated recipes
  •	When name of a recipe is selected user can see the ingredients needed, the instructions for preparing the meal and the image of the meal (if provided)
  •	When user want to cook a recipe a shopping list is generated and displayed
  •	User can write the shopping list on a list of paper, or get it in its phone by QR code, there is an option the shopping list to be send by mail to registered users or to other user not registered in the Smart Fridge again with QR code
  •	If the user want to cook another meal it can return to the previous page and choose another recipe and add it to the shopping list
  •	Products from the shopping list can be removed (not all products are in the fridge, some of them may be in the garden and waiting to be collected) and QR code is updated  
  •	User can display all products and recipe instructions and start cooking.



