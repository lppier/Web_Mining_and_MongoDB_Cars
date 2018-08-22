db.listings.mapReduce(
    function(){emit(this.type_of_veh, this.price);},
    function(key, values){return Array.sum(values)/values.length;},
    {
      out: "price_average_by_vehicle_type"
    }
  )