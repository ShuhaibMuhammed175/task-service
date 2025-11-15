import environ
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from .models import User, UserActivityLog, EmailOTP
from .serializers import (
    RegisterSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer
)
from .tasks import send_email_task
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from . otp_handler import OTPHandler
import requests
from .throttles import UserMinThrottle, UserDayThrottle, ResendOTPThrottle, ResendOTPThrottleDay

import logging

logger = logging.getLogger(__name__)

logger.info("Task created successfully")
logger.error("Something went wrong")


env = environ.Env()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


User = get_user_model()

class LoginWithOTPView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)

        if user:
            OTPHandler.generate_otp(email)
            temp_access_token = AccessToken.for_user(user)
            logger.info("user created successfully")
            return Response({
                "message": "OTP sent successfully. Please verify to log in.",
                "temp_token": str(temp_access_token)
            }, status=status.HTTP_200_OK)
        else:
            logger.error("Invalid Credentials")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAndLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get("otp")
        temp_token_str = request.data.get("temp_token")

        if not otp or not temp_token_str:
            return Response({"error": "OTP and temp_token are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validated_token = JWTAuthentication().get_validated_token(temp_token_str)
            user_id = validated_token["user_id"]
            user = User.objects.get(id=user_id)

            if OTPHandler.verify_otp(user.email, otp):
                serializer = CustomTokenObtainPairSerializer()
                refresh = serializer.get_token(user)
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({"error": "Invalid or expired temporary token"}, status=status.HTTP_400_BAD_REQUEST)
        

        

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            email = serializer.validated_data['email']
            email_otp, _ = EmailOTP.objects.get_or_create(user=user)
            with transaction.atomic():
                otp = email_otp.generate_otp()

            
            email_otp.otp = otp
            email_otp.attempts = 3
            email_otp.save()

            subject = "Account Activation"
            content = f"Your OTP for account activation is: {otp}\nThis OTP is valid for 5 minutes."
            send_email_task.delay(subject, content, user_email=[email])
            logger.info("User registered successfully. OTP sent to email.")
            return Response(
                {"message": "User registered successfully. OTP sent to email."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.save()
            return Response(
                {'Account Activated': 'Account activated successfully'},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    
    # throttle_classes = [
    #       ResendOTPThrottle, ResendOTPThrottleDay
    #  ]
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                email_otp = EmailOTP.objects.select_related('user').get(user__email=email)
            except EmailOTP.DoesNotExist:
               return Response({"error": "No OTP request found for this email."}, status=status.HTTP_404_NOT_FOUND)

            # Check lock
            if email_otp.is_locked():
                return Response({"error": "Too many wrong attempts. Try again later."}, status=status.HTTP_403_FORBIDDEN)

    
            with transaction.atomic():
    
                otp = email_otp.generate_otp()

            
            subject = "Account Activation"
            content = f"Your OTP for account activation is: {otp}\nThis OTP is valid for 5 minutes."
            send_email_task.delay(subject, content, user_email=[email])
            return Response(
                    {"message": "OTP has been resent successfully."},
                    status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ForgotPasswordView(APIView):
    # throttle_classes = [
    #       UserMinThrottle,
    #       UserDayThrottle
    #  ]
    permission_classes = [AllowAny]
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            uid = uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            
            with transaction.atomic():
                UserActivityLog.objects.create(user=user,
                                            action='FORGOT_PASSWORD',
                                            ip_address=ip,
                                            user_agent=user_agent)

            reset_link = f"{env('BASE_URL_FP')}/reset-password/{uid}/{token}"
            send_email_task.delay(subject='Password Reset Request',
                                  content=f'Click this link to reset your password: {reset_link}', user_email=[email])

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uid, token):
        serializer = ResetPasswordSerializer(data=request.data)
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            try:
                uid = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({"error": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                user.set_password(new_password)
                user.last_password_change = timezone.now()
                user.save()

                UserActivityLog.objects.create(
                    user=user,
                    action='RESET_PASSWORD',
                    ip_address=ip,
                    user_agent=user_agent
    )

            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

        if serializer.is_valid():
            with transaction.atomic():
                user = request.user
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.last_password_change = timezone.now()
                user.save()
                UserActivityLog.objects.create(user=user,
                                            action='CHANGE_PASSWORD',
                                            ip_address=ip,
                                            user_agent=user_agent)
            return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extract the user's access token
        access_token = request.auth  # token from Authorization header

        # The URL of your task_service
        task_service_url = "http://host.docker.internal:8002/tasks/"

        # Make the request to task_service
        try:
            response = requests.get(
                task_service_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code == 200:
                return Response({"tasks": response.json()}, status=200)
            else:
                return Response({"error": "Failed to fetch tasks", "details": response.text}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Task service unreachable", "details": str(e)}, status=500)
