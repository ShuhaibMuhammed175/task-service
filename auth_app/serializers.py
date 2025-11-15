from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from . models import EmailOTP
from django.utils import timezone

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['last_password_change'] = str(user.last_password_change)
        return token



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user
    

    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value
    

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Wrong current password."})
        
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"new_password2": "New passwords must match."})
        return data
    

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(
        required=True,
        min_length=4,
        max_length=6,
        error_messages={
            "required": "Please enter the OTP.",
            "min_length": "OTP must be at least 4 digits.",
            "max_length": "OTP cannot exceed 6 digits.",
        },
    )

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            email_otp = EmailOTP.objects.select_related('user').get(user__email=email)
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("OTP not found for this email.")
        
        if email_otp.is_locked():
            remaining_time = (email_otp.locked_until - timezone.now()).seconds // 60
            raise serializers.ValidationError(
                f"Too many wrong attempts. Please try again after {remaining_time} minutes."
        )
        
        if email_otp.otp != otp:
            email_otp.reduce_attempt()
            remaining = email_otp.attempts
            if email_otp.is_locked():
                remaining_time = (email_otp.locked_until - timezone.now()).seconds // 60
                raise serializers.ValidationError(
                    
                    "Maximmum aaattempts reached. Please try again after 1 hour."
                )
            raise serializers.ValidationError(f"Invalid OTP. {remaining} attempts")
        
        if email_otp.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")
        
        email_otp.attempts = 3
        email_otp.locked_until = None
        email_otp.save(update_fields=['attempts', 'locked_until'])
        
        
        data['user'] = email_otp.user
        data['email'] = email_otp.user.email
        data['otp'] = email_otp.otp
        return data


class  ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    
    