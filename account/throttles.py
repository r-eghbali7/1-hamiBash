from rest_framework.throttling import UserRateThrottle

class FollowRateThrottle(UserRateThrottle):
    scope = 'follow'