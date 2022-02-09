
$(document).ready(function() {
    // Use weather namespace.
    namespace = '/Weather';

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
        $('#Temperature').text(msg.T);
        $('#Pressure').text(msg.P);
        $('#Humidity').text(msg.H);
        $('#Time').text(msg.S);
    });



});

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