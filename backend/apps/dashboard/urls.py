from django.urls import path

from .views import contact, dashboard_home

app_name = "dashboard"

urlpatterns = [
    path("api/contact", contact, name="contact"),
    path("", dashboard_home, name="home"),
]
