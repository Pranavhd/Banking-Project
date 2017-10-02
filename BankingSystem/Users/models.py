from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Individual(Profile):
    None


class Merchant(Profile):
    None


# Internal Users
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField()  # Admin=0, Tier1Employee=1, Tier2Employee=2
