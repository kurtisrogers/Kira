import pytest
from apps.projects.models import ProjectMembership, ProjectRole
from django.urls import reverse


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("projects:dashboard"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_dashboard_lists_member_projects(authenticated_client, project):
    response = authenticated_client.get(reverse("projects:dashboard"))
    assert response.status_code == 200
    assert project.key in response.content.decode()


@pytest.mark.django_db
def test_create_project_adds_admin_membership(client, user):
    client.login(username="tester", password="pass1234")
    response = client.post(
        reverse("projects:create"),
        {"name": "New App", "key": "NEW", "description": "A project"},
    )

    assert response.status_code == 302
    membership = ProjectMembership.objects.get(project__key="NEW", user=user)
    assert membership.role == ProjectRole.ADMIN


@pytest.mark.django_db
def test_project_detail_shows_issues(authenticated_client, project, issue):
    response = authenticated_client.get(reverse("projects:detail", kwargs={"key": project.key}))
    assert response.status_code == 200
    assert issue.key in response.content.decode()
