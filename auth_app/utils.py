from rest_framework.throttling import UserRateThrottle

class OTPRequestThrottle(UserRateThrottle):
    rate = '3/hour'