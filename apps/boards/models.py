from django.db import models

from apps.core.models import TimeStampedModel
from apps.issues.models import IssueStatus
from apps.projects.models import Project


class Board(TimeStampedModel):
    class BoardType(models.TextChoices):
        KANBAN = "kanban", "Kanban"
        SCRUM = "scrum", "Scrum"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="boards")
    name = models.CharField(max_length=200)
    board_type = models.CharField(
        max_length=20, choices=BoardType.choices, default=BoardType.KANBAN
    )
    filter_query = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.project.key} — {self.name}"

    def get_columns(self):
        """Return board columns — statuses for this project or global defaults."""
        return IssueStatus.objects.filter(
            models.Q(project=self.project) | models.Q(project__isnull=True)
        ).order_by("position")


class BoardColumn(TimeStampedModel):
    """Optional custom column mapping — for future swimlane/column customization."""

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")
    status = models.ForeignKey(IssueStatus, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    wip_limit = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["position"]
        unique_together = [("board", "status")]

    def __str__(self):
        return f"{self.board.name}: {self.status.name}"
