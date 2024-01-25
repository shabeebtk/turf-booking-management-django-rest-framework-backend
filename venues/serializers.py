from .models import Venues, VenueFacilities, VenueImages, VenuePrice, VenueBookings
from rest_framework import serializers
from turf_owner.models import Owners
from users.serializers import UserSerializer


class VenueFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueFacilities
        fields = '__all__'
        
class VenueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImages
        fields = '__all__'

class VenuePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenuePrice
        fields = '__all__'
        
class VenueOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owners
        fields = '__all__'
        extra_kwargs = {
            'owner_password' : {'write_only' : True}
        }
        
        
class VenueSerailizer(serializers.ModelSerializer):
    venue_facilities = VenueFacilitiesSerializer(many=True)
    venue_images = VenueImageSerializer(many=True, read_only=True)
    venue_prices = VenuePriceSerializer(many=True, read_only=True)
    owner_details = VenueOwnerSerializer(source='owner_id', read_only=True)

    class Meta:
        model = Venues
        fields = '__all__'
    
    
class AddVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venues
        fields = '__all__'
        
class CheckVenueSerializer(serializers.ModelSerializer):
    venue_images = VenueImageSerializer(many=True, read_only=True)
    class Meta:
        model = Venues
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImages
        fields = ('image', 'venue_id')
        
        
        
class VenueBookingsSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user_id', read_only=True)
    venue = VenueSerailizer(source='venue_id', read_only=True)
    class Meta:
        model = VenueBookings
        fields = '__all__'
        