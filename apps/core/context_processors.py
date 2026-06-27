from django.conf import settings

from apps.core.extensions import registry


def kira_globals(request):
    return {
        "kira_nav_items": registry.get_data("nav_items"),
        "kira_dashboard_widgets": registry.get_data("dashboard_widgets"),
        "DEBUG": settings.DEBUG,
    }
