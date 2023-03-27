from datetime import datetime

from django.db import models

from user.models import UserModel


class Card(models.Model):
    """
    Model for board card

    """
    NEW = "New"
    IN_PROGRES = "In_progress"
    IN_QA = "In_QA"
    READY = "Ready"
    DONE = "Done"
    STATUS_CHOICES = [
        (NEW, "New"),
        (IN_PROGRES, "In progress"),
        (IN_QA, "In QA"),
        (READY, "Ready"),
        (DONE, "Done"),
    ]

    description: str = models.CharField(max_length=255)
    status: str = models.CharField(max_length=15, choices=STATUS_CHOICES, default=NEW)
    creator: str = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    executor: str = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created: datetime = models.DateField(auto_now_add=True)
    updated: datetime = models.DateField(auto_now=True)
    is_deleted: bool = models.BooleanField(default=False)

