from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('restaurant_manager', 'Restaurant Manager'),
        ('delivery_guy', 'Delivery Guy'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=4, blank=True, null=True)
