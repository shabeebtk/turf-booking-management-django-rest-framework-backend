from django.db import models

# Create your models here.

class Owners(models.Model):
    owner_name = models.CharField(max_length=100)
    owner_email = models.EmailField(max_length=100, unique=True, null=False)
    owner_phone = models.BigIntegerField(unique=True)
    owner_password = models.CharField(max_length=100)
    owner_verified = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.owner_email
    
class OwnerOtp(models.Model):
    OTP_CHOICES = [
        ('email', 'email'),
        ('phone', 'phone'),
    ]
    owner_id = models.ForeignKey(Owners, on_delete=models.CASCADE)
    otp_type = models.CharField(max_length=50, choices=OTP_CHOICES)
    otp = models.CharField(max_length=10)
    
    