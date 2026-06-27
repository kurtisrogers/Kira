from apps.issues import views
from django.urls import path

app_name = "issues"

urlpatterns = [
    path(
        "projects/<str:project_key>/issues/new/",
        views.IssueCreateView.as_view(),
        name="create",
    ),
    path("issues/<str:key>/", views.IssueDetailView.as_view(), name="detail"),
    path("issues/<str:key>/edit/", views.IssueUpdateView.as_view(), name="edit"),
    path("issues/<str:key>/comment/", views.AddCommentView.as_view(), name="comment"),
    path(
        "issues/<str:key>/inline-update/",
        views.IssueInlineUpdateView.as_view(),
        name="inline_update",
    ),
    path(
        "projects/<str:project_key>/issues/partial/",
        views.IssueListPartialView.as_view(),
        name="list_partial",
    ),
]
