from database_setup import *

session = get_database_session()




# Menu for UrbanBurger
restaurant1 = Restaurant(name="Urban Burger")

session.add(restaurant1)
session.commit()

menuItem2 = MenuItem(name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                     price="$7.50", course="Entree", restaurant=restaurant1)

session.add(menuItem2)
session.commit()


menuItem1 = MenuItem(name="French Fries", description="with garlic and parmesan",
                     price="$2.99", course="Appetizer", restaurant=restaurant1)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(name="Chicken Burger", description="Juicy grilled chicken patty with tomato mayo and lettuce",
                     price="$5.50", course="Entree", restaurant=restaurant1)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(name="Chocolate Cake", description="fresh baked and served with ice cream",
                     price="$3.99", course="Dessert", restaurant=restaurant1)

session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(name="Sirloin Burger", description="Made with grade A beef",
                     price="$7.99", course="Entree", restaurant=restaurant1)

session.add(menuItem4)
session.commit()