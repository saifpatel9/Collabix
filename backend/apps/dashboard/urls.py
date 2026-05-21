from django.urls import path

from .views import contact, dashboard_home, landing_home

app_name = "dashboard"

urlpatterns = [
    path("api/contact", contact, name="contact"),
    path("dashboard/", dashboard_home, name="home"),
    path("", landing_home, name="landing"),
]
