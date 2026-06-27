import pytest
from apps.issues.models import Issue
from apps.projects.models import Project
from django.contrib.auth.models import User
from django.core.management import call_command


@pytest.mark.django_db
def test_seed_kira_is_idempotent():
    call_command("seed_kira")
    call_command("seed_kira")

    assert User.objects.filter(username="admin").exists()
    assert Project.objects.filter(key="KIRA").exists()
    assert Issue.objects.filter(project__key="KIRA").count() >= 4
