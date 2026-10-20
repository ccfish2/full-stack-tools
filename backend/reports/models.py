from django.db import models
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils import timezone
from django_lifecycle import (
    LifecycleModel,
    hook,
    BEFORE_CREATE,
    BEFORE_UPDATE,
    AFTER_UPDATE,
)

from django_lifecycle.conditions import (
    WhenFieldHasChanged,
    WhenFieldValueWas,
    WhenFieldValueIs,
)

class Organization(LifecycleModel):
    class Employers(models.TextChoices):
        GG="Google",
        AI="Anthropic",
        PLTR="Palantir Technology Inc",
        TSLA="Tesla Inc",
        SPAX="SpaceX"
    name = models.CharField(max_length=100, choices=Employers, default=Employers.GG)

class Report(LifecycleModel):
    class TypeChoice(models.TextChoices):
        INDIAN='IN', "Indian"
        CHINESE='CH', "Chinese"
        ITALIAN="IT"
        GREEK="GK"
        MEXICAN="MX"
    class StatusChoice(models.TextChoices):
        Pending="PENDING"
        ACTIVE="ACTIVE"
        SUSPEND="SUSPEND"
        BLOCKED="BLOCKED"

    name = models.CharField(max_length=200)
    description = models.TextField()
    website = models.URLField(default="")
    owner_email = models.EmailField(default="x@example.com")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True,blank=True)
    employer = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)

    latitude = models.FloatField(default=0)
    longtitude = models.FloatField(default=0)
    status=models.CharField(max_length=10, choices=StatusChoice, default="")
    status_changed_at=models.DateTimeField(null=True,blank=True)

    report_type=models.CharField(max_length=5, choices=TypeChoice, default="")
    type_changed_at=models.DateTimeField(null=True,blank=True)
    
    def __str__(self):
        return self.name
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orig_description = self.description
        self._orig_status = self.status

    @hook(
        BEFORE_UPDATE, 
        condition=WhenFieldHasChanged('description', has_changed=True),
    )
    def on_description_change(self):
        self.updated_at = timezone.now()

    @hook(
        AFTER_UPDATE, 
        condition=(
            WhenFieldValueWas("status", value="BLOCKED")
            & WhenFieldValueIs("status", value="ACTIVE")
        )
    )
    def on_publish(self):
        send_email("report description", self.owner_email, "A report has published!")

    @hook(
        BEFORE_UPDATE, 
        condition=WhenFieldHasChanged('status', has_changed=True),
    )
    def on_status_change(self):
        self.status_changed_at = timezone.now()

    @hook(
        BEFORE_CREATE, 
        condition=WhenFieldHasChanged('type', has_changed=True),
    )
    def on_type_change(self):
        self.type_changed_at = timezone.now()

    @hook(AFTER_UPDATE, condition=WhenFieldHasChanged("employer", has_changed=True))
    def notify_user_of_employer_change(self):
        send_email("Update", self.owner_email, "You now work for someone else!")

    def save(self, *args, **kwargs):
        if self.pk is not None and self.description != self._orig_description:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        if self.status != self._orig_status:
            send_email("report description", self.owner_email, "A report has published!")


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

def send_email(subject, from_email, message):
   
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, ["admin@example.com"])
        except ValueError:
            return HttpResponse("Invalid header found.")
        return HttpResponseRedirect("/contact/thanks/")
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse("Make sure all fields are entered and valid.")