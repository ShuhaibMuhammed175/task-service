import random
from django.core.cache import cache
from .tasks import send_email_task

class OTPHandler:
    @staticmethod
    def generate_otp(identifier, expiration=60):
        """
        Generates a 6-digit OTP, stores it in Redis with an expiration, and returns the OTP.
        
        Args:
            identifier (str): A unique identifier for the user (e.g., email or phone number).
            expiration (int): The OTP expiration time in seconds. Defaults to 180 (3 minutes).
        
        Returns:
            str: The generated OTP.
        """
        otp = str(random.randint(100000, 999999))
        cache.set(identifier, otp, timeout=expiration)
        
        subject = "OTP For Login"
        content = f"Your OTP for login is: {otp}\nThis OTP is valid for 5 minutes."
        send_email_task.delay(subject, content, user_email=[identifier])

        return otp
    
    @staticmethod
    def verify_otp(identifier, otp):
        stored_otp = cache.get(identifier)
        if stored_otp and stored_otp == otp:
            cache.delete(identifier)
            return True
        return False