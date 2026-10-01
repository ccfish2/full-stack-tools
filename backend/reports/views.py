# backend/reports/views.py
# from rest_framework import viewsets
# from .models import Report
# from .serializers import ReportSerializer

# class ReportViewSet(viewsets.ModelViewSet):
#     queryset = Report.objects.all()
#     serializer_class = ReportSerializer

from django.shortcuts import render

def index(request):
    cities = [
    {"name": "Mumbai", "population": "19,000,000", "country": "India"},
    {"name": "New York", "population": "20,000,000", "country": "USA"},
    {"name": "Calcutta", "population": "15,000,000", "country": "India"},
    {"name": "Chicago", "population": "7,000,000", "country": "USA"},
    {"name": "Tokyo", "population": "33,000,000", "country": "Japan"},
    ]

    context = {'cities': cities}

#     books = [
#     {"title": "1984", "author": {"name": "George", "age": 45}},
#     {"title": "Timequake", "author": {"name": "Kurt", "age": 75}},
#     {"title": "Alice", "author": {"name": "Lewis", "age": 33}},
# ]
#     context = {'books': books}
    # template_name = "reports/reports.html"
    return render(request, 'reports/reports.html', context)