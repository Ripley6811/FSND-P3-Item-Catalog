API Reference
=============

Get list of restaurants
-----------------------
.. http:get:: /api/restaurants

    Get a list of restaurant records in the database.

    :Authentication: Not required.
    :response: JSON
    :example:
        
        .. sourcecode:: json
        
            {
              "restaurants": [
                {
                  "created_by": 1,
                  "id": 1,
                  "name": "Urban Burger",
                  "note": "",
                  "phone": "555-1234"
                },
              ],
              "status": "ok"
            }
    
Get restaurant menu
-------------------
.. http:get:: /api/menu

    Get a list of restaurant menu items from the database. Enter either a restaurant name or it's database ID.

    :Authentication: Not required.
    :arg optional restaurant_id: Database ID for a restaurant.
    :arg optional restaurant: Name of a restaurant in the database.
    :response: JSON
    :example:
        
        .. sourcecode:: json
        
            {
              "menu": [
                {
                  "bad_count": 0,
                  "course": "Entree",
                  "created_by": 1,
                  "description": "a Vietnamese noodle soup consisting of broth, linguine-shaped rice noodles called banh pho, a few herbs, and meat.",
                  "favorite_count": 0,
                  "good_count": 0,
                  "id": 16,
                  "name": "Pho",
                  "price": "8.99",
                  "restaurant_id": 3,
                  "restaurant_name": "Panda Garden"
                },
              ],
              "status": "ok"
            }
        
Get list of favorites
---------------------
.. http:get:: /api/favorites

    Gets a random list of three of a user's favorited items.    
    Pass a *user_id* as a parameter or default to the currently logged in user.
    Returns an error if neither is found.
    

    :Authentication: Optional.
    :arg optional user_id: ID of user.
    :Response:  JSON
    :example:
        
        .. sourcecode:: json
        
            {
              "items": [
                {
                  "bad_count": 0,
                  "course": "Dessert",
                  "created_by": 2,
                  "description": "fresh baked and served with ice cream",
                  "favorite_count": 2,
                  "good_count": 0,
                  "id": 4,
                  "name": "Chocolate Cake",
                  "price": "3.99",
                  "restaurant_id": 1,
                  "restaurant_name": "Urban Burger"
                },
                {
                  "bad_count": 1,
                  "course": "Beverage",
                  "created_by": 2,
                  "description": "16oz of refreshing goodness",
                  "favorite_count": 1,
                  "good_count": 0,
                  "id": 6,
                  "name": "Root Beer",
                  "price": "1.99",
                  "restaurant_id": 1,
                  "restaurant_name": "Urban Burger"
                },
                {
                  "bad_count": 0,
                  "course": "Appetizer",
                  "created_by": 1,
                  "description": "Maguro, Sake, Hamachi, Unagi, Uni, TORO!",
                  "favorite_count": 1,
                  "good_count": 0,
                  "id": 35,
                  "name": "Nigiri Sampler",
                  "price": "6.75",
                  "restaurant_id": 6,
                  "restaurant_name": "Andala's"
                }
              ]
            }
        