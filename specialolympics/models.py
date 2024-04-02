from django.db import models

class CustomUser(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField()
    state = models.CharField(max_length=100)

    class Meta:
        db_table = 'authenticate_customuser' 