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


class PanerPicture(models.Model):
    picture = models.ImageField(upload_to='paner_pictures/')

    def __str__(self):
        return f'Paner Picture {self.id}'


class Category(models.Model):
    name = models.CharField(max_length=200)
    icon = models.ImageField(upload_to='category_icons/')

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    picture = models.ImageField(upload_to='restaurant_pictures/')
    desc = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=200)
    picture = models.ImageField(upload_to='food_pictures/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    desc = models.CharField(max_length=500)

    def __str__(self):
        return self.name


