from django.urls import include, path

urlpatterns = [
    path(
        "auth/",
        include(("apps.accounts.api.v1.urls", "accounts"), namespace="accounts"),
    ),
    path("core/", include(("apps.core.api.v1.urls", "core"), namespace="core")),
]
