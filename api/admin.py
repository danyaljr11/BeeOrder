from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Food)
admin.site.register(PanerPicture)
admin.site.register(Restaurant)
admin.site.register(Order)
