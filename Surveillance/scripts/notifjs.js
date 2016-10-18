// variable to keep track of the last time we received data
// a time value will be sent back with the response in a unix timestamp format
var lastupdate = 0;
var ipadd = "http://"+document.location.hostname +":8000/notif";
var n = 0;
// call getData when the document has loaded
$(document).ready(function(){
    getData(lastupdate);
});
// execute ajax call to server.py
var getData = function(lastupdate) {
    $.ajax({
        type: "GET",
        // set the destination for the query
        url: ipadd,
        // define JSONP because we're using a different port and/or domain
        dataType: 'jsonp',
        // needs to be set to true to avoid browser loading icons
        async: true,
        cache: false,
        // timeout after 5 minutes
        timeout:300000,
        // process a successful response
        success: function(response) {
            // append the message list with the new message
            var messages = response.data.messages;
	    function increaseNumber(){
     		n = n+1;
    		document.getElementById('number').innerHTML=n;
                zeroNumber();
		}
            function decreaseNumber(){
     		n = n-1;
    		document.getElementById('number').innerHTML=n;
                zeroNumber();
                $('<b>Vu</b>').prependTo('#messages');
		}
            function zeroNumber(){                                
		if(document.getElementById('number').innerHTML==0){
			document.getElementById('box').style.display="none";
      	        }else{
			document.getElementById('box').style.display="block";
                }}
            for (x in messages) {
                var a = messages[x].f;
		var b = messages[x].tp;
                var c = messages[x].ts;
                var d = messages[x].id;
                if (a != 0){
                increaseNumber();
                if(d == "Red"){

                $('<li class="list-group-item list-group-item-danger"><a  class="list-group-item list-group-item-danger" onclick="decreaseNumber()">'+a+'Mhz : '+b+' at '+c+'</a></li>').prependTo('#messages');}
                if(d == "Green"){
                $('<li class="list-group-item list-group-item-success"><a  class="list-group-item list-group-item-success" onclick="decreaseNumber()" >'+a+'Mhz : '+b+' at '+c+'</a></li>').prependTo('#messages');
            }
            }
               else{
                //nothing !!
               
               }
              
       }
            // call again in 1 second
            setTimeout('getData('+lastupdate+');', 1000);
        },
        // handle error
        error: function(XMLHttpRequest, textStatus, errorThrown){
            // try again in 10 seconds if there was a request error
            setTimeout('getData('+lastupdate+');', 10000);
        },
    });
};
