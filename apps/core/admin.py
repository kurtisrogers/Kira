from django.contrib import admin

from apps.core.models import TimeStampedModel

admin.site.site_header = "Kira Administration"
admin.site.site_title = "Kira Admin"

# Re-export for convenience
__all__ = ["TimeStampedModel"]
