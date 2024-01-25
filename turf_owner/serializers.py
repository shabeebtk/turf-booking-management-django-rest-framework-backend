from rest_framework import serializers
from .models import Owners
from django.contrib.auth.hashers import make_password

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owners
        fields = ['id', 'owner_name', 'owner_email', 'owner_phone', 'owner_password']
        extra_kwargs = {
            'owner_password' : { 'write_only' : True }
        }
        
    def create(self, validated_data):
        print('working')
        password = validated_data.pop('owner_password', None)
        hashed_password = make_password(password)
        instance = self.Meta.model(**validated_data, owner_password= hashed_password)
        instance.save()
        return instance