from django.db import models
from users.models import User
from venues.models import VenueBookings
from datetime import datetime
# Create your models here.


class UserGames(models.Model):
    host_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    booking_id = models.ForeignKey(VenueBookings, on_delete=models.CASCADE, related_name='booking')
    game_name = models.CharField(max_length=100, default=f"{host_user_id.name}'s game")
    max_players = models.IntegerField()
    joined_players = models.IntegerField(default=1)
    SKILL_CHOICES = [
        ('beginner', 'beginner'),
        ('amateur', 'amateur'),
        ('intermediate', 'intermediate'),
        ('advanced', 'advanced'),
        ('professional', 'professional')
    ]
    min_skill = models.CharField(max_length=20, choices=SKILL_CHOICES, null=True, blank=True)
    max_skill = models.CharField(max_length=20, choices=SKILL_CHOICES, null=True, blank=True)
    description = models.TextField()
    expired = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.id} - {self.host_user_id.player_username} - {self.booking_id}'
    
    
class GameUsers(models.Model):
    game_id = models.ForeignKey(UserGames, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('requested', 'requested'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
        ('removed', 'removed'),
        ('left', 'left')
    ]
    game_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='requested')
    date_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['game_id', 'user_id']
    
    def __str__(self):
        return f'{self.user_id.player_username}'
    
    
class GameChat(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    game_id = models.ForeignKey(UserGames, on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user_id} - {self.message}'
    