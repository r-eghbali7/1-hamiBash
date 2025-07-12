from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
import re

User = get_user_model()

MOBILE_REGEX = r"^09\d{9}$"
OTP_REGEX = r"^\d{6}$"



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'full_name', 'mobile_number', 'password']
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': True},
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("ایمیل قبلاً ثبت شده است.")
        return value

    def validate_mobile_number(self, value):
        if CustomUser.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("شماره موبایل قبلاً ثبت شده است.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data.get('username', ''),
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            mobile_number=validated_data['mobile_number'],
            password=validated_data['password'],
            user_level='regular'
        )
        return user


class OTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=11)

    def validate_mobile_number(self, value):
        if not re.match(MOBILE_REGEX, value):
            raise serializers.ValidationError("شماره موبایل معتبر نیست.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=11)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        mobile = attrs.get('mobile_number')
        otp = attrs.get('otp_code')

        if not re.match(MOBILE_REGEX, mobile):
            raise serializers.ValidationError({"mobile_number": "شماره موبایل معتبر نیست."})

        if not re.match(OTP_REGEX, otp):
            raise serializers.ValidationError({"otp_code": "کد تایید باید ۶ رقم باشد."})

        real_otp = cache.get(f"otp:{mobile}")
        if real_otp is None:
            raise serializers.ValidationError("کد تأیید منقضی شده یا پیدا نشد.")
        if otp != real_otp:
            raise serializers.ValidationError("کد تأیید اشتباه است.")

        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("ایمیل یا رمز عبور اشتباه است.")
        if not user.is_active:
            raise serializers.ValidationError("حساب کاربری غیرفعال است.")

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=11)

    def validate_mobile_number(self, value):
        if not re.match(MOBILE_REGEX, value):
            raise serializers.ValidationError("شماره موبایل معتبر نیست.")

        if not User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("کاربری با این شماره یافت نشد.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=11)
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        mobile = attrs.get("mobile_number")
        otp = attrs.get("otp_code")
        new_pass = attrs.get("new_password")

        if not re.match(MOBILE_REGEX, mobile):
            raise serializers.ValidationError({"mobile_number": "شماره موبایل معتبر نیست."})

        if not User.objects.filter(mobile_number=mobile).exists():
            raise serializers.ValidationError("کاربری با این شماره وجود ندارد.")

        real_otp = cache.get(f"otp:{mobile}")
        if real_otp is None:
            raise serializers.ValidationError("کد تأیید منقضی شده یا پیدا نشد.")
        if otp != real_otp:
            raise serializers.ValidationError("کد تأیید اشتباه است.")

        if len(new_pass.strip()) < 8:
            raise serializers.ValidationError({"new_password": "رمز عبور جدید باید حداقل ۸ کاراکتر باشد."})

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8)
    new_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        user = self.context.get("request").user
        old = attrs.get("old_password")
        new = attrs.get("new_password")

        if not user.check_password(old):
            raise serializers.ValidationError({"old_password": "رمز عبور فعلی اشتباه است."})

        if old == new:
            raise serializers.ValidationError("رمز عبور جدید نباید با رمز قبلی یکسان باشد.")
        return attrs
