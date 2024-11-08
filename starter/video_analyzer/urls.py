from django.urls import path
from . import views

urlpatterns = [
    path("", views.analyze_video, name="analyze"),
]
