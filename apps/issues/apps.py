from django.apps import AppConfig


class IssuesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.issues"
    label = "issues"

    def ready(self):
        from apps.core.extensions import registry

        registry.register(
            "issue_types",
            {"key": "task", "name": "Task", "icon": "check-square", "color": "#3B82F6"},
            key="task",
            priority=10,
        )
        registry.register(
            "issue_types",
            {"key": "bug", "name": "Bug", "icon": "bug", "color": "#EF4444"},
            key="bug",
            priority=20,
        )
        registry.register(
            "issue_types",
            {"key": "story", "name": "Story", "icon": "book", "color": "#10B981"},
            key="story",
            priority=30,
        )
        registry.register(
            "issue_types",
            {"key": "epic", "name": "Epic", "icon": "zap", "color": "#8B5CF6"},
            key="epic",
            priority=40,
        )
