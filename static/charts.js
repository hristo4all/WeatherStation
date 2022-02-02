window.onload = function () {
        
    var dps = []; // dataPoints
    var dps2 = []; // dataPoints
    var chart = new CanvasJS.Chart("chartContainer", {
        title :{
            text: "Temperature"
        },
        data: [{
            type: "line",
            dataPoints: dps
        }]
    });
    
    var chart2 = new CanvasJS.Chart("chartContainer2", {
        title :{
            text: "Temperature2"
        },
        data: [{
            type: "line",
            dataPoints: dps2
        }]
    });
    var xVal = 0;
    var yVal = 100; 
    var updateInterval = 1000;
    var dataLength = 15; // number of dataPoints visible at any point
    
    var updateChart = function (count) {
    
        count = count || 1;
    
        for (var j = 0; j < count; j++) {
            yVal = yVal +  Math.round(5 + Math.random() *(-5-5));
            dps.push({
                x: xVal,
                y: yVal
            });
            dps2.push({
                x: xVal,
                y: yVal
            });
            xVal++;
        }
    
        if (dps.length > dataLength) {
            dps.shift();
        }
    
        chart.render();
        chart2.render();
    };
    
    updateChart(dataLength);
    setInterval(function(){updateChart()}, updateInterval);
    
    }