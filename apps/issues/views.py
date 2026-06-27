from apps.issues.models import Comment, Issue, IssueActivity, IssuePriority, IssueStatus, IssueType
from apps.issues.services import IssueService
from apps.projects.models import Project
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "summary",
            "description",
            "issue_type",
            "status",
            "priority",
            "assignee",
            "story_points",
            "due_date",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = "issues/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, key=kwargs["project_key"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["project"] = self.project
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["status"].queryset = IssueStatus.objects.filter(
            models.Q(project=self.project) | models.Q(project__isnull=True)
        )
        form.fields["issue_type"].queryset = IssueType.objects.all()
        form.fields["priority"].queryset = IssuePriority.objects.all()
        form.fields["assignee"].queryset = User.objects.filter(
            models.Q(project_memberships__project=self.project) | models.Q(pk=self.request.user.pk)
        ).distinct()
        if not form.instance.pk:
            form.fields["status"].initial = IssueStatus.objects.filter(name="To Do").first()
            form.fields["priority"].initial = IssuePriority.objects.filter(name="Medium").first()
            form.fields["issue_type"].initial = IssueType.objects.filter(key="task").first()
        return form

    def form_valid(self, form):
        form.instance.project = self.project
        form.instance.reporter = self.request.user
        response = super().form_valid(form)
        IssueService.log_activity(self.object, self.request.user, IssueActivity.Action.CREATED)
        return response

    def get_success_url(self):
        return reverse("issues:detail", kwargs={"key": self.object.key})


class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = "issues/detail.html"
    context_object_name = "issue"
    slug_field = "pk"
    slug_url_kwarg = "pk"

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        project_key, _, number = key.partition("-")
        return get_object_or_404(
            Issue.objects.select_related(
                "project", "status", "priority", "issue_type", "assignee", "reporter", "sprint"
            ).prefetch_related(
                "comments__author",
                "comments__author__profile",
                "activities__actor",
            ),
            project__key=project_key,
            number=int(number),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comment_form"] = CommentForm()
        ctx["statuses"] = IssueStatus.objects.filter(
            models.Q(project=self.object.project) | models.Q(project__isnull=True)
        )
        ctx["priorities"] = IssuePriority.objects.all()
        ctx["subtasks"] = self.object.subtasks.select_related("status", "assignee")
        return ctx


class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = "issues/form.html"

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        project_key, _, number = key.partition("-")
        return get_object_or_404(Issue, project__key=project_key, number=int(number))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["project"] = self.object.project
        return ctx

    def get_success_url(self):
        return reverse("issues:detail", kwargs={"key": self.object.key})


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a comment..."})}


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, key):
        issue = _get_issue_by_key(key)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.author = request.user
            comment.save()
            IssueService.log_activity(issue, request.user, IssueActivity.Action.COMMENTED)
            if request.htmx:
                return render(
                    request,
                    "issues/partials/comment.html",
                    {"comment": comment},
                )
        return redirect("issues:detail", key=key)


class IssueInlineUpdateView(LoginRequiredMixin, View):
    """HTMX endpoint for inline field updates on issue detail."""

    ALLOWED_FIELDS = {"status", "priority", "assignee", "summary"}

    def post(self, request, key):
        issue = _get_issue_by_key(key)
        field = request.POST.get("field", "")
        value = request.POST.get("value", "")

        if field not in self.ALLOWED_FIELDS:
            return HttpResponse("Invalid field", status=400)

        old_value = IssueService.get_field_display(issue, field)
        IssueService.update_field(issue, field, value, request.user)
        new_value = IssueService.get_field_display(issue, field)

        action = (
            IssueActivity.Action.STATUS_CHANGED
            if field == "status"
            else IssueActivity.Action.UPDATED
        )
        IssueService.log_activity(
            issue,
            request.user,
            action,
            field_name=field,
            old_value=old_value,
            new_value=new_value,
        )

        if request.htmx:
            template = f"issues/partials/{field}_badge.html"
            ctx = {"issue": issue}
            if field == "status":
                ctx["status"] = issue.status
            elif field == "priority":
                ctx["priority"] = issue.priority
            return render(request, template, ctx)

        return redirect("issues:detail", key=key)


class IssueListPartialView(LoginRequiredMixin, View):
    """HTMX partial for filtering issues in project view."""

    def get(self, request, project_key):
        project = get_object_or_404(Project, key=project_key)
        issues = Issue.objects.filter(project=project).select_related(
            "status", "priority", "issue_type", "assignee"
        )

        status_id = request.GET.get("status")
        if status_id:
            issues = issues.filter(status_id=status_id)

        assignee_id = request.GET.get("assignee")
        if assignee_id:
            issues = issues.filter(assignee_id=assignee_id)

        q = request.GET.get("q", "").strip()
        if q:
            issues = issues.filter(
                models.Q(summary__icontains=q) | models.Q(description__icontains=q)
            )

        return render(
            request,
            "issues/partials/issue_list.html",
            {"issues": issues, "project": project},
        )


def _get_issue_by_key(key: str) -> Issue:
    project_key, _, number = key.partition("-")
    return get_object_or_404(Issue, project__key=project_key, number=int(number))
