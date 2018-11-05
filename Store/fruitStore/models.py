from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class UserInfo(AbstractUser):
    phone = models.CharField(max_length=11)
    gender = models.CharField(max_length=4)
    address = models.CharField(max_length=128)
    roles = models.ManyToManyField(to="Role")

    def __str__(self):
        return self.username


class Role(models.Model):
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField(to="Permission")

    def __str__(self):
        return self.title


class Permission(models.Model):
    title = models.CharField(max_length=32)
    url = models.CharField(max_length=32)

    def __str__(self):
        return self.title





