from apps.core.models import TimeStampedModel
from django.contrib import admin

admin.site.site_header = "Kira Administration"
admin.site.site_title = "Kira Admin"

# Re-export for convenience
__all__ = ["TimeStampedModel"]
