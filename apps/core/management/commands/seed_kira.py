from apps.accounts.models import Profile
from apps.boards.models import Board
from apps.issues.models import Issue, IssuePriority, IssueStatus, IssueType
from apps.projects.models import Project, ProjectMembership, ProjectRole
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed demo data for Kira"

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@kira.local", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin")
            admin.save()
        Profile.objects.get_or_create(user=admin)

        demo, _ = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@kira.local", "first_name": "Demo", "last_name": "User"},
        )
        if _:
            demo.set_password("demo")
            demo.save()
        Profile.objects.get_or_create(user=demo, defaults={"display_name": "Demo User"})

        for _key, name, level in [
            ("highest", "Highest", 5),
            ("high", "High", 4),
            ("medium", "Medium", 3),
            ("low", "Low", 2),
            ("lowest", "Lowest", 1),
        ]:
            IssuePriority.objects.get_or_create(name=name, defaults={"level": level})

        for key, name, icon, color in [
            ("task", "Task", "check", "#3B82F6"),
            ("bug", "Bug", "bug", "#EF4444"),
            ("story", "Story", "book", "#10B981"),
            ("epic", "Epic", "zap", "#8B5CF6"),
        ]:
            IssueType.objects.get_or_create(
                key=key, defaults={"name": name, "icon": icon, "color": color}
            )

        for name, category, pos in [
            ("Backlog", "todo", 0),
            ("To Do", "todo", 1),
            ("In Progress", "in_progress", 2),
            ("In Review", "in_progress", 3),
            ("Done", "done", 4),
        ]:
            IssueStatus.objects.get_or_create(
                name=name, project=None, defaults={"category": category, "position": pos}
            )

        project, _ = Project.objects.get_or_create(
            key="KIRA",
            defaults={
                "name": "Kira Platform",
                "description": "Core platform development",
                "lead": admin,
            },
        )
        ProjectMembership.objects.get_or_create(
            project=project, user=admin, defaults={"role": ProjectRole.ADMIN}
        )
        ProjectMembership.objects.get_or_create(
            project=project, user=demo, defaults={"role": ProjectRole.MEMBER}
        )

        Board.objects.get_or_create(project=project, defaults={"name": "KIRA Board"})

        todo = IssueStatus.objects.get(name="To Do")
        in_progress = IssueStatus.objects.get(name="In Progress")
        done = IssueStatus.objects.get(name="Done")
        medium = IssuePriority.objects.get(name="Medium")
        high = IssuePriority.objects.get(name="High")
        task = IssueType.objects.get(key="task")
        bug = IssueType.objects.get(key="bug")
        story = IssueType.objects.get(key="story")

        samples = [
            ("Set up extension registry", task, todo, medium, admin),
            ("Build Kanban board view", story, in_progress, high, demo),
            ("Fix login redirect loop", bug, todo, high, None),
            ("Write plugin documentation", task, done, medium, admin),
        ]

        for summary, itype, status, priority, assignee in samples:
            if not Issue.objects.filter(project=project, summary=summary).exists():
                Issue.objects.create(
                    project=project,
                    summary=summary,
                    issue_type=itype,
                    status=status,
                    priority=priority,
                    assignee=assignee,
                    reporter=admin,
                    description=f"Demo issue: {summary}",
                )

        self.stdout.write(
            self.style.SUCCESS("Seed data created. Login: admin / admin or demo / demo")
        )
