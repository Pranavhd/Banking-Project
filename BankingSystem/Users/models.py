from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Employee(models.Model):
    None


class Individual(Profile):
    phone_number = PhoneNumberField(default='')
    mailing_adress = models.CharField(max_length=1000,default='NOT_PROVIDED')

class Merchant(Profile):
    None
