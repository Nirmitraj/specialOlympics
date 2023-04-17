from django.db import models
from django.contrib.auth.models import User

class Usermetadata(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=20, unique=True)