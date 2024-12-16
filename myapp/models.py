
from django.contrib.auth.models import User
from django.db import models

class RewardCode(models.Model):
    code = models.CharField(max_length=20, unique=True) 
    is_used = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    points_required = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.code} - {self.points_required} points"



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    contact_no = models.CharField(max_length=15, blank=True, null=True, unique=True)
    reward_code = models.CharField(max_length=20, blank=True, null=True)
    point_accumulated = models.PositiveIntegerField(default=0)  # New field for points

    def __str__(self):
        return self.user.username
    

