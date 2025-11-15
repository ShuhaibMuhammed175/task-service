from rest_framework.throttling import UserRateThrottle, ScopedRateThrottle

class UserMinThrottle(UserRateThrottle):
             scope = 'user_min'

class UserDayThrottle(UserRateThrottle):
             scope = 'user_day'

class ResendOTPThrottle(UserRateThrottle):
        scope = 'resend_otp'

class ResendOTPThrottleDay(UserRateThrottle):
        scope = 'resend_otp_day'