
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    contact_no = models.CharField(max_length=15, blank=True, null=True, unique=True)
    reward_code = models.CharField(max_length=20, blank=True, null=True)
    point_accumulated = models.PositiveIntegerField(default=0)
    email_verified = models.BooleanField(default=False)
    points_awarded_for_email = models.BooleanField(default=False)  # New field

    def __str__(self):
        return self.user.username



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

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    required_points = models.PositiveIntegerField()       

    def __str__(self):
        return self.name

class SurveyQuestion(models.Model):
    question_text = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.question_text

class SurveyOption(models.Model):
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255) 
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.option_text} (Votes: {self.votes})"


