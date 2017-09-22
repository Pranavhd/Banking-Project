from django.db import models
from BankingSystem.Users.models import User


class Request(models.Model):
    originator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="originator")
    referencing = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="referencing", null=True)
    comment = models.TextField()
    status = (
        ("P", "PENDING"),
        ("A", "APPROVED"),
        ("D", "DENIED"),
    )
    statement = models.TextField()
