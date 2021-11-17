from django.db import models

# Create your models here.
from django.db import models

class User(models.Model):
    user_name = models.CharField(max_length=10)
    user_password = models.CharField(max_length=20)
    