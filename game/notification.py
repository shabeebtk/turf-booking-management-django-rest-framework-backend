import requests
import json
from backend.settings import FIRBASE_SERVER_KEY
from users.models import User, FCMToken

def send(user_fcm_tokens, message_title, message_body):
    fcm_api = FIRBASE_SERVER_KEY    
    url = "https://fcm.googleapis.com/fcm/send"
    
    headers = {
    "Content-Type":"application/json",
    "Authorization": 'key='+fcm_api
    }

    payload = {
        "registration_ids" :user_fcm_tokens,
        "priority" : "high",
        "notification" : {
            "title" : message_title,
            "body" : message_body,
            # "image" : "https://i.ytimg.com/vi/m5WUPHRgdOA/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLDwz-yjKEdwxvKjwMANGk5BedCOXQ",
            # "icon": "https://yt3.ggpht.com/ytc/AKedOLSMvoy4DeAVkMSAuiuaBdIGKC7a5Ib75bKzKO3jHg=s900-c-k-c0x00ffffff-no-rj",
        }
    }
    
    result = requests.post(url,  data=json.dumps(payload), headers=headers)
    print(result.json)
    
    
    
def send_notification(user_id, notification_title, notifiction_body):
    host_user = User.objects.filter(id=user_id).first()
    notification = FCMToken.objects.filter(user_id=host_user).first()
    print(notification, '--------notification------')
    if notification:
        fcm_token = [notification.fcm_token]
        send(fcm_token, notification_title, notifiction_body)
        return
    else:
        return