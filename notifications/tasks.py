from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

@shared_task
def send_notification_task(user_id, message):
    try:
        user = User.objects.get(id=user_id)
        Notification.objects.create(user=user, message=message)
    except User.DoesNotExist:
        # اگر کاربر حذف شده بود یا پیدا نشد، خطا نده
        pass