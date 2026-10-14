from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Report(models.Model):
    class TypeChoice(models.TextChoices):
        INDIAN='IN', "Indian"
        CHINESE='CH', "Chinese"
        ITALIAN="IT"
        GREEK="GK"
        MEXICAN="MX"
    name = models.CharField(max_length=200)
    description = models.TextField()
    website = models.URLField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(default=0)
    longtitude = models.FloatField(default=0)
    report_type=models.CharField(max_length=2, choices=TypeChoice.choices, default="")

    def __str__(self):
        return self.name

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField

    def __str__(self):
        return f"Rating: {self.Rating}"

class Sale(models.Model):
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True)
    income = models.DecimalField(max_digits=8,decimal_places=2)
    datetime = models.DateTimeField()