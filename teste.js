 data = function()
    {
      var today = new Date();
      var date = today.getDate() + '/'+(today.getMonth()+1)+ '/'+today.getFullYear();
      var time = today.getHours() + ":" + today.getMinutes();
      var dateTime = date+' '+time;
      console.log(dateTime)
      return dateTime
      
    };

    data();