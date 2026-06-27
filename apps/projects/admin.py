from apps.projects.models import Project, ProjectMembership
from django.contrib import admin


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["key", "name", "lead", "is_archived"]
    search_fields = ["name", "key"]
    inlines = [ProjectMembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "role"]
    list_filter = ["role"]
