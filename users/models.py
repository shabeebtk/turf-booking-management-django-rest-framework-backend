from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.fields import CharField
from .constant import PaymentStatus
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, phone, password, **extra_fields)

class User(AbstractUser):
    player_username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.BigIntegerField(unique=True) 
    password = models.CharField(max_length=100)
    profile_img = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    verified = models.BooleanField(default=False)
    username = None
    SKILL_CHOICES = [
        ('beginner', 'beginner'),
        ('amateur', 'amateur'),
        ('intermediate', 'intermediate'),
        ('advanced', 'advanced'),
        ('professional', 'professional')
    ]
    skill_level = models.CharField(max_length=50, choices=SKILL_CHOICES, default='beginner')
    
    REGISTRATION_CHOICES = [
        ('email', 'Email'),
        ('google', 'Google')
    ]
    registration_method = models.CharField(max_length=10, choices=REGISTRATION_CHOICES, default='email')
    google_user_id = models.CharField(max_length=255, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'player_username']
    
    objects = CustomUserManager()
    
    
class Otp(models.Model):
    OTP_CHOICES = [
        ('email', 'email'),
        ('phone', 'phone'),
    ]
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_type = models.CharField(max_length=50, choices=OTP_CHOICES)
    email = models.EmailField(max_length=100, default='abc@gmail.com', blank=True, null=True)
    otp = models.CharField(max_length=10)
    
    
class RazorPayment(models.Model):
    order_product = models.CharField(max_length=100)
    order_amount = models.CharField(max_length=25)
    order_payment_id = models.CharField(max_length=100)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_product
    
class FCMToken(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=250)
    
    def __str__(self):
        return f"{self.user_id.email}'s FCM Token"
