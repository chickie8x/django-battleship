window.onload = function(){
    const gameId = document.getElementById('game-id').dataset.gameid
    const gameCreator = document.getElementById('creator-name').textContent
    const gameOpponent = document.getElementById('opponent-name')
    const waitingPlayer = document.getElementById('waiting-player')
    const csrf = document.getElementsByTagName('input')[0].value
    var cells = document.getElementsByClassName('cell-event')
    var current_user = document.getElementById('current-user').dataset.currentid

    // init the websocket connection 
    const gameSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/gameid/'
        +gameId
        + '/'
    );
    
    // listening to events 
    gameSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        // user left the game 
        if (data.message === 'left'){
            alert(data.user + ' was left the game')
        }

        // user connected game
        if(data.message === 'connected'){
            let user = data.user
            let userid=data.userid
            if(user != gameCreator){
                gameOpponent.textContent=user
                waitingPlayer.textContent='Game ready, let\'s play :)'
                let cells = document.getElementsByClassName('cell-event')
                for(i=0;i<cells.length;i++){
                    if(!cells[i].dataset.user){
                        cells[i].dataset.user=userid
                    }
                }
            }
        }

        // player mark a cell , switch player turn
        if(data.message==='marked_cell'){
            var cell_owner = data.cell_owner
            var game = data.game
            var index = data.index
            var current_turn_value = data.current_turn
            var current_turn_set = document.getElementById('set-current-turn')
            current_turn_set.textContent=current_turn_value
            var cells = document.getElementsByClassName('cell-event')
            for(i=0;i<cells.length;i++){
                if(cells[i].dataset.user==cell_owner && cells[i].dataset.game==game && cells[i].dataset.index==index){
                   var current_class = cells[i].classList[1]
                   if(data.cell_status==='selected'){
                       cells[i].classList.remove(current_class)
                       cells[i].classList.add('cell-selected')
                   }
                   if(data.cell_status==='ship_selected'){
                    cells[i].classList.remove(current_class)
                    cells[i].classList.add('ship-selected')
                   }
                }
            }
        }
    };

    // websocket connection closed
    gameSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };


    // add event listener on cells 
    for(i=0;i<cells.length;i++){
        cells[i].addEventListener('click',function(){
            if(this.dataset.user != current_user){
                var data = new FormData()
                data.append('owner',this.dataset.user)
                data.append('game',this.dataset.game)
                data.append('index',this.dataset.index)
                data.append('csrfmiddlewaretoken', csrf)
                fetch('/playgame',{
                    method: 'post',
                    body: data
                }).then((res)=>{
                    return res.json()
                }).then(function(data){
                    var status = data.status
                    if(status==='success'){
                        gameSocket.send(JSON.stringify({
                            'message':'marked_cell',
                            'cell_owner': data.cell_owner,
                            'game':data.game,
                            'index': data.index,
                            'cell_status':data.cell_status,
                            'current_turn':data.current_turn,
                        }))
                    }
                    if(status==='won'){
                        console.log(data)
                    }
                    if(status==='is_done'){
                        window.location.replace('/')
                    }
                })
            }
            else{
                alert('choose a cell of your opponent\'s board')
            }
            
        })
    }

}

