from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Individual(Profile):
    phone_number = PhoneNumberField(default='')
    mail_address = models.CharField(max_length=1000,default='NOT_PROVIDED')

class Merchant(Profile):
    None

# Internal Users
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField()  # Admin=0, Tier1Employee=1, Tier2Employee=2
