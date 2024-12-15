
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    contact_no = models.CharField(max_length=15, blank=True, null=True , unique=True)
    reward_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
