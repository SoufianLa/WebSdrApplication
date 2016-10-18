//variable to keep track of the last time we received data
// a time value will be sent back with the response in a unix timestamp format
var lastupdate = 0;
// call getData when the document has loaded
$(document).ready(function(){
    getData(lastupdate);
});
// execute ajax call to server.py
var getData = function(lastupdate) {
    $.ajax({
        type: "GET",
        // set the destination for the query
        url: 'http://localhost:8900',
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
            $('<li>'+response.status+'</li>').appendTo('#messages');
            for (x in messages) {
                $('<li>'+messages[x].published+' - '+messages[x].message+'</li>').appendTo('#messages');
            }

            // set lastupdate
            lastupdate = response.timestamp;
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