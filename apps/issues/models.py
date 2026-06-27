from apps.core.models import TimeStampedModel
from apps.projects.models import Project
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class IssueType(TimeStampedModel):
    """Configurable issue types — extend by adding rows or registering via extensions."""

    key = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="circle")
    color = models.CharField(max_length=7, default="#6B7280")
    is_subtask = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class IssueStatusCategory(models.TextChoices):
    TODO = "todo", "To Do"
    IN_PROGRESS = "in_progress", "In Progress"
    DONE = "done", "Done"


class IssueStatus(TimeStampedModel):
    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=20, choices=IssueStatusCategory.choices, default=IssueStatusCategory.TODO
    )
    position = models.PositiveIntegerField(default=0)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, related_name="statuses"
    )

    class Meta:
        ordering = ["position", "name"]
        verbose_name_plural = "issue statuses"

    def __str__(self):
        return self.name


class IssuePriority(TimeStampedModel):
    name = models.CharField(max_length=50)
    level = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=50, default="minus")
    color = models.CharField(max_length=7, default="#6B7280")

    class Meta:
        ordering = ["-level"]
        verbose_name_plural = "issue priorities"

    def __str__(self):
        return self.name


class Sprint(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sprints")
    name = models.CharField(max_length=200)
    goal = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.project.key} — {self.name}"


class Issue(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    number = models.PositiveIntegerField()
    issue_type = models.ForeignKey(IssueType, on_delete=models.PROTECT, related_name="issues")
    status = models.ForeignKey(IssueStatus, on_delete=models.PROTECT, related_name="issues")
    priority = models.ForeignKey(IssuePriority, on_delete=models.PROTECT, related_name="issues")
    summary = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues"
    )
    reporter = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="reported_issues"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subtasks"
    )
    sprint = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name="issues"
    )
    story_points = models.PositiveSmallIntegerField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = [("project", "number")]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assignee"]),
        ]

    def __str__(self):
        return f"{self.key}: {self.summary}"

    @property
    def key(self) -> str:
        return f"{self.project.key}-{self.number}"

    def get_absolute_url(self):
        return reverse("issues:detail", kwargs={"key": self.key})

    def save(self, *args, **kwargs):
        if not self.number:
            last = (
                Issue.objects.filter(project=self.project)
                .order_by("-number")
                .values_list("number", flat=True)
                .first()
            )
            self.number = (last or 0) + 1
        super().save(*args, **kwargs)


class Comment(TimeStampedModel):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="issue_comments")
    body = models.TextField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.issue.key} by {self.author.username}"


class IssueActivity(TimeStampedModel):
    """Audit log for issue changes — extensible via signals."""

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        COMMENTED = "commented", "Commented"
        STATUS_CHANGED = "status_changed", "Status changed"
        ASSIGNED = "assigned", "Assigned"

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="activities")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30, choices=Action.choices)
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "issue activities"

    def __str__(self):
        return f"{self.issue.key}: {self.action}"
