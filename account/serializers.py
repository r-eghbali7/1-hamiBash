from rest_framework import serializers
from .models import CustomUser

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

class VerifyOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=11)
    otp_code = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

class ForgotPasswordSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=11)

class ResetPasswordSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=11)
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8)
    new_password = serializers.CharField(min_length=8)