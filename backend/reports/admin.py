from django.contrib import admin
from reports.models import Report, Rating, Sale

# Register your models here.
admin.site.register(Report)
admin.site.register(Rating)
admin.site.register(Sale)