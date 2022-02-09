$(document).ready(function() {
    // Use weather namespace.
    namespace = '/Weather';

    var tempData = [];
    var currTemp = null;
    var time = null;
    // Connect to the Socket.IO server.
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    // Event handler for new connections.
    socket.on('connect', function() {
        socket.emit('my_event', {
            data: 'I\'m connected!'
        });
    });

    // Event handler for server sent data.
    socket.on('my_response', function(msg) {
        $('#Temperature').text(msg.T +'C');
        $('#Pressure').text(msg.P +'hPa');
        $('#Humidity').text(msg.H);
        $('#Time').text(msg.S);
        

        
        const today = new Date(msg.S);
        let hour = today.getHours();
        let minutes = today.getMinutes();
        //const d = new Date();
        //et hour = d.getHours();
        //console.log(hour);


        var a = `${hour}.${minutes}`;

        var parsed = parseFloat(a);

        console.log(parsed);


        if(isNaN(msg.S) && msg.T != "Reading..."){
            
            currTemp = parseFloat(msg.T);
            $('#Test').text(currTemp);
            tempData.push({
                x:parsed,
                y:currTemp
            })

        }
        //onsole.log(msg.T);
        //console.log(msg.P);
        //console.log(msg.H);
        //console.log(msg.S);
        //console.log(tempData);
        //currTemp= msg.T;
        
        //tempData.push(currTemp);
        //console.log(tempData);
    });

    var xVal = 0;
    var yVal = 100; 
    var updateInterval = 2000;
    var dataLength = 5; // number of dataPoints visible at any point
    //var dps = [];
    //console.log(dps)

    var chart = new CanvasJS.Chart("chartContainer", {
        title :{
            text: "Temperature"
        },
        data: [{
            type: "line",
            dataPoints: tempData
        }]
    });

    var updateChart = function (count) {

        count = count || 1;

        /*for (var j = 0; j < count; j++) {
            yVal = yVal +  Math.round(5 + Math.random() *(-5-5));
            dps.push({
                x: xVal,
                y: yVal
            });
 
            xVal++;
            console.log(dps)
        }*/
    
        if (tempData.length > dataLength) {
            tempData.shift();
        }
    
        chart.render();
        //chart2.render();
    };
    updateChart(dataLength);
    setInterval(function(){updateChart()}, updateInterval);
    
 

});// end of function onload




function toggleView() {

    var Cardelems = document.querySelectorAll('div.card');
    var Chartelems = document.querySelectorAll('div.chartWrapper');

    if(!check.checked)
    {
        for(var i = 0;i < Cardelems.length; i++)
        {
            Cardelems[i].style.display = 'flex';
        }
        for(var i = 0;i < Chartelems.length; i++)
        {
            Chartelems[i].style.display = 'none';
        }
    }   
    else{
    
        for(var i = 0;i < Cardelems.length; i++)
        {
            Cardelems[i].style.display = 'none';
        }
        for(var i = 0;i < Chartelems.length; i++)
        {
            Chartelems[i].style.display = 'flex';
        }
    }
}