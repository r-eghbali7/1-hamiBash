from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
import uuid

from account.throttles import FollowRateThrottle
from .serializers import *
from .tasks import send_otp_to_phone, generate_otp
from .redis_service import OTPService
from .models import CustomUser
from .utils.mongo_service import follows_collection


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


# User registration view
class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()
            otp_service = OTPService()
            otp_code = generate_otp()
            otp_service.save_otp(user.mobile_number, otp_code)
            send_otp_to_phone.delay(user.mobile_number, otp_code)
            otp_service.increment_otp_attempts(user.mobile_number)
            return Response({"message": "کاربر ثبت شد. کد OTP به شماره موبایل ارسال شد."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OTP verification view
class OTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data['mobile_number']
            otp_service = OTPService()
            attempts = otp_service.get_otp_attempts(mobile_number)
            if attempts >= 5:
                return Response({"error": "حداکثر تعداد تلاش برای ارسال OTP در یک ساعت به پایان رسیده است."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            try:
                user = CustomUser.objects.get(mobile_number=mobile_number)
                if not user.is_active:
                    otp_code = generate_otp()
                    otp_service.save_otp(mobile_number, otp_code)
                    send_otp_to_phone.delay(mobile_number, otp_code)
                    otp_service.increment_otp_attempts(mobile_number)
                    return Response({"message": "کد OTP به شماره موبایل ارسال شد."}, status=status.HTTP_200_OK)
                return Response({"error": "کاربر قبلاً فعال شده است."}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Verify OTP view
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data['mobile_number']
            otp_code = serializer.validated_data['otp_code']
            otp_service = OTPService()
            if otp_service.verify_otp(mobile_number, otp_code):
                try:
                    user = CustomUser.objects.get(mobile_number=mobile_number)
                    user.is_active = True
                    user.is_email_verified = True
                    user.save()
                    return Response({"message": "کد OTP تأیید شد. کاربر فعال شد."}, status=status.HTTP_200_OK)
                except CustomUser.DoesNotExist:
                    return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "کد OTP نامعتبر یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update user level view
class UpdateUserLevelView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        new_level = request.data.get('user_level')
        if new_level not in dict(CustomUser.USER_LEVELS).keys():
            return Response({"error": "سطح کاربری نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(mobile_number=mobile_number)
            user.user_level = new_level
            user.save()
            return Response({"message": f"سطح کاربری به {new_level} تغییر کرد."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

# User panel view
class UserPanelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        follow_data = follows_collection.find_one({"user_id": str(user.id)}, {"_id": 0})
        followers_count = len(follow_data.get("followers", [])) if follow_data else 0
        following_count = len(follow_data.get("following", [])) if follow_data else 0

        data = {
            'email': user.email,
            'full_name': user.full_name,
            'mobile_number': user.mobile_number,
            'user_level': user.user_level,
            'is_email_verified': user.is_email_verified,
            'followers_count': followers_count,
            'following_count': following_count
        }
        return Response(data, status=status.HTTP_200_OK)

# Login view
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user and user.is_active:
                login(request, user)
                return Response({
                    'user': {
                        'email': user.email,
                        'full_name': user.full_name,
                        'mobile_number': user.mobile_number
                    },
                    'message': 'ورود با موفقیت انجام شد.'
                }, status=status.HTTP_200_OK)
            return Response({"error": "ایمیل یا رمز عبور اشتباه است یا حساب غیرفعال است."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Forgot password view
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data['mobile_number']
            otp_service = OTPService()
            attempts = otp_service.get_otp_attempts(mobile_number)
            if attempts >= 5:
                return Response({"error": "حداکثر تعداد تلاش برای ارسال OTP در یک ساعت به پایان رسیده است."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            try:
                user = CustomUser.objects.get(mobile_number=mobile_number)
                otp_code = generate_otp()
                otp_service.save_otp(mobile_number, otp_code)
                send_otp_to_phone.delay(mobile_number, otp_code)
                otp_service.increment_otp_attempts(mobile_number)
                return Response({"message": "کد OTP برای بازنشانی رمز عبور ارسال شد."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Reset password view
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data['mobile_number']
            otp_code = serializer.validated_data['otp_code']
            new_password = serializer.validated_data['new_password']
            otp_service = OTPService()
            if otp_service.verify_otp(mobile_number, otp_code):
                try:
                    user = CustomUser.objects.get(mobile_number=mobile_number)
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "رمز عبور با موفقیت بازنشانی شد."}, status=status.HTTP_200_OK)
                except CustomUser.DoesNotExist:
                    return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "کد OTP نامعتبر یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Change password view
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            form = PasswordChangeForm(user=user, data=serializer.validated_data)
            if form.is_valid():
                form.save()
                return Response({"message": "رمز عبور با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)
            return Response({"error": form.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Follow user view
class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [FollowRateThrottle]

    def post(self, request, user_id):
        me = str(request.user.id)
        target = str(user_id)

        if not is_valid_uuid(target):
            return Response({"error": "شناسه نامعتبر است."}, status=400)

        if me == target:
            return Response({"error": "نمی‌توانید خودتان را فالو کنید."}, status=400)

        if not CustomUser.objects.filter(id=target).exists():
            return Response({"error": "کاربر یافت نشد."}, status=404)

        # بررسی بلاک شدن (اختیاری)
        block_doc = follows_collection.find_one({"user_id": target}, {"blocked": 1})
        if block_doc and me in block_doc.get("blocked", []):
            return Response({"error": "شما اجازه فالو این کاربر را ندارید."}, status=403)

        # بررسی فالو بودن قبلی
        already = follows_collection.find_one({"user_id": me, "following": target})
        if already:
            return Response({"message": "قبلاً این کاربر را فالو کرده‌اید."}, status=200)

        follows_collection.update_one(
            {"user_id": me},
            {"$addToSet": {"following": target}},
            upsert=True
        )
        follows_collection.update_one(
            {"user_id": target},
            {"$addToSet": {"followers": me}},
            upsert=True
        )

        return Response({"message": "کاربر با موفقیت فالو شد."}, status=200)

# Unfollow user view
class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        me = str(request.user.id)
        target = str(user_id)

        follows_collection.update_one(
            {"user_id": me},
            {"$pull": {"following": target}}
        )
        follows_collection.update_one(
            {"user_id": target},
            {"$pull": {"followers": me}}
        )

        return Response({"message": "کاربر آنفالو شد."}, status=200)
    
# User follow list view
class UserFollowListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        doc = follows_collection.find_one({"user_id": str(user_id)}, {"_id": 0})
        if not doc:
            return Response({"followers": [], "following": []})

        return Response({
            "followers": doc.get("followers", []),
            "following": doc.get("following", [])
        })