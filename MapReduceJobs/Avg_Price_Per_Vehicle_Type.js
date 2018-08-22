db.listings.mapReduce(
    function(){
        emit(this.type_of_veh, this.price);
    },
    function(key, values){
        sum_of_prices = 0;
        count = 0;
        for(var itr = 0; itr< values.length; itr++){
          if(values[itr]){
            sum_of_prices += values[itr]
            count += 1
          }
        }

        return sum_of_prices/count;
    },
    {
      out: "price_average_by_vehicle_type"
    }
  )