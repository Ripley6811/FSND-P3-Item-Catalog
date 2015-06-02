
API
===

.. http:get:: /api/get/favorites

    :Authentication: Not required.
    :arg required her: A URI for me
    :arg optional me: A URI for me
    :Response: 
        Stringthing
        
        Example
        
        .. sourcecode:: json
        
            {
               "results" : [
                  {
                     "elevation" : 1608.637939453125,
                     "location" : {
                        "lat" : 39.73915360,
                        "lng" : -104.98470340
                     },
                     "resolution" : 4.771975994110107
                  }
               ],
               "status" : "OK"
            }
        