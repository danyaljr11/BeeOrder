from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('delivery_guy', 'Delivery Guy'),
        ('restaurant_manager', 'Restaurant Manager'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    otp = models.CharField(max_length=4, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=False, null=False, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=20, null=False, blank=False)


class PanerPicture(models.Model):
    picture = models.ImageField(upload_to='images/paner_pictures/')

    def __str__(self):
        return f'Paner Picture {self.id}'


class Category(models.Model):
    name = models.CharField(max_length=200)
    icon = models.ImageField(upload_to='images/category_icons/')

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    picture = models.ImageField(upload_to='images/restaurant_pictures/')
    desc = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=200)
    picture = models.ImageField(upload_to='images/food_pictures/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    desc = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('on_the_way', 'On the Way'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    delivery_location = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_time = models.DateTimeField()
    items = models.JSONField()  # or use TextField for JSON string if using older Django versions

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class FCMDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registration_id = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=[('android', 'Android'), ('ios', 'iOS')], default='android')

    def __str__(self):
        return f'{self.user} - {self.registration_id}'