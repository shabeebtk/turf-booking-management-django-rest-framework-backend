from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GameUsers, UserGames, GameChat
from venues.models import VenueBookings
from users.authenticate import check_user_jwt
from .constant import SKILL_VALUE, REQUESTED, ACCEPTED, REJECTED, REMOVED, LEFT
from venues.constant import ACCEPTED
from users.models import User
from .serializers import GamesSerializer, GameJoinedUsers, ChatSerializer
from django.utils import timezone
from .utils import current_indian_date, current_indian_time, check_game_expired
from django.db.models import Q
from datetime import datetime, timedelta
from .notification import send_notification
from backend.settings import FIRBASE_SERVER_KEY
from users.models import FCMToken


# Create your views here.

class CreateGame(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        print(token)
        user = check_user_jwt(token)
        
        game_name = request.data.get('game_name', None)        
        booking_id = request.data['booking_id']
        max_players = request.data['max_players']
        min_skill = request.data.get('min_skill', None)
        max_skill = request.data.get('max_skill', None)
        description = request.data['description']
        
        booking = VenueBookings.objects.get(id=booking_id)
        if booking and booking.booking_status == ACCEPTED:  
            if UserGames.objects.filter(booking_id=booking).exists():
                return Response('failed to create game', status=status.HTTP_409_CONFLICT)
            
            print(booking.user_id, '==', user.id)
            if booking.user_id.id != user.id:
                 return Response('failed to create game', status=status.HTTP_401_UNAUTHORIZED)
             
            game = UserGames.objects.create(host_user_id=user,
                                            booking_id=booking,
                                            game_name=game_name,
                                            max_players=max_players,
                                            min_skill=min_skill,
                                            max_skill=max_skill,
                                            description=description)
            game.save()
            return Response('game created successfully')
        else:
            return Response('failed to create game', status=status.HTTP_400_BAD_REQUEST)
        
        
class getGames(APIView):
    def get(self, request):
        time = current_indian_time()
        date = current_indian_date()

        all_games = UserGames.objects.filter(expired=False, booking_id__date__gte=date).exclude(booking_id__date=date, booking_id__time__lte=time)
        serializer = GamesSerializer(all_games, many=True)
        print(all_games)
        return Response(serializer.data)
            
            
class getUserGames(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')
        print(token)
        user = check_user_jwt(token)
        
        time = current_indian_time()
        date = current_indian_date()
        print(date)
        all_games = UserGames.objects.exclude(
            Q(host_user_id=user) | Q(expired=True) | Q(booking_id__date__lt=date) | Q(booking_id__date=date, booking_id__time__lte=time)
        )
        print(all_games)
            
        serializer = GamesSerializer(all_games, many=True)
        return Response(serializer.data)
    
    
class FilterGames(APIView):
    def post(self, request):
        print(request.data)
        selected_court = request.data.get('court', None)
        selected_dates = request.data.get('dates', None)
        user_id = request.data.get('user', None)
        
        print(selected_court, selected_dates, user_id)
        selected_dates = [datetime.strptime(date, '%Y/%m/%d').date() for date in selected_dates]
        formatted_dates = [date.strftime('%Y-%m-%d') for date in selected_dates]
        
        time = current_indian_time()
        date = current_indian_date()
        filter_conditions = Q()
        if selected_court:
            filter_conditions |= Q(booking_id__court__in=selected_court)
        if selected_dates:
            filter_conditions |= Q(booking_id__date__in=formatted_dates)
            
        filter_games = UserGames.objects.filter(filter_conditions, expired=False, booking_id__date__gte=date)
        
        if (user_id):
            user = User.objects.get(id=user_id)
            filter_games = filter_games.exclude(host_user_id=user)
            
        print(filter_games, 'after usr')
        
        serializer = GamesSerializer(filter_games, many=True)
        return Response(serializer.data)
    
class GameDetails(APIView):
    def post(self, request):
            game_id = request.data['game_id']
            game = UserGames.objects.get(id=game_id)
            time = current_indian_time()
            date = current_indian_date()
            
            print(type(game.booking_id.time), 'date', type(time))
            if game.booking_id.date < date or game.booking_id.date == date and game.booking_id.time < time:
                game.expired = True
                game.save()
            
            serializer = GamesSerializer(game)
            return Response(serializer.data)
            # return Response({'error': 'failed to get game'}, status=status.HTTP_400_BAD_REQUEST)
        
class CheckUserJoinedGame(APIView):
    def post(self, request):
        user_id = request.data['user_id']
        game_id = request.data['game_id']
        
        user = User.objects.get(id=user_id)
        game = UserGames.objects.get(id=game_id)
        
        game_user = GameUsers.objects.filter(user_id=user, game_id=game).first()
        serializer = GameJoinedUsers(game_user)
        return Response(serializer.data)
    
class CheckUserJoinedGames(APIView):
    def post(self, request):
        user_id = request.data['user_id']
        user = User.objects.get(id=user_id)        
        game_user = GameUsers.objects.filter(user_id=user)
        
        print(game_user, '---------------------')
        serializer = GameJoinedUsers(game_user, many=True)
        return Response(serializer.data)
            
class RequestGameJoin(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        game_id = request.data['game_id']
        game = UserGames.objects.get(id=game_id)
                
        if game and not check_game_expired(game):
            if game.joined_players < game.max_players and SKILL_VALUE[user.skill_level] >= SKILL_VALUE[game.min_skill] and SKILL_VALUE[user.skill_level] <= SKILL_VALUE[game.max_skill]:
                add_user = GameUsers.objects.create(game_id=game, user_id=user)
                add_user.save()
                
                # send notification 
                send_notification(game.host_user_id.id, 'new game request', f'{user.player_username} requested for your game to join')     
                return Response('game requested successfully')
            else:
                return Response({'error' : "can't sent request to this game"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        return Response({'error' : "failed to request game"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class getHostUserGames(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        games = UserGames.objects.filter(host_user_id=user).order_by('id')
        serializer = GamesSerializer(games, many=True)
        return Response(serializer.data)
    
class getJoinedUserGames(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        games = UserGames.objects.filter(gameusers__user_id=user).order_by('id')
        serializer = GamesSerializer(games, many=True)
        return Response(serializer.data)
    
    
class getGameRequests(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        game_id = request.data['game_id']
        
        game = UserGames.objects.get(id=game_id)
        if game.host_user_id.id == user.id:
            requested_users = GameUsers.objects.filter(game_id=game, game_status=REQUESTED)
            serializer = GameJoinedUsers(requested_users, many=True)
            return Response(serializer.data)
        else:
            return Response({'error':'authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)

    
class AcceptJoinRequest(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        game_id = request.data['game_id']
        requested_user = request.data['requested_user']
        
        game = UserGames.objects.get(id=game_id)
        print(requested_user)
        requested_user = User.objects.get(id=requested_user)
        
        
        requested_users = GameUsers.objects.get(game_id=game, user_id=requested_user, game_status=REQUESTED)
        
        if user.id == game.host_user_id.id:
            requested_users.game_status = ACCEPTED
            game.joined_players += 1
            requested_users.save()
            game.save()
            return Response('requested user accepted')
        else:
            return Response({'error':"operation failed"}, status=status.HTTP_401_UNAUTHORIZED)
      
class RejectJoinRequest(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        try:
            game_id = request.data['game_id']
            requested_user = request.data['requested_user']
            
            game = UserGames.objects.get(id=game_id)
            requested_user = User.objects.get(id=requested_user)
            
            requested_user = GameUsers.objects.get(game_id=game, user_id=requested_user, game_status=REQUESTED)
            
            if user.id == game.host_user_id.id:
                requested_user.game_status = REJECTED
                requested_user.save()
                return Response('requested user rejected')
            else:
                return Response({'error':"operation failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error':"an error occured"}, status=status.HTTP_400_BAD_REQUEST)
            
            
class RemoveJoinedUser(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        try:
            game_id = request.data['game_id']
            removing_user = request.data['requested_user']
            
            game = UserGames.objects.get(id=game_id)
            removing_user = User.objects.get(id=removing_user)
            
            removing_user = GameUsers.objects.get(game_id=game, user_id=removing_user, game_status=ACCEPTED)
            
            if user.id == game.host_user_id.id:
                removing_user.game_status = REMOVED
                game.joined_players -= 1
                removing_user.save()
                game.save()
                return Response('user removed')
            else:
                return Response({'error':"operation failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error':"an error occured"}, status=status.HTTP_400_BAD_REQUEST)
        
class LeftGame(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        try:
            game_id = request.data['game_id']
                        
            game = UserGames.objects.get(id=game_id)            
            left_user = GameUsers.objects.get(game_id=game, user_id=user, game_status=ACCEPTED)
            
            if left_user:
                left_user.game_status = LEFT
                game.joined_players -= 1
                left_user.save()
                game.save()
                return Response('user left')
            else:
                return Response({'error':"operation failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error':"an error occured"}, status=status.HTTP_400_BAD_REQUEST)
        
        
# game chat 
class GetChatMessages(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        game_id = request.data['game_id']
        chats = GameChat.objects.filter(game_id=game_id)
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)
        
        

  
            
                
            
        