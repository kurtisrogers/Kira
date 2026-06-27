import pytest
from apps.accounts.models import Profile
from apps.boards.models import Board
from apps.issues.models import Issue, IssuePriority, IssueStatus, IssueType
from apps.projects.models import Project, ProjectMembership, ProjectRole
from django.contrib.auth.models import User


@pytest.fixture
def user(db):
    user = User.objects.create_user(username="tester", password="pass1234")
    Profile.objects.create(user=user, display_name="Test User")
    return user


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="pass1234")


@pytest.fixture
def project(user):
    project = Project.objects.create(key="TEST", name="Test Project", lead=user)
    ProjectMembership.objects.create(project=project, user=user, role=ProjectRole.ADMIN)
    return project


@pytest.fixture
def issue_type(db):
    return IssueType.objects.create(key="task", name="Task")


@pytest.fixture
def issue_status(db):
    return IssueStatus.objects.create(name="To Do", category="todo", position=1)


@pytest.fixture
def issue_status_done(db):
    return IssueStatus.objects.create(name="Done", category="done", position=2)


@pytest.fixture
def issue_priority(db):
    return IssuePriority.objects.create(name="Medium", level=3)


@pytest.fixture
def issue(user, project, issue_type, issue_status, issue_priority):
    return Issue.objects.create(
        project=project,
        summary="Test issue",
        issue_type=issue_type,
        status=issue_status,
        priority=issue_priority,
        reporter=user,
    )


@pytest.fixture
def board(project):
    return Board.objects.create(project=project, name="Test Board")


@pytest.fixture
def authenticated_client(client, user):
    client.login(username="tester", password="pass1234")
    return client
