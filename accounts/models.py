from django.contrib.auth.models import AbstractUser
from django.db import models

from patients.models import Geocode


class Role(models.Model):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
    )
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Role(name='{self.name}')>"



class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    primary_geocode = models.ForeignKey(Geocode, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
