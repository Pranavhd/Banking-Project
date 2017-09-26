from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Employee(models.model):
    None


class Individual(Profile):
    None


class Merchant(Profile):
    None
