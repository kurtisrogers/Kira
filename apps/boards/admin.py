from apps.boards.models import Board, BoardColumn
from django.contrib import admin


class BoardColumnInline(admin.TabularInline):
    model = BoardColumn
    extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "board_type"]
    inlines = [BoardColumnInline]


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ["board", "status", "position", "wip_limit"]
