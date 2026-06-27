from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.projects.models import Project, ProjectMembership, ProjectRole


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "key", "description", "lead"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return (
            Project.objects.filter(
                Q(memberships__user=self.request.user) | Q(lead=self.request.user),
                is_archived=False,
            )
            .annotate(issue_count=Count("issues"))
            .distinct()
        )


class DashboardView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/dashboard.html"
    context_object_name = "projects"

    def get_queryset(self):
        return (
            Project.objects.filter(
                Q(memberships__user=self.request.user) | Q(lead=self.request.user),
                is_archived=False,
            )
            .annotate(issue_count=Count("issues"))
            .distinct()[:6]
        )

    def get_context_data(self, **kwargs):
        from apps.issues.models import Issue

        ctx = super().get_context_data(**kwargs)
        ctx["my_issues"] = (
            Issue.objects.filter(assignee=self.request.user)
            .select_related("project", "status", "priority")
            .order_by("-updated_at")[:10]
        )
        ctx["recent_issues"] = (
            Issue.objects.filter(
                Q(project__memberships__user=self.request.user)
                | Q(project__lead=self.request.user)
            )
            .select_related("project", "status", "priority", "assignee")
            .distinct()
            .order_by("-updated_at")[:10]
        )
        return ctx


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"
    slug_field = "key"
    slug_url_kwarg = "key"

    def get_context_data(self, **kwargs):
        from apps.issues.models import Issue, IssueStatus

        ctx = super().get_context_data(**kwargs)
        ctx["issues"] = (
            Issue.objects.filter(project=self.object)
            .select_related("status", "priority", "issue_type", "assignee", "reporter")
            .order_by("-updated_at")
        )
        ctx["statuses"] = IssueStatus.objects.filter(
            models.Q(project=self.object) | models.Q(project__isnull=True)
        )
        ctx["members"] = self.object.memberships.select_related("user", "user__profile")
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        ProjectMembership.objects.create(
            project=self.object,
            user=self.request.user,
            role=ProjectRole.ADMIN,
        )
        if not self.object.lead:
            self.object.lead = self.request.user
            self.object.save(update_fields=["lead"])
        return response

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"key": self.object.key})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"
    slug_field = "key"
    slug_url_kwarg = "key"

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"key": self.object.key})
