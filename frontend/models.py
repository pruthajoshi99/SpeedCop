from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    location = models.TextField(max_length = 50)

class State(models.Model):
    name = models.TextField(max_length = 30)
    code = models.TextField(primary_key = True)

class City(models.Model):
    name = models.TextField(max_length = 30)
    code = models.IntegerField(primary_key = True)
    state = models.ForeignKey(State, on_delete = models.CASCADE) 
