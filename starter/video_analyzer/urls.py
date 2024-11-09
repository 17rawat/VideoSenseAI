from django.urls import path
from . import views

app_name = "video_analyzer"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("analysis/", views.analysis, name="analysis"),
]
