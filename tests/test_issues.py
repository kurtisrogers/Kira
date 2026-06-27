import pytest
from apps.issues.models import Issue, IssueActivity
from apps.issues.services import IssueService
from django.urls import reverse


@pytest.mark.django_db
def test_issue_key_and_auto_numbering(project, issue_type, issue_status, issue_priority, user):
    first = Issue.objects.create(
        project=project,
        summary="First",
        issue_type=issue_type,
        status=issue_status,
        priority=issue_priority,
        reporter=user,
    )
    second = Issue.objects.create(
        project=project,
        summary="Second",
        issue_type=issue_type,
        status=issue_status,
        priority=issue_priority,
        reporter=user,
    )

    assert first.key == "TEST-1"
    assert second.key == "TEST-2"
    assert first.get_absolute_url() == reverse("issues:detail", kwargs={"key": "TEST-1"})


@pytest.mark.django_db
def test_issue_service_update_status(issue, issue_status_done, user):
    IssueService.update_field(issue, "status", str(issue_status_done.pk), user)
    issue.refresh_from_db()

    assert issue.status == issue_status_done
    assert IssueService.get_field_display(issue, "status") == "Done"


@pytest.mark.django_db
def test_issue_service_log_activity(issue, user):
    activity = IssueService.log_activity(
        issue,
        user,
        IssueActivity.Action.CREATED,
        field_name="status",
        old_value="To Do",
        new_value="Done",
    )

    assert activity.issue == issue
    assert activity.actor == user
    assert activity.action == IssueActivity.Action.CREATED


@pytest.mark.django_db
def test_issue_service_rejects_unknown_field(issue, user):
    with pytest.raises(ValueError, match="Unsupported field"):
        IssueService.update_field(issue, "unknown", "x", user)


@pytest.mark.django_db
def test_issue_detail_requires_login(client, issue):
    response = client.get(reverse("issues:detail", kwargs={"key": issue.key}))
    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_issue_detail_authenticated(authenticated_client, issue):
    response = authenticated_client.get(reverse("issues:detail", kwargs={"key": issue.key}))
    assert response.status_code == 200
    assert issue.summary in response.content.decode()


@pytest.mark.django_db
def test_add_comment_via_htmx(authenticated_client, issue, user):
    response = authenticated_client.post(
        reverse("issues:comment", kwargs={"key": issue.key}),
        {"body": "Looks good"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert issue.comments.count() == 1
    assert "Looks good" in response.content.decode()


@pytest.mark.django_db
def test_inline_status_update(authenticated_client, issue, issue_status_done):
    response = authenticated_client.post(
        reverse("issues:inline_update", kwargs={"key": issue.key}),
        {"field": "status", "value": str(issue_status_done.pk)},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    issue.refresh_from_db()
    assert issue.status == issue_status_done
