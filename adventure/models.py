from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid

class Room(models.Model):
    # id = models.AutoField(primary_key=True)
    id = models.IntegerField(default=0, primary_key=True)
    # room_number = models.IntegerField(default=0)
    title = models.CharField(max_length=50, default="DEFAULT TITLE")
    description = models.CharField(max_length=500, default="DEFAULT DESCRIPTION")
    n_to = models.IntegerField(default=None, null=True)
    s_to = models.IntegerField(default=None, null=True)
    e_to = models.IntegerField(default=None, null=True)
    w_to = models.IntegerField(default=None, null=True)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    def listRooms():
        return [{
                "pk": room.pk,
                "id": room.id,
                "title": room.title,
                "description": room.description,
                "n_to": room.n_to,
                "s_to": room.s_to,
                "e_to": room.e_to,
                "w_to": room.w_to,
                "x": room.x,
                "y": room.y
                } for room in Room.objects.all()
            ]
    # def __repr__(self):
    #     # if self.e_to is not None:
    #     #     return f"({self.x}, {self.y}) -> ({self.e_to.x}, {self.e_to.y})"
    #     return f"n: {self.n_to}, e: {self.e_to}, s: {self.s_to}, w: {self.w_to}"
    def connect_rooms(self, connecting_room, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        reverse_dir = reverse_dirs[direction]
        setattr(self, f"{direction}_to", connecting_room.id)
        setattr(connecting_room, f"{reverse_dir}_to", self.id)
        self.save()
        connecting_room.save()
    def get_room_in_direction(self, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        return getattr(self, f"{direction}_to")
    def playerNames(self, currentPlayerID):
        return [p.user.username for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]
    def playerUUIDs(self, currentPlayerID):
        return [p.uuid for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currentRoom = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    def initialize(self):
        if self.currentRoom == 0:
            self.currentRoom = Room.objects.first().id
            self.save()
    def room(self):
        try:
            return Room.objects.get(id=self.currentRoom)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()





