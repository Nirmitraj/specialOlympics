from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    state = models.CharField(max_length=20)
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField()
    state = models.CharField(max_length=100)
# class AuthUser(models.Model):
#     email = models.EmailField(unique=True)
#     is_active = models.BooleanField(default=True)
#     date_joined = models.DateTimeField()
#     state = models.CharField(max_length=100)

