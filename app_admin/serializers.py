from rest_framework import serializers
from users.models import User

class AdminSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'password']
        extra_kwargs = {
            'password' : {'write_only' : True}
        }


class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_venues = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    