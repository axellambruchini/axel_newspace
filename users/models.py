from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_client = models.BooleanField(default=True)
    is_staff_member = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username