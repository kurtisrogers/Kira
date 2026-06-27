from apps.boards.models import Board
from apps.issues.models import Issue, IssueStatus
from apps.issues.services import IssueService
from apps.projects.models import Project
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView


class BoardListView(LoginRequiredMixin, ListView):
    model = Board
    template_name = "boards/list.html"
    context_object_name = "boards"

    def get_queryset(self):
        return (
            Board.objects.filter(project__memberships__user=self.request.user)
            .select_related("project")
            .distinct()
        )


class BoardDetailView(LoginRequiredMixin, DetailView):
    model = Board
    template_name = "boards/detail.html"
    context_object_name = "board"
    pk_url_kwarg = "board_id"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        columns = self.object.get_columns()
        ctx["columns"] = []
        for status in columns:
            issues = (
                Issue.objects.filter(project=self.object.project, status=status)
                .select_related("priority", "issue_type", "assignee", "assignee__profile")
                .order_by("-updated_at")
            )
            col = {"status": status, "issues": issues}
            ctx["columns"].append(col)
        ctx["all_columns"] = ctx["columns"]
        return ctx


class MoveIssueView(LoginRequiredMixin, View):
    """HTMX endpoint: move issue to a new status column on the board."""

    def post(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        issue_id = request.POST.get("issue_id")
        status_id = request.POST.get("status_id")

        issue = get_object_or_404(Issue, pk=issue_id, project=board.project)
        get_object_or_404(IssueStatus, pk=status_id)

        IssueService.update_field(issue, "status", str(status_id), request.user)

        if request.htmx:
            response = HttpResponse(status=204)
            response["HX-Refresh"] = "true"
            return response

        return redirect("boards:detail", board_id=board_id)


class ProjectBoardView(LoginRequiredMixin, View):
    """Default board view for a project — creates board if none exists."""

    def get(self, request, project_key):
        project = get_object_or_404(Project, key=project_key)
        board, _ = Board.objects.get_or_create(
            project=project,
            defaults={"name": f"{project.key} Board"},
        )
        return redirect("boards:detail", board_id=board.pk)
