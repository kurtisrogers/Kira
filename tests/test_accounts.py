import pytest
from apps.accounts.models import Profile
from django.urls import reverse


@pytest.mark.django_db
def test_profile_initials_from_display_name(user):
    profile = Profile.objects.get(user=user)
    profile.display_name = "Ada Lovelace"
    assert profile.initials == "AL"


@pytest.mark.django_db
def test_profile_initials_from_username(user):
    profile = Profile.objects.get(user=user)
    profile.display_name = ""
    user.first_name = ""
    user.last_name = ""
    assert profile.initials == "TE"


@pytest.mark.django_db
def test_signup_creates_profile(client):
    response = client.post(
        reverse("accounts:signup"),
        {
            "username": "newbie",
            "email": "new@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
        },
    )

    assert response.status_code == 302
    assert Profile.objects.filter(user__username="newbie").exists()


@pytest.mark.django_db
def test_login_redirects_to_dashboard(client, user):
    response = client.post(
        reverse("accounts:login"),
        {"username": "tester", "password": "pass1234"},
    )
    assert response.status_code == 302
    assert response.url == reverse("projects:dashboard")
