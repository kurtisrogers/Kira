from apps.core.extensions import registry
from django.conf import settings


def kira_globals(request):
    return {
        "kira_nav_items": registry.get_data("nav_items"),
        "kira_dashboard_widgets": registry.get_data("dashboard_widgets"),
        "DEBUG": settings.DEBUG,
    }
