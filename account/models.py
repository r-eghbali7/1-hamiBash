from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
import uuid

class CustomUser(AbstractUser):
    USER_LEVELS = (
        ('regular', 'Regular User'),
        ('content_creator', 'Content Creator'),
        ('pending_creator', 'Pending Creator'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    email = models.EmailField(unique=True, validators=[EmailValidator()], verbose_name='ایمیل')
    full_name = models.CharField(
        max_length=100,
        validators=[RegexValidator(regex=r'^[آ-یءئ\s]+$', message="نام کامل باید فقط شامل حروف فارسی و فاصله باشد.")],
        verbose_name='نام کامل'
    )
    mobile_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(regex=r'^09[0-9]{9}$', message="فرمت شماره موبایل اشتباه است.")],
        verbose_name='شماره موبایل'
    )
    user_level = models.CharField(max_length=20, choices=USER_LEVELS, default='regular', verbose_name='سطح کاربری')
    is_email_verified = models.BooleanField(default=False, verbose_name='تایید ایمیل')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email}"