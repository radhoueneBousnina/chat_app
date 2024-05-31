from django.contrib.auth.models import AbstractUser
# from django.db import models


# Create your models here.
class User(AbstractUser):
    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username
