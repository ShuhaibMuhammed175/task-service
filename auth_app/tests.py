from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.core.cache import cache
from .models import EmailOTP

User = get_user_model()


class BaseTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()


# 1️⃣ Register View
class RegisterTest(BaseTest):

    @patch("auth_app.tasks.send_email_task.delay")
    def test_register(self, mock_email):
        url = reverse("register")
        data = {
            "username": "test",
            "email": "test@example.com",
            "password": "pass1234",
            "password2": "pass1234",
        }

        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 201)
        mock_email.assert_called_once()


# 2️⃣ Login (OTP sent)
class LoginOTPTest(BaseTest):

    @patch("auth_app.otp_handler.cache.set")
    @patch("auth_app.otp_handler.send_email_task.delay")
    def test_login_send_otp(self, mock_email, mock_cache):
        User.objects.create_user(
            username="user",
            email="test@example.com",
            password="pass1234",
            is_active=True
        )

        url = reverse("login")
        data = {"email": "test@example.com", "password": "pass1234"}

        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)
        mock_email.assert_called_once()
        mock_cache.assert_called_once()


# 3️⃣ Verify Registration OTP
class VerifyRegisterOTPTest(BaseTest):

    def test_verify_register_otp(self):
        user = User.objects.create_user(
            username="uuu",
            email="t@t.com",
            password="aaa",
            is_active=False
        )
        EmailOTP.objects.create(user=user, otp="123456")

        url = reverse("verify-otp")
        data = {"email": "t@t.com", "otp": "123456"}

        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 202)


# 4️⃣ Resend OTP
class ResendOTPTest(BaseTest):

    @patch("auth_app.tasks.send_email_task.delay")
    def test_resend_otp(self, mock_email):
        user = User.objects.create_user(
            username="test",
            email="test@example.com",
            password="123"
        )
        EmailOTP.objects.create(user=user, otp="123456")

        url = reverse("resend-otp")
        res = self.client.post(url, {"email": "test@example.com"})

        self.assertEqual(res.status_code, 201)
        mock_email.assert_called_once()


# 5️⃣ Forgot Password
class ForgotPasswordTest(BaseTest):

    @patch("auth_app.tasks.send_email_task.delay")
    def test_forgot_password(self, mock_email):
        User.objects.create_user(
            username="aa",
            email="user@example.com",
            password="123"
        )

        url = reverse("forgot-password")
        res = self.client.post(url, {"email": "user@example.com"})

        self.assertEqual(res.status_code, 200)
        mock_email.assert_called_once()


# 6️⃣ Reset Password
class ResetPasswordTest(BaseTest):

    def test_reset_password_invalid(self):
        url = reverse("reset-password", args=["invalid", "token"])
        res = self.client.post(url, {"new_password": "a", "confirm_password": "a"})
        self.assertEqual(res.status_code, 400)


# 7️⃣ Change Password
class ChangePasswordTest(BaseTest):

    def test_change_password(self):
        user = User.objects.create_user(
            username="uu",
            email="u@u.com",
            password="oldpass"
        )

        self.client.force_authenticate(user=user)

        url = reverse("change-password")
        data = {
            "old_password": "oldpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }

        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)


# 8️⃣ User Task Fetch
class UserTasksTest(BaseTest):

    @patch("auth_app.views.requests.get")
    def test_fetch_tasks(self, mock_get):
        user = User.objects.create_user(
            username="uu",
            email="u@u.com",
            password="123"
        )

        self.client.force_authenticate(user=user)

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": 1, "title": "Task"}]

        url = reverse("user-task")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
