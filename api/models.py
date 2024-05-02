from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('delivery_guy', 'Delivery Guy'),
        ('restaurant_manager', 'Restaurant Manager'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    otp = models.CharField(max_length=4, blank=True, null=True)
