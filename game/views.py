from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import shipmap
from game.models import Game, BoardCell
import json

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password = password)
            if user is not None:
                login(request,user)
                return redirect('/')
            else:
                mes = 'Login failed , check again your username or password'
                mes_tag = 'danger'
                return render(request,'game/login.html',{'mes':mes, 'mes_tag':mes_tag})          
        else:
            return render(request, 'game/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('/')
        else:
            form = UserCreationForm()
        return render(request, 'game/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')


def index_view(request):
    lobbies = Game.objects.filter(is_waiting = True)
    print(lobbies)

    context = {
        'lobbies': lobbies,
    }

    return render(request,'game/index.html',context=context)


def create_game(request):
    if request.method == 'POST':
        userid = request.POST['userid']
        user = User.objects.get(pk=userid)
        game = Game.objects.create(creator=user, current_turn=user)
        game.save()
        return JsonResponse({'gameid':game.id})
    else:
        return JsonResponse({'mes':'failed'})



def game_view(request, gameid):
    game = Game.objects.get(pk=gameid)
    maps = shipmap.maps;
    ships_creator = shipmap.gen_map(maps)
    ships_opponent = shipmap.gen_map(maps)
    board_opponent =[]
    board_creator = []
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user != game.creator and request.user != game.opponent and game.opponent != None:
        return redirect('/')

    if request.user == game.creator:
        if game.map_created == False:
            for i in range(100):
                if i not in ships_creator:
                    cell = BoardCell.objects.get_or_create(game=game,owner=game.creator,status='free',map_index=i)
                    board_creator.append(cell[0])
                else:
                    cell = BoardCell.objects.get_or_create(game=game,owner=game.creator,status='ship_pos',map_index=i)
                    board_creator.append(cell[0])

            for i in range(100):
                if i not in ships_opponent:
                    cell = BoardCell.objects.get_or_create(game=game,owner=game.opponent,status='free',map_index=i)
                    board_opponent.append(cell[0])
                else:
                    cell = BoardCell.objects.get_or_create(game=game,owner=game.opponent,status='ship_pos',map_index=i)
                    board_opponent.append(cell[0])

            game.map_created = True
            game.save()
        else:
            board_creator = BoardCell.objects.filter(game=game, owner=game.creator)
            board_opponent = BoardCell.objects.filter(game=game, owner=game.opponent)
    else:
        if game.opponent==None:
            game.opponent = request.user
            game.save()
            cells = BoardCell.objects.filter(game=game,owner=None)
            for cell in cells:
                cell.owner = game.opponent
                cell.save()
            board_creator = BoardCell.objects.filter(game=game, owner=game.creator)
            board_opponent = BoardCell.objects.filter(game=game, owner=game.opponent)
        else:
            board_creator = BoardCell.objects.filter(game=game, owner=game.creator)
            board_opponent = BoardCell.objects.filter(game=game, owner=game.opponent)
        

    context={
        'game':game,
        'board_creator':board_creator,
        'board_opponent':board_opponent,
    }
    return  render(request,'game/game.html',context=context)

def play_game(request):
    if request.method == 'POST':
        cell_owner = request.POST['owner']
        cell_map_index =request.POST['index']
        game = request.POST['game']
        cell = BoardCell.objects.get(owner=cell_owner, map_index = cell_map_index, game = game)
        if cell.status == 'free':
            cell.status = 'selected'
            cell.save()
        if cell.status =='ship_pos':
            cell.status = 'ship_selected'
            cell.save()
        return JsonResponse({
            'status': 'success',
            'cell_owner':cell_owner,
            'game':game,
            'index': cell_map_index,
            'cell_status':cell.status,
        },status=200)