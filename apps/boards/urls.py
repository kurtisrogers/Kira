from apps.boards import views
from django.urls import path

app_name = "boards"

urlpatterns = [
    path("boards/", views.BoardListView.as_view(), name="list"),
    path("boards/<int:board_id>/", views.BoardDetailView.as_view(), name="detail"),
    path("boards/<int:board_id>/move/", views.MoveIssueView.as_view(), name="move"),
    path(
        "projects/<str:project_key>/board/",
        views.ProjectBoardView.as_view(),
        name="project_board",
    ),
]
