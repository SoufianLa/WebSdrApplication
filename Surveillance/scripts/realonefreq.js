var lastupdate = 0;
a = -39; 
var ipadd = "http://"+document.location.hostname +":8000/rtof";
$(document).ready(function(){
    getData(lastupdate);
});
var getData = function(lastupdate) {
    $.ajax({
        type: "GET",
        url: ipadd,
        dataType: 'jsonp',
        async: true,
        cache: false,
        timeout:300000,
        success: function(response) {
            var messages = response.data.messages;
            for (x in messages) {
                a = messages[x].value;}
            setTimeout('getData('+lastupdate+');', 1000);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            setTimeout('getData('+lastupdate+');', 10000);
        },
    });
};
$(function () {
            $(document).ready(function () {
                Highcharts.setOptions({
                    global: {
                        useUTC: false
                    }
                });

        $('#container').highcharts({
            chart: {
                zoomType: 'xy',
                type: 'spline',
                
                marginRight: 10,

                events: {
                    load: function () {
                        var series = this.series[0];
                        setInterval(function () {
                            var x = (new Date()).getTime(),
                                y = a;
                            series.addPoint([x, y], true, true);
                        }, 2000);
                    }
                }
            
            },

            title: {
                text: ''
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis:{
            min: -48, max: 0,

            lineColor: '#FF0000',
            lineWidth: 1,
            title: {
                text: 'Values (DB)'

        },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                        Highcharts.numberFormat(this.y, 2);
                }
            },
            legend: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            series: [{
                animation: false,
                name: 'mesures',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -10; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 1000,
                            y: a
                        });
                    }
                    return data;
                }())
            }]
        });
    });
});
