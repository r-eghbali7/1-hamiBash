from django.urls import path
from .views import *

urlpatterns = [
    # User management
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/', OTPView.as_view(), name='otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('update-user-level/', UpdateUserLevelView.as_view(), name='update-user-level'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('panel/', UserPanelView.as_view(), name='user-panel'),
    
    # Follow/Unfollow
    path('follow/<uuid:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<uuid:user_id>/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('user-follow-list/<uuid:user_id>/', UserFollowListView.as_view(), name='follows-list'),
]