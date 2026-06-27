from django.urls import path

from apps.projects import views

app_name = "projects"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("projects/", views.ProjectListView.as_view(), name="list"),
    path("projects/new/", views.ProjectCreateView.as_view(), name="create"),
    path("projects/<str:key>/", views.ProjectDetailView.as_view(), name="detail"),
    path("projects/<str:key>/edit/", views.ProjectUpdateView.as_view(), name="edit"),
]
