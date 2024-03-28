from django.contrib import admin
from .models import UserGames, GameUsers, GameChat
# Register your models here.


admin.site.register(UserGames)
admin.site.register(GameUsers)
admin.site.register(GameChat)