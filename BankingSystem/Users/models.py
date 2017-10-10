from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class BankUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 'CUSTOMER', 'MERCHANT', 'ADMIN', 'TIER2', 'TIER1'
    user_type = models.CharField(choices=[], max_length=10)

