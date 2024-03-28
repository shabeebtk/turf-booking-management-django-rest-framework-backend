from django.contrib import admin
from .models import User, Otp, RazorPayment, FCMToken
from app_admin.models import UserNotification


# Register your models here.

admin.site.register(User)
admin.site.register(Otp)
admin.site.register(RazorPayment)
admin.site.register(UserNotification)
admin.site.register(FCMToken)
