window.onload = function () {
    const ctx = document.getElementById('myChart');
    var dataSet = [12,30,21];
    var dataSet2 = [10,20,30];
    const myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dataSet2,
            datasets: [{
                label: 'Temperature',
                data: dataSet,
                backgroundColor: [
                    '#def6c4',

                ],
                borderColor: [

                    '#def6c4'
                ],
                borderWidth: 1,
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks:{
                        color: '#def6c4',
                    }
                },
                x:{
                    beginAtZero: true,
                    ticks:{
                        color: '#def6c4',
                    }
                }
            },
            plugins: {
                
                legend: {
                    display: true,
                    labels: {
                        color: '#91a180',
                        // This more specific font property overrides the global property
                        font: {
                            size: 20,
                            
                        }
                    }
                }
            }
            
            
        }
    });

    var updateInterval = 1000;

    function updateChart(count){

        count = count || 1;


        var count =0;
        var num1=0;
        var num2=0;
        for(count=0;count<1;count++)
        {
            num1 = num2 +  Math.round((Math.random() * (22.5  - 10.24 + 1)) + 10.24)
            num2 = num1 +  Math.round((Math.random() * (26.5  - 10.24 + 1)) + 10.24)

            //console.log(num1);
            //console.log(num2);

            myChart.data.datasets[0].data.push(num1);
            myChart.data.labels.push(num2);
            myChart.update();
            
        }    
        //console.log(dataSet);
        //console.log(dataSet2);

        if (dataSet.length && dataSet2.length > count) {
            dataSet.shift();
            dataSet2.shift();
        }
    }
    updateChart(10);
    setInterval(function(){updateChart()}, updateInterval);    
}
        
    