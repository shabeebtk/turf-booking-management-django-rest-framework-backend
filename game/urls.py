from django.urls import path
from .views import *

urlpatterns = [
    path('create', CreateGame.as_view()),
    path('get_games', getGames.as_view()),
    path('get_user_games', getUserGames.as_view()),
    path('filter', FilterGames.as_view()),
    path('game_details', GameDetails.as_view()),
    path('check_user_game', CheckUserJoinedGame.as_view()),
    path('check_user_all_game', CheckUserJoinedGames.as_view()),
    path('request', RequestGameJoin.as_view()),
    path('accept_request', AcceptJoinRequest.as_view()),
    path('reject_request', RejectJoinRequest.as_view()),
    path('remove_user', RemoveJoinedUser.as_view()),
    path('left_game', LeftGame.as_view()),
    path('get_user_hosted_games', getHostUserGames.as_view()),
    path('get_user_joined_games', getJoinedUserGames.as_view()),
    path('get_game_requests', getGameRequests.as_view()),
    path('game_chats', GetChatMessages.as_view())
]
