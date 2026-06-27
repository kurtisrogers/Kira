from apps.core.models import TimeStampedModel
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class ProjectRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"
    VIEWER = "viewer", "Viewer"


class Project(TimeStampedModel):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    lead = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="led_projects"
    )
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.key} — {self.name}"

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"key": self.key})


class ProjectMembership(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_memberships")
    role = models.CharField(max_length=20, choices=ProjectRole.choices, default=ProjectRole.MEMBER)

    class Meta:
        unique_together = [("project", "user")]
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username} @ {self.project.key} ({self.role})"
