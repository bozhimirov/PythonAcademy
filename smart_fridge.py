
from controller import Controller
from initDB import CreateDB

if __name__ == '__main__':
	db = CreateDB()
	food_manager = Controller()
	food_manager.main()
