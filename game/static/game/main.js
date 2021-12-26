$(document).ready(function(){

    var csrf = $("input[name=csrfmiddlewaretoken]").val();

    var lobby = document.getElementById('lobby')

    const indexSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/'
    );

    indexSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log(data.gameid)
        var newgame = document.createElement('div')
        newgame.className='lobby-item'
        newgame.textContent='game id : ' + data.gameid
        lobby.appendChild(newgame)
    };
    
    indexSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };





    $('.create-game-btn').click(function(){
        $.ajax({
            url: 'creategame',
            method: 'post',
            data: {
                csrfmiddlewaretoken: csrf,
                'userid':$(this).data("user"),
            },
            success: function(res){
                if(res.gameid !='failed'){
                    indexSocket.send(JSON.stringify({
                        'type_event':'create_game',
                        'gameid':res.gameid,
                    }))
                window.location.replace('gameid/'+res.gameid)
                }
                else{
                    alert('failed to create new game')
                }
                
            }
        })
    })
    
})