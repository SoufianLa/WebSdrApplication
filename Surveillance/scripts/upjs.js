//variable to keep track of the last time we received data
// a time value will be sent back with the response in a unix timestamp format

var lastupdate = 0;
var ipadd = "http://"+document.location.hostname +":8000/";
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
        crossDomain: true,
        // timeout after 5 minutes
        timeout:300000,
        // process a successful response
        success: function(response) {
            // append the message list with the new message
            var messages = response.data.messages;
            for (x in messages) {
                var a = messages[x].freq;
                var b = messages[x].vale;
            }
            window.onload = function () {

        //initial value of dataPoints 
        var dps = []; 
        for (var j = 0; j < a.length; j++) {                 
                            dps.push({
                                x: a[j],
                                y: b[j]
                            });  
                        }; 
        var chart = new CanvasJS.Chart("chartContainer",{ 
                        zoomEnabled: true,

                        axisX: {                        
                        title: "Frequencies (MHz)"
                        },
                        axisY: {                        
                        title: "Value (DB)"
                        //suffix: "DB"
                        },          
            title: {
                text: "measurement "      
            },
                                            
            data: [
            {
                type: "spline", 
                bevelEnabled: true,             
                indexLabel: "",
                dataPoints: dps                 
            }
            ]
        });

        var updateInterval = 100;  

        var updateChart = function () {

            for (var i = 0; i < dps.length; i++) {
                
                // generating random variation deltaY
                //var deltaY = Math.round(2 + Math.random() *(-2-2));             
                var yVal = dps[i].y;
                
                var boilerColor;


                // color of dataPoint dependent upon y value. 

                boilerColor =
                yVal < -44 ? "#FF6000":
                yVal >= -10 ? "#6B8E23":
                yVal > 0 ? "#FF2500":                           
                null;


                // updating the dataPoint
                for (x in messages) {
                //$('<li>'+messages[x].vale+' ***** '+messages[x].freq+'</li>').appendTo('#messages');
                var a = messages[x].freq;
                var b = messages[x].vale;
            

                dps[i] = {x: a[i] , y: b[i], color: boilerColor};}

            };
            
            chart.render();
        };
        for(x in messages){
        updateChart();      

        // update chart after specified interval 
        setInterval(function(){updateChart()}, updateInterval);}
        setTimeout(window.onload, 1000);

        
    }

            // set lastupdate
            
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
