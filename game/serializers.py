from .models import GameUsers, UserGames, GameChat
from rest_framework import serializers
from users.serializers import UserSerializer
from venues.serializers import VenueBookingsSerializer
from venues.models import User
from venues.models import VenueBookings, Venues

class GameUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'player_username', 'profile_img', 'skill_level']
        
class GameVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venues
        fields = '__all__'
        
class GameBookingsSerializer(serializers.ModelSerializer):
    venue = GameVenueSerializer(source='venue_id', read_only=True)
    class Meta:
        model = VenueBookings
        fields = ['id', 'venue_id', 'user_id', 'court', 'date', 'time', 'duration', 'booking_status', 'created_at', 'venue']
        
        
class GameJoinedUsers(serializers.ModelSerializer):
    user = GameUserSerializer(source='user_id', read_only=True)
    
    class Meta:
        model = GameUsers
        fields = '__all__'
        

class GamesSerializer(serializers.ModelSerializer):
    user = GameUserSerializer(source='host_user_id', read_only=True)
    booking = GameBookingsSerializer(source='booking_id', read_only=True)
    joined_users = GameJoinedUsers(many=True, read_only=True, source='gameusers_set')
    
    class Meta:
        model = UserGames
        fields = '__all__'
        
        
class ChatSerializer(serializers.ModelSerializer):
    user = GameUserSerializer(source='user_id', read_only=True)

    class Meta:
        model = GameChat
        fields = '__all__'