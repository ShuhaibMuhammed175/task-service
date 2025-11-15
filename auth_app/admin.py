from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailOTP

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email',)

admin.site.register(User, CustomUserAdmin)

class CustomEmailOTPAdmin(admin.ModelAdmin):
    model = EmailOTP
    list_display = ('user', 'otp', 'attempts', 'created_at')
    
admin.site.register(EmailOTP, CustomEmailOTPAdmin)
