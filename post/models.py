import uuid
from django.db import models
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager


User = get_user_model()

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("published", "منتشر شده"),
        ("rejected", "رد شده"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    tags = TaggableManager()  # ← سیستم تگ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    is_published = models.BooleanField(default=True)  # ← در صورت نیاز برای مدیریت نمایش

    def __str__(self):
        return self.title