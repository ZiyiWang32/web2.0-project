from django.db import models

# Create your models here.
from django.db import models
from django.http import response

class User(models.Model):
    user_name = models.CharField(max_length=10)
    user_password = models.CharField(max_length=20)
    user_level = models.IntegerField(default=0)
    user_exp = models.IntegerField(default=0)

class Post(models.Model):
    post_id = models.CharField(primary_key=True, unique=True, max_length=50)
    owner_id = models.CharField(max_length=10)
    like_num = models.IntegerField(default=0)
    favorite_num = models.IntegerField(default=0)
    topic_text = models.CharField(max_length=20)
    content_text = models.CharField(max_length=100)
    create_date = models.DateField()
    response_num = models.IntegerField(default=0)

class Response(models.Model):
    r_id = models.CharField(primary_key=True, unique=True, max_length=50)
    owner_id = models.CharField(max_length=10)
    post_id = models.CharField(max_length=50)
    text = models.CharField(max_length=100)
    create_date = models.DateField()
        
class Like(models.Model):
    user_name = models.CharField(max_length=10)
    post_id = models.CharField(max_length=50)
    topic_text = models.CharField(max_length=20)

class Favorite(models.Model):
    topic_text = models.CharField(max_length=20)
    user_name = models.CharField(max_length=10)
    post_id = models.CharField(max_length=50)
    tag = models.CharField(max_length=20)