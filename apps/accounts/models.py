from django.contrib.auth.models import User
from django.db import models

from apps.core.models import TimeStampedModel


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=150, blank=True)
    avatar_color = models.CharField(max_length=7, default="#4F46E5")

    def __str__(self):
        return self.display_name or self.user.username

    @property
    def initials(self) -> str:
        name = self.display_name or self.user.get_full_name() or self.user.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[:2].upper()
