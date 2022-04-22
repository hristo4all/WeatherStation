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
function getPrediction(){
    
}