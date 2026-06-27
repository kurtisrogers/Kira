"""Issue business logic — keeps views thin and extensible."""

from __future__ import annotations

from django.contrib.auth.models import User

from apps.issues.models import Issue, IssueActivity, IssuePriority, IssueStatus


class IssueService:
    @staticmethod
    def update_field(issue: Issue, field: str, value: str, actor: User) -> Issue:
        if field == "status":
            issue.status = IssueStatus.objects.get(pk=int(value))
        elif field == "priority":
            issue.priority = IssuePriority.objects.get(pk=int(value))
        elif field == "assignee":
            issue.assignee = User.objects.get(pk=int(value)) if value else None
        elif field == "summary":
            issue.summary = value
        else:
            raise ValueError(f"Unsupported field: {field}")
        issue.save(update_fields=[field, "updated_at"])
        return issue

    @staticmethod
    def get_field_display(issue: Issue, field: str) -> str:
        if field == "status":
            return issue.status.name
        if field == "priority":
            return issue.priority.name
        if field == "assignee":
            return issue.assignee.username if issue.assignee else ""
        if field == "summary":
            return issue.summary
        return ""

    @staticmethod
    def log_activity(
        issue: Issue,
        actor: User | None,
        action: str,
        *,
        field_name: str = "",
        old_value: str = "",
        new_value: str = "",
    ) -> IssueActivity:
        return IssueActivity.objects.create(
            issue=issue,
            actor=actor,
            action=action,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
        )
