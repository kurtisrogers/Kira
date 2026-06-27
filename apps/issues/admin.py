from apps.issues.models import (
    Comment,
    Issue,
    IssueActivity,
    IssuePriority,
    IssueStatus,
    IssueType,
    Sprint,
)
from django.contrib import admin


@admin.register(IssueType)
class IssueTypeAdmin(admin.ModelAdmin):
    list_display = ["key", "name", "is_subtask"]


@admin.register(IssueStatus)
class IssueStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "position", "project"]
    list_filter = ["category"]


@admin.register(IssuePriority)
class IssuePriorityAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "color"]


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "is_active", "start_date", "end_date"]


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ["key_display", "summary", "project", "status", "priority", "assignee"]
    list_filter = ["project", "status", "priority", "issue_type"]
    search_fields = ["summary", "description"]
    inlines = [CommentInline]

    def key_display(self, obj):
        return obj.key

    key_display.short_description = "Key"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["issue", "author", "created_at"]


@admin.register(IssueActivity)
class IssueActivityAdmin(admin.ModelAdmin):
    list_display = ["issue", "actor", "action", "created_at"]
    list_filter = ["action"]
