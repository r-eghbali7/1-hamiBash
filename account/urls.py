from django.urls import path
from .views import (
    RegisterView, OTPView, VerifyOTPView, UpdateUserLevelView, UserPanelView,
    LoginView, ForgotPasswordView, ResetPasswordView, ChangePasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/', OTPView.as_view(), name='otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('update-user-level/', UpdateUserLevelView.as_view(), name='update-user-level'),
    path('panel/', UserPanelView.as_view(), name='user-panel'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]