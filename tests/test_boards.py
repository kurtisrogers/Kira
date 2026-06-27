import pytest
from apps.boards.models import Board
from django.urls import reverse


@pytest.mark.django_db
def test_board_detail_groups_issues_by_status(authenticated_client, board, issue):
    response = authenticated_client.get(reverse("boards:detail", kwargs={"board_id": board.pk}))
    assert response.status_code == 200
    assert issue.key in response.content.decode()


@pytest.mark.django_db
def test_move_issue_changes_status(authenticated_client, board, issue, issue_status_done):
    response = authenticated_client.post(
        reverse("boards:move", kwargs={"board_id": board.pk}),
        {"issue_id": issue.pk, "status_id": issue_status_done.pk},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 204
    assert response.headers.get("HX-Refresh") == "true"
    issue.refresh_from_db()
    assert issue.status == issue_status_done


@pytest.mark.django_db
def test_project_board_creates_default_board(authenticated_client, project):
    response = authenticated_client.get(
        reverse("boards:project_board", kwargs={"project_key": project.key})
    )
    assert response.status_code == 302
    assert Board.objects.filter(project=project).exists()
