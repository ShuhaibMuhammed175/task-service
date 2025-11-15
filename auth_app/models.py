from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import random
from datetime import timedelta


class CustomUserManager(BaseUserManager):
    """Custom manager for User model with email as the unique identifier"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# <--------------------------------------------------------------------------------------------------------------------->#


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    last_password_change = models.DateTimeField(
        default=timezone.now, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, null=True, blank=True)
    attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    locked_until = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        otp = str(random.randint(100000, 999999))
        self.otp = otp
        self.created_at = timezone.now()
        self.attempts = 3 
        self.locked_until = None  
        self.save(update_fields=['otp', 'attempts', 'locked_until', 'created_at'])
        return otp

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def reduce_attempt(self):
        self.attempts -= 1
        if self.attempts <= 0:
            self.locked_until = timezone.now() + timedelta(minutes=2)
            self.attempts = 0
        self.save(update_fields=['attempts', 'locked_until'])
            


    def is_locked(self):
        if self.locked_until and timezone.now() > self.locked_until:
            self.attempts = 3
            self.locked_until = None
            self.save(update_fields=['attempts', 'locked_until'])
            return False
        return self.locked_until and self.locked_until > timezone.now()

    def __str__(self):
        return f"{self.user.email} - {self.otp}"


class UserActivityLog(models.Model):
    ACTION_CHOICES = [
        ('FORGOT_PASSWORD', 'Forgot Password Requested'),
        ('RESET_PASSWORD', 'Password Reset Successful'),
        ('CHANGE_PASSWORD', 'Password Changed from Profile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
    


