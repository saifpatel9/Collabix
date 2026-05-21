from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(("config.api_v1_urls", "api"), namespace="v1")),
    path("auth/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("", include(("apps.employees.urls", "employees"), namespace="employees")),
    path("", include(("apps.dashboard.urls", "dashboard"), namespace="dashboard")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
