from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("", include("apps.projects.urls")),
    path("", include("apps.issues.urls")),
    path("", include("apps.boards.urls")),
]
