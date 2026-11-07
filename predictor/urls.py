from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("history/", views.history, name="history"),
    path("meter-reading/", views.meter_reading, name="meter_reading"),
    path("notifications/", views.notifications, name="notifications"),
]
