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
                  "description": "a Vietnamese noodle soup.",
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
    
Get list of users
-------------------
.. http:get:: /api/users

    Get a list of users from the database.

    :Authentication: Not required.
    :response: JSON
    :example:
        
        .. sourcecode:: json
        
            {
              "status": "ok",
              "users": [
                {
                  "email": "b.white@gmail.com",
                  "id": 1,
                  "name": "Barry White",
                  "picture": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlHU4qMDG0Ln9LfgRJre4CYAt-KvHr3GQD3EJQqNd93n-2mpvIWA"
                },
                {
                  "email": "b.white@yahoo.com",
                  "id": 2,
                  "name": "Betty White",
                  "picture": "http://borderlessnewsandviews.com/wp-content/uploads/2012/05/Betty-white.jpg"
                },
                {
                  "email": "e.white@aol.com",
                  "id": 3,
                  "name": "E. B. White",
                  "picture": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcS1Z80NlvDZ-sBs2i9hCviJf3-eXH0kCi5s3K6Zk366Q_ZJr1Rl"
                }
              ]
            }
        
Get list of favorites
---------------------
.. http:get:: /api/favorites

    Gets a random list of a user's favorited items.    
    Pass a *user_id* as a parameter or default to the currently logged in user.
    Returns an error if neither is found. The default *limit* is three.
    

    :Authentication: Optional.
    :arg optional user_id: ID of user.
    :arg optional limit: Max number of items to return.
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
        
        
Get list of VM packages
------------------------------------
.. http:get:: /api/environment

    Gets a listing of installed packages and version numbers from server.
    
    :Authentication: Not required.
    :Response:  JSON
    :example:
        
        .. sourcecode:: json
        
            {
              "installed_packages": [
                "alabaster == 0.7.4",
                "apt-xapian-index == 0.45",
                "argparse == 1.2.1",
                "babel == 1.3",
                "bleach == 1.4.1",
                "blinker == 1.3",
                "chardet == 2.0.1",
                "cheetah == 2.4.4",
                "cloud-init == 0.7.5",
                "..."
              ]
            }
                
