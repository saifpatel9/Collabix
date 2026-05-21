from django.urls import include, path

urlpatterns = [
    path("v1/", include(("apps.core.api.v1.urls", "core"), namespace="v1")),
]
