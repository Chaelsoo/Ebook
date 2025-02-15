from django.contrib import admin

# Register your models here.
from .models import UserProfile, Review
from  django.contrib.auth.admin import UserAdmin

# Register User with default UserAdmin
admin.site.register(UserProfile)
admin.site.register(Review)

