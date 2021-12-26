from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Game(models.Model):
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='creator')
    opponent = models.ForeignKey(User, null= True, on_delete=models.DO_NOTHING, related_name='player')
    winner = models.ForeignKey(User, null= True, on_delete=models.DO_NOTHING, related_name='winner')
    current_turn = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    map_created = models.BooleanField(default=False)
    is_waiting = models.BooleanField(default=True)
    is_done = models.BooleanField(default=False)


class BoardCell(models.Model):
    CELL_STATUS = (
        ('free','free'),
        ('selected','selected'),
        ('ship_pos','ship_pos'),
        ('ship_selected','ship_selected')
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    status = models.CharField(choices=CELL_STATUS, max_length=25, default='free')
    map_index = models.IntegerField()


class Scores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
        