from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    is_client = models.BooleanField(default=True)
    is_staff_member = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return self.username