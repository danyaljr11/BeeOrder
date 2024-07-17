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
    phone = models.CharField(max_length=15, blank=False, null=False, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        return self.full_name


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
    address = models.CharField(max_length=200)
    lat = models.FloatField(max_length=300)
    lot = models.FloatField(max_length=300)
    picture = models.ImageField(upload_to='images/restaurant_pictures/')
    desc = models.CharField(max_length=300)
    manager = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='restaurant')

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
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('canceled', 'Canceled'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('on_the_way', 'On The Way'),
        ('delivered', 'Delivered'),
    )

    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    delivery_guy = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='deliveries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField(max_length=300)
    lot = models.FloatField(max_length=300)
    w_lat = models.FloatField(max_length=300, default=None , null=True, blank=True)
    w_lot = models.FloatField(max_length=300, default=None, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Example field, you can adjust as needed
    date_time = models.DateTimeField()  # Example field, you can adjust as needed
    items = models.JSONField()  # JSON field for storing items

    def __str__(self):
        return f"Order {self.id} by {self.customer.full_name}"


class FCMToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.id} for {self.user.full_name}"

