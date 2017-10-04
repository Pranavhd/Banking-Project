from django.db import models
from djmoney.models.fields import MoneyField
from BankingSystem.Users.models import Profile


# Create your models here.
class Request(models.Model):
    requester = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name="requester")


class MoneyRequest(Request):
    reciever = models.ForeignKey('Users.Profile', on_delete=None, related_name="reciever")
    transfer_ammount = MoneyField(max_digits=20, decimal_places=2, default_currency='USD')
    direction = (
        ("send", 'Send'),
        ("recieve", 'Recieve'),
    )
