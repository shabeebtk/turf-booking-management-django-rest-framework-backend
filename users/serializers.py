from rest_framework import serializers
from .models import User, RazorPayment
from app_admin.models import UserNotification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'player_username', 'email', 'phone', 'password', 'is_active', 'profile_img', 'skill_level', 'verified']
        extra_kwargs = {
            'password' : {'write_only' : True}
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    
class RazorPaymentSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format="%d %B %Y %I:%M %p")
    
    class Meta:
        model = RazorPayment
        fields = '__all__'
        depth = 2
        
class userNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = '__all__'


    

        