from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', views.LoginWithOTPView.as_view(), name='login'),
    path('verify-login-otp/', views.VerifyOTPAndLoginView.as_view(), name='verify-login-otp'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),    
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:uid>/<str:token>', views.ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('user-task/', views.UserTasksView.as_view(), name='user-task'),
]
