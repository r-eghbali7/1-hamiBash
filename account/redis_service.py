import redis
import os

class OTPService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=2,
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )

    def save_otp(self, mobile_number, otp_code):
        """ذخیره OTP با زمان انقضای 5 دقیقه"""
        key = f"otp:{mobile_number}"
        self.redis_client.setex(key, 300, str(otp_code))  # 300 ثانیه = 5 دقیقه

    def verify_otp(self, mobile_number, otp_code):
        """تأیید OTP و حذف آن پس از تأیید"""
        key = f"otp:{mobile_number}"
        stored_otp = self.redis_client.get(key)
        if stored_otp and stored_otp == str(otp_code):
            self.redis_client.delete(key)  # حذف OTP پس از تأیید
            return True
        return False

    def get_otp_attempts(self, mobile_number):
        """شمارش تعداد تلاش‌های ارسال OTP در یک ساعت"""
        key = f"otp_attempts:{mobile_number}"
        return int(self.redis_client.get(key) or 0)

    def increment_otp_attempts(self, mobile_number):
        """افزایش تعداد تلاش‌های OTP با انقضای 1 ساعت"""
        key = f"otp_attempts:{mobile_number}"
        self.redis_client.incr(key)
        self.redis_client.expire(key, 3600)  # انقضای 1 ساعت
